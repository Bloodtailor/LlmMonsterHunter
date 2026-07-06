print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

import random
from backend.core.workflow_registry import register_workflow
from backend.core.utils.responses import success_response, error_response
from backend.core.utils.validation import require_keys
from typing import Callable, Dict, Any, List, Optional

@register_workflow()
def battle_round(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """
    Process one battle round: enemy action selection, then every action
    resolved sequentially by the LLM referee. Python owns conditions,
    ordering, and the outcome; the LLM narrates and judges impacts.
    """

    workflow_name = 'battle_round'
    # "context" should have the following keys:
    # actions: [{monster_id, action: 'attack'|'ability'|'defend', ability_id?, target_id?}]
    required_keys = ["actions"]

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.battle import manager as battle
        from backend.game.battle.generator import (
            build_monster_battle_details,
            build_side_details,
            generate_enemy_actions,
            resolve_action,
            generate_battle_outcome_text
        )
        from backend.game.dungeon import manager as dungeon
        from backend.models.monster import Monster

        # Step 0 - validate required keys and battle phase
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        state = battle.get_battle_state()
        if not state.get('in_battle') or state.get('phase') != 'selecting':
            raise Exception("No battle awaiting action selection")

        state['phase'] = 'processing'
        battle.save_battle_state(state)

        # Load Monster objects for everyone in the battle
        monsters = {}
        for side in ('allies', 'enemies'):
            for monster_id in state.get(side, {}):
                monsters[monster_id] = Monster.get_monster_by_id(int(monster_id))

        location = dungeon.get_current_location() or {'name': 'the dungeon', 'description': ''}

        # ===== HELPERS (shared by both sides) =====

        def alive_ids(side):
            return [mid for mid in state.get(side, {}) if not battle.is_incapacitated(state, side, mid)]

        def find_side(monster_id):
            for side in ('allies', 'enemies'):
                if str(monster_id) in state.get(side, {}):
                    return side
            return None

        def entry_name(side, monster_id):
            return state.get(side, {}).get(str(monster_id), {}).get('name', 'Unknown')

        def normalize_player_action(raw) -> Optional[Dict[str, Any]]:
            monster_id = str(raw.get('monster_id'))
            if monster_id not in state.get('allies', {}):
                return None
            action = raw.get('action')
            ability = None
            if action == 'ability':
                ability_id = raw.get('ability_id')
                monster = monsters.get(monster_id)
                ability = next((a for a in (monster.abilities if monster else []) if a.id == ability_id), None)
                if not ability:
                    action = 'attack'  # unknown ability - degrade gracefully
            target_id = str(raw.get('target_id')) if raw.get('target_id') is not None else None
            return {
                'side': 'allies', 'monster_id': monster_id, 'action': action,
                'ability': ability, 'target_id': target_id, 'target_side': find_side(target_id) if target_id else None
            }

        def normalize_enemy_action(raw) -> Optional[Dict[str, Any]]:
            """Resolve the LLM's name-based enemy action to real monsters"""
            name = str(raw.get('name', '')).strip().lower()
            monster_id = next(
                (mid for mid in state.get('enemies', {})
                 if entry_name('enemies', mid).strip().lower() == name),
                None
            )
            if not monster_id or battle.is_incapacitated(state, 'enemies', monster_id):
                return None

            action = str(raw.get('action', 'attack')).strip().lower()
            if action not in ('attack', 'ability', 'defend'):
                action = 'attack'

            ability = None
            if action == 'ability':
                ability_name = str(raw.get('ability_name') or '').strip().lower()
                monster = monsters.get(monster_id)
                ability = next(
                    (a for a in (monster.abilities if monster else []) if a.name.strip().lower() == ability_name),
                    None
                )
                if not ability:
                    action = 'attack'

            target_id, target_side = None, None
            if action != 'defend':
                target_name = str(raw.get('target') or '').strip().lower()
                for side in ('allies', 'enemies'):
                    match = next(
                        (mid for mid in state.get(side, {})
                         if entry_name(side, mid).strip().lower() == target_name),
                        None
                    )
                    if match:
                        target_id, target_side = match, side
                        break
                if not target_id:
                    living = alive_ids('allies')
                    if living:
                        target_id, target_side = random.choice(living), 'allies'

            return {
                'side': 'enemies', 'monster_id': monster_id, 'action': action,
                'ability': ability, 'target_id': target_id, 'target_side': target_side
            }

        def fallback_enemy_action(monster_id) -> Dict[str, Any]:
            living = alive_ids('allies')
            return {
                'side': 'enemies', 'monster_id': monster_id, 'action': 'attack', 'ability': None,
                'target_id': random.choice(living) if living else None,
                'target_side': 'allies' if living else None
            }

        # ===== STEP 1: enemy action selection =====
        step = "select_enemy_actions"
        on_update(step, progress_data)

        enemy_details = build_side_details(monsters, state.get('enemies', {}))
        ally_details = build_side_details(monsters, state.get('allies', {}))
        raw_enemy_actions = generate_enemy_actions(state, enemy_details, ally_details, workflow_name)

        enemy_actions = {}
        for raw in raw_enemy_actions:
            normalized = normalize_enemy_action(raw)
            if normalized:
                enemy_actions[normalized['monster_id']] = normalized
        # Every living enemy acts - fill any the LLM missed
        for monster_id in alive_ids('enemies'):
            if monster_id not in enemy_actions:
                enemy_actions[monster_id] = fallback_enemy_action(monster_id)

        player_actions = [a for a in map(normalize_player_action, context['actions']) if a]

        # ===== STEP 2: defending takes effect for the whole round =====
        battle.clear_defending_all(state)
        all_actions = player_actions + list(enemy_actions.values())
        for act in all_actions:
            if act['action'] == 'defend':
                battle.set_defending(state, act['side'], act['monster_id'])
        battle.save_battle_state(state)

        # ===== STEP 3: order by speed (Python sequencing) =====
        def speed_of(act):
            monster = monsters.get(act['monster_id'])
            return monster.speed if monster else 0
        queue = sorted(all_actions, key=speed_of, reverse=True)

        # ===== STEP 4: resolve sequentially =====
        step = "resolve_actions"
        outcome = 'unresolved'

        for act in queue:
            side, monster_id = act['side'], act['monster_id']
            actor_name = entry_name(side, monster_id)

            # Fallen mid-round - they lose their action (no LLM call needed)
            if battle.is_incapacitated(state, side, monster_id):
                on_update("action_resolved", {"action_result": {
                    'narration': f"{actor_name} lies incapacitated and cannot act.",
                    'actor_name': actor_name, 'action': 'skipped', 'ability_name': None,
                    'target_name': None, 'impact': 'none',
                    'battle_snapshot': battle.get_battle_snapshot(state)
                }})
                continue

            # Attacks retarget if the chosen target already fell (heals may
            # still target the fallen - that's revival, and it's earned)
            target_id, target_side = act['target_id'], act['target_side']
            if act['action'] != 'defend' and target_id:
                target_down = battle.is_incapacitated(state, target_side, target_id)
                is_offensive = target_side != side
                if target_down and is_offensive:
                    living = alive_ids('enemies' if side == 'allies' else 'allies')
                    if living:
                        target_id = random.choice(living)
                        target_side = 'enemies' if side == 'allies' else 'allies'

            # Build the referee's inputs
            actor_monster = monsters.get(monster_id)
            actor_details = build_monster_battle_details(actor_monster, state[side][monster_id]) if actor_monster else actor_name

            if act['action'] == 'defend':
                action_description = f"{actor_name} takes a defensive stance, bracing against incoming attacks."
                target_id, target_side = monster_id, side  # self
            elif act['action'] == 'ability' and act['ability']:
                action_description = (
                    f"{actor_name} uses the ability '{act['ability'].name}': {act['ability'].description} "
                    f"Target: {entry_name(target_side, target_id)}"
                )
            else:
                action_description = f"{actor_name} performs a basic attack on {entry_name(target_side, target_id)}"

            target_monster = monsters.get(target_id)
            target_details = (
                build_monster_battle_details(target_monster, state[target_side][target_id])
                if target_monster else entry_name(target_side, target_id)
            )

            target_name = entry_name(target_side, target_id)
            fallback_narration = f"{actor_name} strikes at {target_name}, landing a solid blow."

            resolution = resolve_action(
                location, actor_details, action_description, target_details,
                state, workflow_name, fallback_narration
            )

            # Python guardrails: defends never harm, self-narrations can't hurt the actor
            impact = resolution['impact']
            if act['action'] == 'defend':
                impact = 'none'

            new_condition = battle.apply_impact(state, target_side, target_id, impact)
            battle.append_log(state, resolution['narration'])
            battle.save_battle_state(state)

            on_update("action_resolved", {"action_result": {
                'narration': resolution['narration'],
                'actor_name': actor_name,
                'action': act['action'],
                'ability_name': act['ability'].name if act.get('ability') else None,
                'target_name': target_name,
                'impact': impact,
                'target_condition': new_condition,
                'battle_snapshot': battle.get_battle_snapshot(state)
            }})

            # An action that ends the battle skips the rest (design 1.3.3)
            outcome = battle.derive_outcome(state)
            if outcome != 'unresolved':
                break

        # ===== STEP 5: round / battle outcome =====
        step = "determine_outcome"
        on_update(step, progress_data)

        outcome_text = None
        if outcome in ('victory', 'defeat'):
            from backend.game.state.manager import get_party_details

            outcome_text = generate_battle_outcome_text(
                outcome, location, get_party_details(),
                build_side_details(monsters, state.get('enemies', {})),
                state, workflow_name
            )

            # Battle damage persists in the run
            dungeon.set_party_conditions({
                monster_id: entry.get('condition', 'fresh')
                for monster_id, entry in state.get('allies', {}).items()
            })

            state['phase'] = outcome
            battle.save_battle_state(state)

            if outcome == 'defeat':
                # The run is over - clear everything backend-side
                battle.end_battle()
                dungeon.exit_dungeon()
        else:
            battle.next_round()

        return success_response({
            "outcome": outcome,
            "outcome_text": outcome_text,
            "round": battle.get_battle_state().get('round', 0),
            "battle_snapshot": battle.get_battle_snapshot()
        })

    except Exception as e:
        # Unstick the battle so the player can retry the round
        try:
            from backend.game.battle import manager as battle
            recovery = battle.get_battle_state()
            if recovery.get('in_battle'):
                recovery['phase'] = 'selecting'
                battle.save_battle_state(recovery)
        except Exception:
            pass

        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })
