print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

import random
from backend.core.workflow_registry import register_workflow
from backend.core.utils.responses import success_response, error_response
from typing import Callable, Dict, Any, Optional

@register_workflow()
def battle_turn(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """
    Process battle turns, one monster at a time. Resolves the player's
    input (an ally's turn or a reply to enemy talk), then advances -
    the LLM directs turn order - resolving enemy turns until it is an
    ally's turn again, someone starts talking, or the battle ends.
    """

    workflow_name = 'battle_turn'
    # "context" may have: player_action {...} or player_response str

    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.battle import manager as battle
        from backend.game.battle.constants import MAX_CONSECUTIVE_ENEMY_TURNS
        from backend.game.battle.generator import (
            build_monster_battle_details,
            build_side_details,
            build_combatant_summary,
            generate_next_turn,
            generate_enemy_turn,
            resolve_action,
            resolve_freeform_action,
            generate_battle_talk,
            generate_battle_outcome_text
        )
        from backend.game.dungeon import manager as dungeon
        from backend.game.state.manager import get_party_details
        from backend.models.monster import Monster
        from backend.models.following_monsters import FollowingMonster

        step = "validate_context"
        on_update(step, progress_data)

        state = battle.get_battle_state()
        phase = state.get('phase')
        if not state.get('in_battle') or phase not in ('ready', 'awaiting_player_turn', 'awaiting_player_response'):
            raise Exception(f"Battle is not awaiting input (phase: {phase})")

        # Load Monster objects for everyone in the battle
        monsters = {}
        for side in ('allies', 'enemies'):
            for monster_id in state.get(side, {}):
                monsters[monster_id] = Monster.get_monster_by_id(int(monster_id))

        location = dungeon.get_current_location() or {'name': 'the dungeon', 'description': ''}

        # ===== SHARED HELPERS =====

        def entry_name(side, monster_id):
            return state.get(side, {}).get(str(monster_id), {}).get('name', 'Unknown')

        def find_side(monster_id):
            for side in ('allies', 'enemies'):
                if str(monster_id) in state.get(side, {}):
                    return side
            return None

        def find_by_name(name, sides=('allies', 'enemies')):
            """Resolve a monster name (LLM output) to (side, id) among active fighters"""
            wanted = str(name or '').strip().lower()
            for side in sides:
                for monster_id in battle.active_ids(state, side):
                    if entry_name(side, monster_id).strip().lower() == wanted:
                        return side, monster_id
            return None, None

        def details_of(side, monster_id):
            monster = monsters.get(str(monster_id))
            if monster:
                return build_monster_battle_details(monster, state[side][str(monster_id)])
            return entry_name(side, monster_id)

        def emit_turn(entry: Dict[str, Any]):
            """One resolved turn for the frontend's click-through log"""
            entry['battle_snapshot'] = battle.get_battle_snapshot(state)
            on_update("action_resolved", {"action_result": entry})

        def apply_talk_decision(decision: str):
            """Turn a negotiation decision into a battle ending (or not)"""
            if decision == 'enemies_join':
                joined = []
                for monster_id in battle.active_ids(state, 'enemies'):
                    FollowingMonster.add_follower(int(monster_id))
                    joined.append(entry_name('enemies', monster_id))
                return 'victory', 'joined', joined
            if decision == 'enemies_yield':
                return 'victory', 'yielded', []
            if decision == 'enemies_flee':
                for monster_id in battle.active_ids(state, 'enemies'):
                    battle.mark_fled(state, monster_id)
                return 'victory', 'fled', []
            if decision == 'party_spared':
                return 'defeat', 'spared', []
            return 'unresolved', None, []

        def resolve_combat_turn(side, actor_id, action, ability, target_side, target_id):
            """Resolve one attack/ability/defend turn via the referee"""
            actor_name = entry_name(side, actor_id)

            if action == 'defend':
                target_side, target_id = side, actor_id
                action_description = f"{actor_name} takes a defensive stance, bracing against incoming attacks."
            elif action == 'ability' and ability:
                action_description = (
                    f"{actor_name} uses the ability '{ability.name}': {ability.description} "
                    f"Target: {entry_name(target_side, target_id)}"
                )
            else:
                action = 'attack'
                action_description = f"{actor_name} performs a basic attack on {entry_name(target_side, target_id)}"

            target_name = entry_name(target_side, target_id)
            resolution = resolve_action(
                location, details_of(side, actor_id), action_description,
                details_of(target_side, target_id), state, workflow_name,
                f"{actor_name} strikes at {target_name}, landing a solid blow."
            )

            impact = 'none' if action == 'defend' else resolution['impact']
            if action == 'defend':
                battle.set_defending(state, side, actor_id)

            new_condition = battle.apply_impact(state, target_side, target_id, impact)
            battle.append_log(state, resolution['narration'])
            battle.record_turn(state, actor_name, action)
            battle.save_battle_state(state)

            emit_turn({
                'narration': resolution['narration'], 'actor_name': actor_name,
                'action': action, 'ability_name': ability.name if ability else None,
                'target_name': target_name, 'impact': impact,
                'target_condition': new_condition, 'dialogue': None
            })

        def resolve_talk_exchange(exchange: str, initiator_name: str, spoken: str):
            """Run the negotiation adjudicator and apply its decision"""
            talk = generate_battle_talk(
                location,
                build_side_details(monsters, state.get('enemies', {})),
                build_side_details(monsters, state.get('allies', {})),
                exchange, state, workflow_name
            )
            battle.append_log(state, f'{initiator_name} spoke: "{spoken}" The reply: "{talk["response"]}"')
            battle.record_turn(state, initiator_name, 'talk')
            battle.save_battle_state(state)

            emit_turn({
                'narration': talk['response'], 'actor_name': initiator_name,
                'action': 'talk', 'ability_name': None, 'target_name': None,
                'impact': 'none', 'target_condition': None, 'dialogue': spoken
            })
            return apply_talk_decision(talk['decision'])

        outcome, resolution, joined_names = 'unresolved', None, []

        # ===== PHASE A: resolve the player's input =====

        if phase == 'awaiting_player_turn':
            step = "resolve_player_turn"
            on_update(step, progress_data)

            player_action = context.get('player_action')
            actor_id = str(state.get('pending_actor'))
            if not player_action or actor_id not in state.get('allies', {}):
                raise Exception("No valid player action for the pending turn")

            state['pending_actor'] = None
            state['phase'] = 'processing'
            battle.clear_defending(state, 'allies', actor_id)  # stance ends as the turn begins
            battle.save_battle_state(state)

            actor_name = entry_name('allies', actor_id)
            action_type = player_action.get('type')

            if action_type in ('attack', 'ability', 'defend'):
                ability = None
                if action_type == 'ability':
                    monster = monsters.get(actor_id)
                    ability = next(
                        (a for a in (monster.abilities if monster else []) if a.id == player_action.get('ability_id')),
                        None
                    )
                    if not ability:
                        action_type = 'attack'
                target_id = str(player_action.get('target_id')) if player_action.get('target_id') is not None else None
                target_side = find_side(target_id) if target_id else None
                resolve_combat_turn('allies', actor_id, action_type, ability, target_side, target_id)

            elif action_type == 'custom':
                target_id = str(player_action.get('target_id')) if player_action.get('target_id') is not None else None
                target_name = entry_name(find_side(target_id), target_id) if target_id else ''
                result = resolve_freeform_action(
                    location, details_of('allies', actor_id),
                    str(player_action.get('text', '')), target_name,
                    str(player_action.get('info', '')), state, workflow_name
                )

                # Apply the impact to the referee's named target (validated)
                impact, impacted_side, impacted_id = result['impact'], None, None
                if result['possible'] and impact != 'none':
                    impacted_side, impacted_id = find_by_name(result.get('impact_target'))
                    if not impacted_id and target_id:
                        impacted_side, impacted_id = find_side(target_id), target_id
                new_condition = battle.apply_impact(state, impacted_side, impacted_id, impact) if impacted_id else None

                battle.append_log(state, result['narration'])
                battle.record_turn(state, actor_name, 'custom action' if result['possible'] else 'a failed attempt')
                battle.save_battle_state(state)

                emit_turn({
                    'narration': result['narration'], 'actor_name': actor_name,
                    'action': 'custom' if result['possible'] else 'skipped',
                    'ability_name': None,
                    'target_name': entry_name(impacted_side, impacted_id) if impacted_id else None,
                    'impact': impact if impacted_id else 'none',
                    'target_condition': new_condition, 'dialogue': None
                })

            elif action_type == 'talk':
                spoken = str(player_action.get('text', ''))
                outcome, resolution, joined_names = resolve_talk_exchange(
                    f'The adventuring party says to the hostile monsters: "{spoken}"',
                    actor_name, spoken
                )

            else:
                raise Exception(f"Unknown player action type: {action_type}")

        elif phase == 'awaiting_player_response':
            step = "resolve_player_response"
            on_update(step, progress_data)

            player_response = str(context.get('player_response') or '')
            pending_talk = state.get('pending_talk') or {}
            speaker_name = entry_name('enemies', pending_talk.get('speaker_id'))
            if not player_response:
                raise Exception("No player response for the pending talk")

            state['pending_talk'] = None
            state['phase'] = 'processing'
            battle.save_battle_state(state)

            outcome, resolution, joined_names = resolve_talk_exchange(
                f'{speaker_name} said to the adventuring party: "{pending_talk.get("dialogue", "")}"\n'
                f'The party replied: "{player_response}"',
                'The party', player_response
            )

        else:  # 'ready' - opening initiative, straight to the advance loop
            state['phase'] = 'processing'
            battle.save_battle_state(state)

        # Combat may have decided things already
        if outcome == 'unresolved':
            outcome = battle.derive_outcome(state)
            if outcome != 'unresolved':
                resolution = 'combat'

        # ===== PHASE B: advance until an ally's turn or the battle ends =====

        step = "advance_turns"
        consecutive_enemy_turns = 0

        while outcome == 'unresolved':

            # The turn director picks who acts next (pure LLM choice,
            # with one softlock valve so the player always gets to act)
            force_ally = consecutive_enemy_turns >= MAX_CONSECUTIVE_ENEMY_TURNS
            picked = generate_next_turn(build_combatant_summary(monsters, state), state, workflow_name)
            side, actor_id = find_by_name(picked, sides=('allies',) if force_ally else ('allies', 'enemies'))

            if not actor_id:
                # Fallback: least-recently-acted, fastest first
                recent = [t.get('actor') for t in state.get('turn_history', [])]
                candidates = []
                for s in (('allies',) if force_ally else ('allies', 'enemies')):
                    for mid in battle.active_ids(state, s):
                        name = entry_name(s, mid)
                        last_acted = max((i for i, r in enumerate(recent) if r == name), default=-1)
                        speed = monsters[mid].speed if monsters.get(mid) else 0
                        candidates.append((last_acted, -speed, s, mid))
                if not candidates:
                    break
                candidates.sort()
                _, _, side, actor_id = candidates[0]

            if side == 'allies':
                # The player's monster - hand control back
                state['pending_actor'] = actor_id
                state['phase'] = 'awaiting_player_turn'
                battle.save_battle_state(state)
                return success_response({
                    "pending": "player_turn",
                    "pending_actor": actor_id,
                    "pending_actor_name": entry_name('allies', actor_id),
                    "battle_snapshot": battle.get_battle_snapshot(state)
                })

            # An enemy's turn
            consecutive_enemy_turns += 1
            actor_name = entry_name('enemies', actor_id)
            battle.clear_defending(state, 'enemies', actor_id)

            raw = generate_enemy_turn(
                details_of('enemies', actor_id),
                build_side_details(monsters, state.get('allies', {})),
                build_side_details(monsters, state.get('enemies', {})),
                state, workflow_name
            )
            action = str(raw.get('action', 'attack')).strip().lower()
            if action not in ('attack', 'ability', 'defend', 'talk', 'flee'):
                action = 'attack'

            if action == 'talk':
                dialogue = str(raw.get('dialogue') or '').strip()
                if dialogue:
                    state['pending_talk'] = {'speaker_id': actor_id, 'dialogue': dialogue}
                    state['phase'] = 'awaiting_player_response'
                    battle.record_turn(state, actor_name, 'talk')
                    battle.save_battle_state(state)
                    return success_response({
                        "pending": "player_response",
                        "pending_talk": {"speaker_name": actor_name, "dialogue": dialogue},
                        "battle_snapshot": battle.get_battle_snapshot(state)
                    })
                action = 'attack'  # talk without words - degrade

            if action == 'flee':
                battle.mark_fled(state, actor_id)
                narration = f"{actor_name} breaks away from the fight and vanishes into the shadows of {location.get('name', 'the dungeon')}."
                battle.append_log(state, narration)
                battle.record_turn(state, actor_name, 'flee')
                battle.save_battle_state(state)
                emit_turn({
                    'narration': narration, 'actor_name': actor_name, 'action': 'flee',
                    'ability_name': None, 'target_name': None, 'impact': 'none',
                    'target_condition': None, 'dialogue': None
                })
            else:
                ability = None
                if action == 'ability':
                    monster = monsters.get(actor_id)
                    wanted = str(raw.get('ability_name') or '').strip().lower()
                    ability = next(
                        (a for a in (monster.abilities if monster else []) if a.name.strip().lower() == wanted),
                        None
                    )
                    if not ability:
                        action = 'attack'

                target_side, target_id = (None, None)
                if action != 'defend':
                    target_side, target_id = find_by_name(raw.get('target'))
                    if not target_id or (target_side == 'enemies' and action == 'attack'):
                        living = battle.active_ids(state, 'allies')
                        if not living:
                            break
                        target_side, target_id = 'allies', random.choice(living)

                resolve_combat_turn('enemies', actor_id, action, ability, target_side, target_id)

            outcome = battle.derive_outcome(state)
            if outcome != 'unresolved':
                resolution = 'combat'

        # ===== ENDING =====

        step = "determine_outcome"
        on_update(step, progress_data)

        if outcome not in ('victory', 'defeat'):
            raise Exception("Battle advance loop ended without an outcome")

        resolution = resolution or 'combat'
        outcome_text = generate_battle_outcome_text(
            outcome, resolution, location, get_party_details(),
            build_side_details(monsters, state.get('enemies', {})),
            state, workflow_name
        )

        # Battle damage persists in the run
        dungeon.set_party_conditions({
            monster_id: entry.get('condition', 'fresh')
            for monster_id, entry in state.get('allies', {}).items()
        })

        # The dungeon log gets a compact summary of the battle - the
        # detailed blow-by-blow stays in the battle's own log
        if dungeon.is_in_dungeon():
            enemy_names = ', '.join(
                entry.get('name', 'Unknown') for entry in state.get('enemies', {}).values()
            )
            ally_summary = ', '.join(
                f"{entry.get('name')}: {entry.get('condition')}"
                for entry in state.get('allies', {}).values()
            )
            summary = f"A battle against {enemy_names} ended in {outcome} ({resolution})."
            if joined_names:
                summary += f" {', '.join(joined_names)} joined the party."
            summary += f" Party condition afterward: {ally_summary}."
            dungeon.append_dungeon_log(summary)

        state['phase'] = outcome
        state['resolution'] = resolution
        state['pending_actor'] = None
        state['pending_talk'] = None
        battle.save_battle_state(state)

        if outcome == 'defeat':
            # The run is over - clear everything backend-side
            battle.end_battle()
            dungeon.exit_dungeon()

        return success_response({
            "outcome": outcome,
            "resolution": resolution,
            "joined_names": joined_names,
            "outcome_text": outcome_text,
            "battle_snapshot": battle.get_battle_snapshot()
        })

    except Exception as e:
        # Unstick the battle so the player can retry
        try:
            from backend.game.battle import manager as battle
            recovery = battle.get_battle_state()
            if recovery.get('in_battle') and recovery.get('phase') == 'processing':
                if recovery.get('pending_talk'):
                    recovery['phase'] = 'awaiting_player_response'
                elif recovery.get('pending_actor'):
                    recovery['phase'] = 'awaiting_player_turn'
                else:
                    recovery['phase'] = 'ready'
                battle.save_battle_state(recovery)
        except Exception:
            pass

        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })
