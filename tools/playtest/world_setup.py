# World setup for headless playtest runs - the REAL post-Ngx world shape:
# a player character (always in the party) plus companion monsters.
# Rows are created directly (the offline-suite pattern, test_first_run.py)
# so world building costs zero LLM calls; encounter monsters generated
# DURING runs go through the real staged generator against the stub.

import random
from typing import Any


def build_world(rng: random.Random, companion_count: int = 2) -> dict[str, Any]:
    """Reset the test world and stand up player + companions.
    Returns {'player_id': int, 'companion_ids': [int]}."""
    from backend.game.player.manager import PLAYER_MONSTER_KEY
    from backend.game.state.manager import add_following_monster, reset_game_state
    from backend.models.global_variables import GlobalVariable

    reset_game_state()

    player = _make_monster(
        rng,
        name='Aaron the Wayfarer',
        species='Human Adventurer',
        description='The adventurer themself, road-worn and stubborn.',
    )
    GlobalVariable.set(PLAYER_MONSTER_KEY, player.id)

    companion_ids = []
    for index in range(companion_count):
        companion = _make_monster(
            rng,
            name=f'Companion {index + 1}',
            species=rng.choice(['Moss Drake', 'Lantern Wisp', 'Cistern Hound']),
            description='A companion standing with the party for the night.',
        )
        add_following_monster(companion.id)
        companion_ids.append(companion.id)
        _grant_ability(companion, rng)

    return {'player_id': player.id, 'companion_ids': companion_ids}


def grant_starter_item(rng: random.Random):
    """One inventory item so the item-use actions have something to spend"""
    from backend.models.item import Item

    item = Item(
        name='Waybread Bundle',
        emoji='🥖',
        description='Dense travel bread. Restores a little of what the road takes.',
        uses_remaining=rng.randint(2, 4),
    )
    item.save()
    return item


def _make_monster(rng: random.Random, name: str, species: str, description: str):
    from backend.models.monster import Monster

    monster = Monster(
        name=name,
        species=species,
        description=description,
        max_health=rng.randint(40, 70),
        attack=rng.randint(8, 14),
        defense=rng.randint(8, 14),
        speed=rng.randint(8, 14),
        personality_traits=['steadfast'],
        generation_stage='complete',
    )
    monster.save()
    return monster


def _grant_ability(monster, rng: random.Random):
    """A hand-made ability row (no LLM) so battle ability-picks have targets"""
    try:
        from backend.models.ability import Ability

        ability = Ability.create_from_llm_data(
            monster.id,
            {
                'name': rng.choice(['Ember Snap', 'Mosswall', 'Keening Note']),
                'description': 'A practiced trick, reliable in a pinch.',
                'type': rng.choice(['attack', 'defense', 'support']),
            },
        )
        ability.save()
    except Exception as ability_error:
        # Abilities are a bonus for the driver - a schema drift here must
        # not kill the whole night
        print(f"⚠️ Could not grant a starter ability: {ability_error}")
