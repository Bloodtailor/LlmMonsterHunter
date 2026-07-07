# Treasure - a hidden item waits to be discovered at the new location

from typing import Any

from backend.core.utils.responses import success_response
from backend.core.workflow_steps import WorkflowStep


def run_treasure(step: WorkflowStep, location: dict, workflow_name: str) -> dict[str, Any]:
    """Generate the found item and its streamed discovery narration"""
    from backend.game.dungeon import manager
    from backend.game.inventory.generator import (
        generate_treasure_discovery_text,
        generate_treasure_item,
    )

    # Step 3 - the item itself (emits inventory.item_added; provisional
    # until the party exits alive)
    step.emit("generate_treasure_item")
    item = generate_treasure_item(location)
    from backend.game.dungeon.spoils import record_run_item

    record_run_item(item.id)
    step.data.update({"item": item.to_dict()})

    # Step 4 - queue streamed discovery narration referencing the item
    step.emit("queue_treasure_text")
    treasure_text_generation_id = generate_treasure_discovery_text(location, item, workflow_name)
    step.data.update({"treasure_text_generation_id": treasure_text_generation_id})

    # Step 5 - frontend picks the generation id up from this step
    step.emit("emit_generation_id")

    # After the discovery the moment plays like a creature-free
    # explore - the party looks up and decides where to go next
    manager.set_active_encounter(
        {
            'event': 'location_explore',
            'monster_ids': [],
            'monsters_present': False,
            'camped': False,
        }
    )

    manager.append_dungeon_log(
        f"At {location.get('name', 'the new location')}, the party discovered "
        f"a hidden treasure: {item.name} ({item.description})"
    )
    from backend.game.memory.journal import append_party_journal

    append_party_journal(f"Found treasure at {location.get('name', 'a new area')}: {item.name}.")

    return success_response(
        {
            "event": "treasure",
            "current_location": location,
            "item": item.to_dict(),
            "monsters_present": False,
            "monster_ids": [],
            "party_conditions": manager.get_party_conditions(),
        }
    )
