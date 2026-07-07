# Camp - resting in a monster-free location: streamed campfire dialogue,
# a referee-judged restore of the party's reserves, and spotlight growth.

from typing import Any

from backend.core.utils.responses import success_response
from backend.core.utils.validation import require_keys
from backend.core.workflow_steps import WorkflowStep


def run_setup_camp(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """
    Set up camp in a monster-free location: streamed vanity dialogue
    between the party's monsters as they rest
    """
    workflow_name = 'setup_camp'

    from backend.game.dungeon import manager
    from backend.game.dungeon.generator import generate_camp_scene

    # Step 0 - validate required keys
    step.emit("validate_context")
    require_keys(context, [])

    # A quiet moment - condense old dungeon-log entries if due
    manager.queue_log_condense_if_due()

    encounter = manager.get_active_encounter()
    if not encounter or encounter.get('event') != 'location_explore':
        raise Exception("This is no place to camp")
    if encounter.get('monster_ids'):
        raise Exception("Cannot camp with creatures nearby")
    if encounter.get('camped'):
        raise Exception("The party has already camped here")

    location = manager.get_current_location() or {'name': 'the dungeon', 'description': ''}

    # Step 1 - queue the streamed camp scene (party conditions travel
    # inside the full party details block)
    step.emit("queue_camp_text")
    camp_text_generation_id = generate_camp_scene(location, workflow_name)
    step.data.update({"camp_text_generation_id": camp_text_generation_id})

    # Step 2 - frontend picks the generation id up from this step
    step.emit("emit_generation_id")

    # Step 3 - one camp per location (marked BEFORE the rest/growth
    # steps so a failure below can never enable double-camping)
    step.emit("mark_camped")
    encounter['camped'] = True
    manager.set_active_encounter(encounter)
    manager.append_dungeon_log(
        f"The party set up camp at {location.get('name', 'the area')} and rested, "
        f"talking around the fire."
    )

    # Step 4 - rest restores the party's reserves (the camp referee
    # judges how much for each monster; failures mean a full rest)
    step.emit("restore_resources")
    from backend.game.battle.constants import (
        BRIMMING,
        RESOURCE_DELTAS,
        RESOURCE_LADDER,
        full_resources,
    )
    from backend.game.dungeon.generator import generate_camp_restore

    restores = generate_camp_restore(location, workflow_name)
    party_resources = manager.get_party_resources()
    for monster_id, pools in restores.items():
        current = party_resources.get(str(monster_id)) or full_resources()
        for resource, delta_word in pools.items():
            steps_delta = RESOURCE_DELTAS.get(delta_word, 0)
            if steps_delta == 0:
                continue
            current_index = RESOURCE_LADDER.index(current.get(resource, BRIMMING))
            new_index = max(0, min(len(RESOURCE_LADDER) - 1, current_index + steps_delta))
            current[resource] = RESOURCE_LADDER[new_index]
        party_resources[str(monster_id)] = current
    manager.set_party_resources(party_resources)
    step.data.update({"party_resources": party_resources})

    # Step 5 - growth: the fire spotlights the 1-2 members whose story
    # mattered most this run; the rest keep the memory of the evening.
    # A failure here never breaks the camp itself.
    step.emit("camp_growth")
    growth_results = []
    try:
        from backend.game.memory import growth
        from backend.game.memory.manager import write_memory
        from backend.game.state.manager import get_party_monster_ids
        from backend.models.monster import Monster

        party_monsters = [
            m for m in (Monster.get_monster_by_id(mid) for mid in get_party_monster_ids()) if m
        ]
        spotlight = growth.pick_spotlight(party_monsters, workflow_name)
        for monster in spotlight:
            step.data.update({"growing": monster.name})
            step.emit("growth_reflection")
            reflection = growth.run_growth_reflection(monster, 'camp', workflow_name)
            if reflection:
                growth_results.append(growth.apply_growth(monster, reflection))

        spotlight_ids = {m.id for m in spotlight}
        location_name = location.get('name', 'the dungeon')
        for monster in party_monsters:
            if monster.id not in spotlight_ids:
                write_memory(
                    monster.id,
                    'camp',
                    f"Rested at a campfire at {location_name} with the party.",
                    {'location': location_name},
                )
    except Exception as growth_error:
        print(f"❌ Camp growth failed (the camp itself stands): {growth_error}")

    step.data.update({"growth": growth_results})

    return success_response(
        {"camped": True, "party_resources": party_resources, "growth": growth_results}
    )
