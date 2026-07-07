# Shared battle starter - dialogue outcomes, failed sneaks, surprise
# attacks, and hostile reunions all start battles against monsters that
# ALREADY exist (unlike the monster_battle event, which generates its
# enemies on arrival)

from typing import Any


def start_encounter_battle(monsters: list[Any], opening_note: str = None) -> dict[str, Any]:
    """Start a battle against existing monsters; returns the battle snapshot"""
    from backend.game.battle import manager as battle_manager
    from backend.game.dungeon import manager
    from backend.models.monster import Monster

    enemy_entries = {
        str(monster.id): {'name': monster.name, 'condition': 'fresh', 'defending': False}
        for monster in monsters
    }

    ally_conditions = {}
    party_resources = manager.get_party_resources()
    for monster_id, condition in manager.get_party_conditions().items():
        ally = Monster.get_monster_by_id(int(monster_id))
        pools = party_resources.get(str(monster_id), {})
        ally_conditions[monster_id] = {
            'name': ally.name if ally else f'Monster {monster_id}',
            'condition': condition,
            'stamina': pools.get('stamina', 'brimming'),
            'mana': pools.get('mana', 'brimming'),
        }

    battle_state = battle_manager.start_battle(ally_conditions, enemy_entries)

    # Seed the battle's own log so the referee knows how this fight started
    # (an ambush, a failed sneak, an insulted monster...)
    if opening_note:
        battle_manager.append_log(battle_state, opening_note)
        battle_manager.save_battle_state(battle_state)

    return battle_manager.get_battle_snapshot(battle_state)
