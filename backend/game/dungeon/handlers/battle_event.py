# Monster battle - hostile monsters attack the party on arrival.
# Enemies are generated fresh (a remembered monster may blend in).

from typing import Any

from backend.core.utils.responses import success_response
from backend.core.workflow_steps import WorkflowStep

from .encounter_battle import start_encounter_battle


def run_monster_battle(step: WorkflowStep, location: dict, workflow_name: str) -> dict[str, Any]:
    """Reveal the hostile pack, generate its challenge, and start the battle"""
    import random as _random

    from backend.game.battle.constants import ENEMY_COUNT_RANGE
    from backend.game.battle.generator import (
        build_side_details,
        generate_battle_arrival_text,
        generate_battle_intro,
    )
    from backend.game.dungeon import manager
    from backend.game.monster.generator import (
        generate_ability,
        generate_card_art,
        generate_contextual_monster,
    )
    from backend.game.state.manager import get_party_details

    # Step 3 - queue streamed hostile arrival text
    step.emit("queue_encounter_text")
    encounter_text_generation_id = generate_battle_arrival_text(location, workflow_name)
    step.data.update({"encounter_text_generation_id": encounter_text_generation_id})

    # Step 4 - frontend picks the generation id up from this step
    step.emit("emit_generation_id")

    # Steps 5+ - the hostile monsters, fully revealed (emit domain
    # events). An avoided or bested monster from another day may
    # be running with this pack (blend-in).
    from backend.game.memory import returning

    enemy_count = _random.randint(*ENEMY_COUNT_RANGE)
    enemies = []

    blended = returning.maybe_blend_in()
    if blended:
        step.emit("reveal_returning_monster")
        returning.stage_reveal(blended)
        enemies.append(blended)
        enemy_count -= 1

    for i in range(enemy_count):
        step.emit(f"generate_enemy_{i + 1}")
        enemy = generate_contextual_monster(location)
        generate_ability(enemy)
        generate_ability(enemy)
        generate_card_art(enemy)
        enemies.append(enemy)

    from backend.game.memory.manager import mark_seen

    mark_seen([enemy.id for enemy in enemies])

    # Battle intro - the enemies' in-character challenge
    step.emit("generate_battle_intro")
    enemy_entries = {
        str(enemy.id): {'name': enemy.name, 'condition': 'fresh', 'defending': False}
        for enemy in enemies
    }
    enemy_details = build_side_details({str(e.id): e for e in enemies}, enemy_entries, 'enemies')
    battle_intro = generate_battle_intro(
        location, enemy_details, get_party_details(), workflow_name
    )

    # Start the battle - allies carry their run conditions in
    step.emit("start_battle")
    battle_snapshot = start_encounter_battle(enemies)

    enemy_names = ', '.join(f"{e.name} ({e.species})" for e in enemies)
    manager.append_dungeon_log(
        f"Hostile monsters attacked the party on arrival: {enemy_names}. A battle began."
    )

    return success_response(
        {
            "event": "monster_battle",
            "current_location": location,
            "enemy_ids": [enemy.id for enemy in enemies],
            "battle_intro": battle_intro,
            "battle_snapshot": battle_snapshot,
            "party_conditions": manager.get_party_conditions(),
        }
    )
