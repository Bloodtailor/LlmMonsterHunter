# Location explore - the most common arrival: look around, maybe meet
# the creatures that dwell here (sometimes one the party already knows)

from typing import Any

from backend.core.utils.responses import success_response
from backend.core.workflow_steps import WorkflowStep


def run_location_explore(step: WorkflowStep, location: dict, workflow_name: str) -> dict[str, Any]:
    """Arrive, look around, and reveal any creatures living here"""
    from backend.game.dungeon import manager
    from backend.game.dungeon.events import roll_explore_monster_count, roll_monsters_present
    from backend.game.dungeon.generator import generate_look_around_text
    from backend.game.monster.card_art import generate_card_art
    from backend.game.monster.generator import (
        generate_ability,
        generate_contextual_monster,
    )

    # Python decides whether creatures dwell here
    monsters_present = roll_monsters_present()

    # Step 3 - queue streamed look-around text
    step.emit("queue_look_text")
    look_text_generation_id = generate_look_around_text(location, monsters_present, workflow_name)
    step.data.update({"look_text_generation_id": look_text_generation_id})

    # Step 4 - frontend picks the generation id up from this step
    step.emit("emit_generation_id")

    # Steps 5+ - the creatures of this place, revealed live (if any).
    # Sometimes one of them is a monster the party has met before -
    # it takes a fresh monster's slot, memories and all (no
    # generation needed; it already exists in full).
    monsters = []
    if monsters_present:
        from backend.game.memory import returning

        monster_count = roll_explore_monster_count()
        blended = returning.maybe_blend_in()
        if blended:
            step.emit("reveal_returning_monster")
            returning.stage_reveal(blended)
            monsters.append(blended)
            monster_count -= 1

        for i in range(monster_count):
            step.emit(f"generate_area_monster_{i + 1}")
            monster = generate_contextual_monster(location)
            generate_ability(monster)
            generate_ability(monster)
            generate_card_art(monster)
            monsters.append(monster)

    # The explore encounter holds what the party found here
    manager.set_active_encounter(
        {
            'event': 'location_explore',
            'monster_ids': [monster.id for monster in monsters],
            'monsters_present': monsters_present,
            'camped': False,
        }
    )

    from backend.game.memory.journal import append_party_journal
    from backend.game.memory.manager import mark_seen

    mark_seen([monster.id for monster in monsters])

    if monsters_present:
        monster_names = ', '.join(f"{m.name} ({m.species})" for m in monsters)
        manager.append_dungeon_log(
            f"Looking around, the party spotted creatures that have not noticed them yet: {monster_names}."
        )
        append_party_journal(
            f"Explored {location.get('name', 'a new area')} and spotted {monster_names}."
        )
    else:
        manager.append_dungeon_log(
            "The party looked around and found the area free of other creatures."
        )
        append_party_journal(f"Explored {location.get('name', 'a new area')} - quiet and empty.")

    return success_response(
        {
            "event": "location_explore",
            "current_location": location,
            "monsters_present": monsters_present,
            "monster_ids": [monster.id for monster in monsters],
            "party_conditions": manager.get_party_conditions(),
        }
    )
