# Stealth actions against monsters spotted while exploring: slipping
# past them unseen, or striking first on the party's terms.

from typing import Any

from backend.core.utils.responses import success_response
from backend.core.utils.validation import require_keys
from backend.core.workflow_steps import WorkflowStep

from .encounter_battle import start_encounter_battle


def _explore_encounter_monsters(manager, error_text: str):
    """The monsters of the active explore encounter, or raise"""
    from backend.models.monster import Monster

    encounter = manager.get_active_encounter()
    if (
        not encounter
        or encounter.get('event') != 'location_explore'
        or not encounter.get('monster_ids')
    ):
        raise Exception(error_text)

    location = manager.get_current_location() or {'name': 'the dungeon', 'description': ''}
    monsters = [
        m
        for m in (Monster.get_monster_by_id(int(mid)) for mid in encounter.get('monster_ids', []))
        if m
    ]
    return location, monsters


def run_sneak_past(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """
    Try to slip past the monsters spotted while exploring.
    The LLM judges success; failure means the monsters notice - battle.
    """
    workflow_name = 'sneak_past'

    from backend.game.dungeon import manager
    from backend.game.dungeon.generator import build_monsters_details, judge_sneak_attempt

    # Step 0 - validate required keys
    step.emit("validate_context")
    require_keys(context, [])

    location, monsters = _explore_encounter_monsters(manager, "There are no monsters to sneak past")
    monster_names = ', '.join(m.name for m in monsters)

    # Step 1 - the referee judges the attempt
    step.emit("judge_sneak")
    attempt = judge_sneak_attempt(location, build_monsters_details(monsters), workflow_name)

    step.emit("resolve_sneak")
    manager.clear_active_encounter()

    if attempt['success']:
        manager.append_dungeon_log(
            f"The party snuck past {monster_names} without being noticed and pressed on."
        )

        # The avoided monsters keep only a vague impression - enough
        # for them to resurface in another group someday
        from backend.game.memory.journal import append_party_journal
        from backend.game.memory.manager import write_memory

        location_name = location.get('name', 'the dungeon')
        for avoided in monsters:
            write_memory(
                avoided.id,
                'avoided',
                f"Sensed someone slip through its territory at {location_name}, "
                f"but never saw them clearly.",
                {'location': location_name},
            )
        append_party_journal(f"Slipped past {monster_names} unseen at {location_name}.")

        return success_response({"success": True, "narration": attempt['narration']})

    # Noticed! The monsters are on them - battle
    step.emit("start_battle")
    battle_snapshot = start_encounter_battle(
        monsters,
        opening_note=f"The party was caught trying to sneak past: {attempt['narration']}",
    )
    manager.append_dungeon_log(
        f"The party tried to sneak past {monster_names} but was noticed - a battle began!"
    )

    return success_response(
        {
            "success": False,
            "narration": attempt['narration'],
            "battle_intro": attempt['narration'],
            "enemy_ids": [m.id for m in monsters],
            "battle_snapshot": battle_snapshot,
        }
    )


def run_surprise_attack(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """Strike first at the monsters spotted while exploring - battle on the party's terms"""
    workflow_name = 'surprise_attack'

    from backend.game.dungeon import manager
    from backend.game.dungeon.generator import build_monsters_details, generate_ambush_intro

    # Step 0 - validate required keys
    step.emit("validate_context")
    require_keys(context, [])

    location, monsters = _explore_encounter_monsters(manager, "There are no monsters to ambush")
    monster_names = ', '.join(m.name for m in monsters)

    # Step 1 - narrate the ambush being sprung
    step.emit("generate_ambush_intro")
    ambush_intro = generate_ambush_intro(location, build_monsters_details(monsters), workflow_name)

    # Step 2 - battle, opened on the party's terms
    step.emit("start_battle")
    manager.clear_active_encounter()
    battle_snapshot = start_encounter_battle(
        monsters,
        opening_note=f"The party sprang a surprise attack - they have the opening moment: {ambush_intro}",
    )
    manager.append_dungeon_log(
        f"The party sprang a surprise attack on {monster_names} - a battle began on their terms!"
    )

    return success_response(
        {
            "battle_intro": ambush_intro,
            "enemy_ids": [m.id for m in monsters],
            "battle_snapshot": battle_snapshot,
        }
    )
