# Returning monster - someone at this location remembers the party.
# The monster comes back CHANGED by its memories; its disposition decides
# whether the moment is a battle, a warm reunion, or a watchful standoff.

from typing import Any, Optional

from backend.core.utils.responses import success_response
from backend.core.workflow_steps import WorkflowStep

from .encounter_battle import start_encounter_battle


def run_returning_monster(
    step: WorkflowStep, location: dict, workflow_name: str
) -> Optional[dict[str, Any]]:
    """
    Play out a remembered monster's return. Returns the workflow response,
    or None when the returning pool emptied since the path was generated
    (e.g. the monster joined the party at a sibling path) - the caller
    degrades invisibly to a plain explore; events are hidden anyway.
    """
    from backend.game.dungeon import manager
    from backend.game.memory import returning

    step.emit("pick_returning_monster")
    remembered = returning.pick_returning_monster()

    if not remembered:
        return None

    # The monster returns CHANGED by what it remembers
    step.emit("transform_returning_monster")
    transformed = returning.transform_returning_monster(remembered, workflow_name)
    disposition = transformed['disposition']
    greeting = transformed['greeting']

    step.emit("reveal_returning_monster")
    returning.stage_reveal(remembered)
    step.data.update({"monster_id": remembered.id, "returning": True})

    # The recognition scene streams while the encounter stages
    step.emit("queue_reunion_text")
    from backend.game.dungeon.generator import generate_reunion_scene

    reunion_text_generation_id = generate_reunion_scene(
        location, remembered, disposition, workflow_name
    )
    step.data.update({"reunion_text_generation_id": reunion_text_generation_id})

    step.emit("emit_generation_id")

    manager.append_dungeon_log(
        f"At {location.get('name', 'the new location')}, the party came face to "
        f"face with {remembered.name} ({remembered.species}) again - it remembers "
        f"them, and its bearing is {disposition}."
    )

    if disposition == 'hostile':
        # A reckoning - straight to battle, its greeting as the intro
        step.emit("start_battle")
        battle_snapshot = start_encounter_battle(
            [remembered],
            opening_note=(
                f"{remembered.name} has returned to face the party, "
                f"hardened by its memories: \"{greeting}\""
            ),
        )
        return success_response(
            {
                "event": "monster_battle",
                "returning": True,
                "current_location": location,
                "enemy_ids": [remembered.id],
                "battle_intro": greeting,
                "battle_snapshot": battle_snapshot,
                "party_conditions": manager.get_party_conditions(),
            }
        )

    if disposition == 'friendly':
        # A warm reunion - it opens the conversation itself
        manager.set_active_encounter(
            {
                'event': 'monster_dialogue',
                'monster_ids': [remembered.id],
                'dialogue': [],
            }
        )
        manager.append_encounter_dialogue(remembered.name, greeting)
        return success_response(
            {
                "event": "monster_dialogue",
                "returning": True,
                "current_location": location,
                "monster_id": remembered.id,
                "greeting": greeting,
                "question": "",
                "party_conditions": manager.get_party_conditions(),
            }
        )

    # wary - a watchful standoff; talk, sneak, or ambush all work
    manager.set_active_encounter(
        {
            'event': 'location_explore',
            'monster_ids': [remembered.id],
            'monsters_present': True,
            'camped': False,
        }
    )
    return success_response(
        {
            "event": "location_explore",
            "returning": True,
            "current_location": location,
            "monsters_present": True,
            "monster_ids": [remembered.id],
            "greeting": greeting,
            "party_conditions": manager.get_party_conditions(),
        }
    )
