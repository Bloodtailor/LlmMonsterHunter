# Dungeon Debug Service - the DEVELOPER X-RAY, split from dungeon_service
# Everything the dungeon/battle LLM prompts are built from, produced by
# the SAME builder functions the generators use - so the Developer
# screen's debug panel shows exactly what the LLM sees. Includes hidden
# information (path events, destinations); never use for game UI.

from typing import Any

from backend.core.utils import success_response
from backend.game.battle import manager as battle_manager
from backend.game.dungeon import manager


def get_debug_context() -> dict[str, Any]:
    """The full LLM-context X-ray for the Developer screen"""
    from backend.game.battle.context_blocks import (
        build_battle_situation,
        build_combatant_summary,
        build_recent_log,
        build_turn_history,
    )
    from backend.game.dungeon.generator import build_monsters_details, build_party_dungeon_details
    from backend.game.state.manager import get_party_summary
    from backend.models.monster import Monster

    dungeon_state = manager.get_dungeon_state()
    encounter = dungeon_state.get('active_encounter') or {}

    encounter_monsters = [
        m
        for m in (Monster.get_monster_by_id(int(mid)) for mid in encounter.get('monster_ids', []))
        if m
    ]

    battle_state = battle_manager.get_battle_state()
    battle_monsters = {}
    if battle_state.get('in_battle'):
        for side in ('allies', 'enemies'):
            for monster_id in battle_state.get(side, {}):
                battle_monsters[monster_id] = Monster.get_monster_by_id(int(monster_id))

    return success_response(
        {
            'in_dungeon': dungeon_state.get('in_dungeon', False),
            'current_location': dungeon_state.get('current_location'),
            # The rolling story of the run: raw entries + the budget-clamped
            # text actually injected into every dungeon prompt
            'dungeon_log': {
                'entries': manager.get_dungeon_log_entries(),
                'clamped_text': manager.get_dungeon_log_text(),
            },
            # The party exactly as dungeon prompts describe it
            'party': {
                'summary': get_party_summary(),
                'details_text': build_party_dungeon_details(),
                'conditions': dungeon_state.get('party_conditions', {}),
                'resources': dungeon_state.get('party_resources', {}),
            },
            # Run identity and the per-monster journal feeding growth reflections
            'run_id': dungeon_state.get('run_id'),
            'run_journal': dungeon_state.get('run_journal', {}),
            'seen_monster_ids': dungeon_state.get('seen_monster_ids', []),
            # The active encounter's context blocks
            'encounter': {
                'event': encounter.get('event'),
                'monster_ids': encounter.get('monster_ids', []),
                'monsters_present': encounter.get('monsters_present'),
                'camped': encounter.get('camped'),
                'dialogue_entries': encounter.get('dialogue', []),
                'dialogue_clamped_text': manager.get_encounter_dialogue_text() if encounter else '',
                'monster_details_text': build_monsters_details(encounter_monsters)
                if encounter_monsters
                else '',
            }
            if encounter
            else None,
            # Paths WITH their hidden events and destinations (the X-ray part)
            'paths_full': dungeon_state.get('available_paths', {}),
            # The battle's context blocks, as the referee/director prompts see them
            'battle': {
                'in_battle': battle_state.get('in_battle', False),
                'phase': battle_state.get('phase'),
                'turn_count': battle_state.get('turn_count', 0),
                'situation_text': build_battle_situation(battle_state),
                'combatant_summary_text': build_combatant_summary(battle_monsters, battle_state),
                'turn_history_text': build_turn_history(battle_state),
                'recent_log_text': build_recent_log(battle_state),
                'recent_log_entries': battle_state.get('recent_log', []),
            }
            if battle_state.get('in_battle')
            else {'in_battle': False},
        }
    )
