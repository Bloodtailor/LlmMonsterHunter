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
        from backend.game.battle.constants import (
            MAX_CONSECUTIVE_ENEMY_TURNS,
            OVERDUE_WAIT_MULTIPLIER,
            RESOURCE_DELTAS,
            ABILITY_POOL_BY_TYPE
        )
        from backend.game.battle.generator import (
            build_monster_battle_details,
            build_side_details,
            build_combatant_summary,
            generate_next_turn,
            generate_enemy_turn,
            resolve_action,
            resolve_freeform_action,
            generate_battle_talk,
            generate_battle_outcome_text,
            generate_battle_summary,
            generate_turn_vanity_text
        )
        from backend.game.dungeon import manager as dungeon
        from backend.game.state.manager import get_party_details
        from backend.game.memory import journal
        from backend.game.memory import manager as memory
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
                # Side is baked into the details so the referee always
                # knows who fights for whom
                return build_monster_battle_details(monster, state[side][str(monster_id)], side)
            return entry_name(side, monster_id)

        def emit_turn(entry: Dict[str, Any]):
            """One resolved turn for the frontend's click-through log"""
            entry['battle_snapshot'] = battle.get_battle_snapshot(state)
            on_update("action_resolved", {"action_result": entry})

        def record_finishing_blow(prior_condition, new_condition, target_id,
                                  actor_side, actor_id, action, used_name):
            """
            Remember WHO dropped a monster and WITH WHAT (in place) - the
            monster's 'was_defeated' memory names its defeater, and a
            returning grudge can answer that exact move.
            """
            if new_condition != 'incapacitated' or prior_condition == 'incapacitated':
                return
            blows = state.get('finishing_blows', {})
            blows[str(target_id)] = {
                'by_id': str(actor_id),
                'by_name': entry_name(actor_side, actor_id),
                'action': action,
                'ability_name': used_name
            }
            state['finishing_blows'] = blows

        def apply_resource_deltas(actor_side, actor_id, target_side, target_id,
                                  stamina_delta, mana_delta):
            """
            Spend and restore reserves (in place). Costs (positive deltas)
            always tire the ACTOR; restores (negative deltas) land on the
            TARGET - so a defend rests the defender, and a soothing mist
            aimed at an ally rests the ally.
            """
            for resource, delta in (('stamina', stamina_delta), ('mana', mana_delta)):
                if not delta or delta == 'none':
                    continue
                if RESOURCE_DELTAS.get(delta, 0) > 0:
                    battle.apply_resource(state, actor_side, actor_id, resource, delta)
                else:
                    restore_side = target_side or actor_side
                    restore_id = target_id or actor_id
                    battle.apply_resource(state, restore_side, restore_id, resource, delta)

        def default_resource_deltas(action, ability):
            """The code's own cost ruling when the referee stays silent"""
            if action == 'ability' and ability:
                pool = ABILITY_POOL_BY_TYPE.get(ability.ability_type, 'stamina')
                return ('moderate', None) if pool == 'stamina' else (None, 'moderate')
            if action == 'attack':
                return 'minor', None
            if action == 'defend':
                # Standing guard is also catching your breath
                return 'restore_minor', None
            return None, None  # items and talk cost the monster nothing

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

        def resolve_combat_turn(side, actor_id, action, ability, target_side, target_id, item=None):
            """Resolve one attack/ability/defend/item turn via the referee"""
            actor_name = entry_name(side, actor_id)

            if action == 'defend':
                target_side, target_id = side, actor_id
                action_description = f"{actor_name} takes a defensive stance, bracing against incoming attacks."
            elif action == 'ability' and ability:
                action_description = (
                    f"{actor_name} uses the ability '{ability.name}': {ability.description} "
                    f"Target: {entry_name(target_side, target_id)}"
                )
            elif action == 'item' and item:
                action_description = (
                    f"{actor_name} uses the party's item '{item.name}': {item.description} "
                    f"Target: {entry_name(target_side, target_id)}. "
                    f"One use of the item is spent regardless of the outcome."
                )
            else:
                action = 'attack'
                action_description = f"{actor_name} performs a basic attack on {entry_name(target_side, target_id)}"

            target_name = entry_name(target_side, target_id)
            fallback_narration = (
                f"{actor_name} uses {item.name}, and its effect washes over {target_name}."
                if action == 'item' and item else
                f"{actor_name} strikes at {target_name}, landing a solid blow."
            )
            resolution = resolve_action(
                location, details_of(side, actor_id), action_description,
                details_of(target_side, target_id), state, workflow_name,
                fallback_narration
            )

            impact = 'none' if action == 'defend' else resolution['impact']
            if action == 'defend':
                battle.set_defending(state, side, actor_id)

            prior_condition = state.get(target_side, {}).get(str(target_id), {}).get('condition')
            new_condition = battle.apply_impact(state, target_side, target_id, impact)
            record_finishing_blow(prior_condition, new_condition, target_id,
                                  side, actor_id, action,
                                  ability.name if ability else (item.name if item else None))

            # Reserves: the referee's judgment, or the code default when
            # it stayed silent on both pools
            stamina_delta = resolution.get('stamina_delta')
            mana_delta = resolution.get('mana_delta')
            if stamina_delta is None and mana_delta is None:
                stamina_delta, mana_delta = default_resource_deltas(action, ability)
            apply_resource_deltas(side, actor_id, target_side, target_id,
                                  stamina_delta, mana_delta)

            # Party monsters journal what they did (feeds growth reflections)
            if side == 'allies':
                used = ability.name if ability else (item.name if item else 'a basic attack')
                journal.append_journal(
                    actor_id,
                    f"Used {used} on {target_name} ({impact}): {resolution['narration'][:110]}"
                )

            battle.append_log(state, resolution['narration'])
            battle.record_turn(state, actor_name, action, actor_id=actor_id, side=side)
            battle.save_battle_state(state)

            used_name = ability.name if ability else (item.name if item else None)
            emit_turn({
                'narration': resolution['narration'], 'actor_name': actor_name,
                'action': action, 'ability_name': used_name,
                'target_name': target_name, 'impact': impact,
                'target_condition': new_condition, 'dialogue': None
            })

        def resolve_talk_exchange(exchange: str, initiator_name: str, spoken: str, initiator_id=None, initiator_side=None):
            """Run the negotiation adjudicator and apply its decision"""
            talk = generate_battle_talk(
                location,
                build_side_details(monsters, state.get('enemies', {}), 'enemies'),
                build_side_details(monsters, state.get('allies', {}), 'allies'),
                exchange, state, workflow_name
            )
            battle.append_log(state, f'{initiator_name} spoke: "{spoken}" The reply: "{talk["response"]}"')
            battle.record_turn(state, initiator_name, 'talk', actor_id=initiator_id, side=initiator_side)
            battle.save_battle_state(state)

            # Words spoken mid-battle are exactly what growth reflections
            # want to see - who this monster talks to, and about what
            talk_note = f'Chose words over blows: said "{spoken[:70]}" - the enemy answered "{talk["response"][:60]}"'
            if initiator_side == 'allies' and initiator_id:
                journal.append_journal(initiator_id, talk_note)
            elif initiator_id is None:
                journal.append_party_journal(talk_note)

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
                prior_condition = (state.get(impacted_side, {}).get(str(impacted_id), {}).get('condition')
                                   if impacted_id else None)
                new_condition = battle.apply_impact(state, impacted_side, impacted_id, impact) if impacted_id else None
                if impacted_id:
                    record_finishing_blow(prior_condition, new_condition, impacted_id,
                                          'allies', actor_id, 'custom', None)

                # A custom action that actually happened costs something -
                # referee's word first, light exertion otherwise
                stamina_delta = result.get('stamina_delta')
                mana_delta = result.get('mana_delta')
                if stamina_delta is None and mana_delta is None and result['possible']:
                    stamina_delta, mana_delta = 'minor', None
                apply_resource_deltas('allies', actor_id, impacted_side, impacted_id,
                                      stamina_delta, mana_delta)

                attempted = str(player_action.get('text', ''))[:70]
                journal.append_journal(
                    actor_id,
                    f"Tried something of its own ('{attempted}'): "
                    f"{'it worked - ' if result['possible'] else 'it failed - '}{result['narration'][:80]}"
                )

                battle.append_log(state, result['narration'])
                battle.record_turn(
                    state, actor_name,
                    'custom action' if result['possible'] else 'a failed attempt',
                    actor_id=actor_id, side='allies'
                )
                battle.save_battle_state(state)

                emit_turn({
                    'narration': result['narration'], 'actor_name': actor_name,
                    'action': 'custom' if result['possible'] else 'skipped',
                    'ability_name': None,
                    'target_name': entry_name(impacted_side, impacted_id) if impacted_id else None,
                    'impact': impact if impacted_id else 'none',
                    'target_condition': new_condition, 'dialogue': None
                })

            elif action_type == 'item':
                from backend.models.item import Item
                from backend.game.inventory.manager import spend_item_use

                item = Item.get_item_by_id(int(player_action.get('item_id')))
                if not item or item.uses_remaining < 1:
                    raise Exception("That item is not in the party's inventory")

                # No chosen target = the actor uses it on itself
                target_id = str(player_action.get('target_id')) if player_action.get('target_id') is not None else None
                target_side = find_side(target_id) if target_id else None
                if not target_id:
                    target_side, target_id = 'allies', actor_id

                resolve_combat_turn('allies', actor_id, 'item', None, target_side, target_id, item=item)

                # The turn is spent, and so is one use of the item
                # (emits inventory.item_updated or inventory.item_consumed)
                spend_item_use(item)

            elif action_type == 'talk':
                spoken = str(player_action.get('text', ''))
                outcome, resolution, joined_names = resolve_talk_exchange(
                    f'The adventuring party says to the hostile monsters: "{spoken}"',
                    actor_name, spoken, initiator_id=actor_id, initiator_side='allies'
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

            # The turn director picks who acts next (LLM choice inside
            # Python guardrails: the softlock valve keeps the player in
            # the fight, and the fairness guardrail force-picks anyone
            # the LLM has neglected for too long - no monster is ever
            # forgotten, regardless of model quality)
            force_ally = consecutive_enemy_turns >= MAX_CONSECUTIVE_ENEMY_TURNS
            eligible_sides = ('allies',) if force_ally else ('allies', 'enemies')

            living = [
                (s, mid) for s in ('allies', 'enemies') for mid in battle.active_ids(state, s)
            ]
            overdue_threshold = OVERDUE_WAIT_MULTIPLIER * max(len(living), 1)
            overdue = sorted(
                (
                    (battle.turns_waiting(state, mid), s, mid)
                    for s, mid in living
                    if s in eligible_sides and battle.turns_waiting(state, mid) >= overdue_threshold
                ),
                reverse=True
            )

            if overdue:
                _, side, actor_id = overdue[0]
            else:
                picked = generate_next_turn(build_combatant_summary(monsters, state), state, workflow_name)
                side, actor_id = find_by_name(picked, sides=eligible_sides)

            if not actor_id:
                # Fallback: longest-waiting first, fastest breaks ties
                candidates = []
                for s in eligible_sides:
                    for mid in battle.active_ids(state, s):
                        speed = monsters[mid].speed if monsters.get(mid) else 0
                        candidates.append((-battle.turns_waiting(state, mid), -speed, s, mid))
                if not candidates:
                    break
                candidates.sort()
                _, _, side, actor_id = candidates[0]

            if side == 'allies':
                # The player's monster - hand control back
                state['pending_actor'] = actor_id
                state['phase'] = 'awaiting_player_turn'
                battle.save_battle_state(state)

                # Streamed inner monologue for the acting monster - what it
                # feels, thinks, and wants (the player still decides the
                # action). Failure can never block the turn.
                try:
                    step = "queue_turn_vanity"
                    turn_vanity_generation_id = generate_turn_vanity_text(
                        details_of('allies', actor_id), location, state, workflow_name
                    )
                    progress_data.update({ "turn_vanity_generation_id": turn_vanity_generation_id })
                    step = "emit_generation_id"
                    on_update(step, progress_data)
                except Exception:
                    pass

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
                build_side_details(monsters, state.get('allies', {}), 'allies'),
                build_side_details(monsters, state.get('enemies', {}), 'enemies'),
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
                    battle.record_turn(state, actor_name, 'talk', actor_id=actor_id, side='enemies')
                    battle.save_battle_state(state)
                    # The whole party hears an enemy reaching for words
                    journal.append_party_journal(
                        f'Enemy {actor_name} spoke to the party mid-battle: "{dialogue[:90]}"'
                    )
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
                battle.record_turn(state, actor_name, 'flee', actor_id=actor_id, side='enemies')
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
            build_side_details(monsters, state.get('enemies', {}), 'enemies'),
            state, workflow_name
        )

        # Battle damage persists in the run
        dungeon.set_party_conditions({
            monster_id: entry.get('condition', 'fresh')
            for monster_id, entry in state.get('allies', {}).items()
        })

        # So do spent reserves - they refill only on the next dungeon entry
        if dungeon.is_in_dungeon():
            dungeon.set_party_resources({
                monster_id: {'stamina': entry.get('stamina', 'brimming'),
                             'mana': entry.get('mana', 'brimming')}
                for monster_id, entry in state.get('allies', {}).items()
            })

        # The dungeon log gets a summary of the battle - the detailed
        # blow-by-blow stays in the battle's own log. The LLM writes the
        # story (including lasting effects like lingering debuffs); a
        # deterministic line covers the mechanical truth either way.
        summary = None
        if dungeon.is_in_dungeon():
            step = "summarize_battle"
            on_update(step, progress_data)

            enemy_names = ', '.join(
                entry.get('name', 'Unknown') for entry in state.get('enemies', {}).values()
            )
            ally_summary = ', '.join(
                f"{entry.get('name')}: {entry.get('condition')}"
                for entry in state.get('allies', {}).values()
            )

            summary = generate_battle_summary(
                outcome, resolution, joined_names, location,
                build_side_details(monsters, state.get('allies', {}), 'allies'),
                build_side_details(monsters, state.get('enemies', {}), 'enemies'),
                state, workflow_name
            )
            if not summary:
                summary = f"A battle against {enemy_names} ended in {outcome} ({resolution})."
                if joined_names:
                    summary += f" {', '.join(joined_names)} joined the party."

            dungeon.append_dungeon_log(
                f"{summary} Party condition afterward: {ally_summary}."
            )

        # ===== WHAT THE MONSTERS WILL REMEMBER =====
        # Written BEFORE any defeat cleanup wipes the run state. A failed
        # memory must never break the battle result.
        step = "write_battle_memories"
        on_update(step, progress_data)
        try:
            location_name = location.get('name', 'the dungeon')
            party_names = ', '.join(
                entry.get('name', 'Unknown') for entry in state.get('allies', {}).values()
            ) or 'the party'
            memory_details = {'location': location_name}
            if summary:
                memory_details['battle_summary'] = summary[:400]

            for monster_id, entry in state.get('enemies', {}).items():
                name_joined = entry.get('name') in joined_names

                if entry.get('condition') == 'incapacitated':
                    blow = state.get('finishing_blows', {}).get(str(monster_id))
                    content = f"Was defeated in battle by the party ({party_names}) at {location_name}."
                    details = dict(memory_details)
                    if blow:
                        with_what = blow.get('ability_name') or 'a basic attack'
                        content += f" Brought down by {blow.get('by_name')} with {with_what}."
                        details.update({'by': blow.get('by_name'), 'with': with_what})
                    memory.write_memory(int(monster_id), 'was_defeated', content, details)

                elif entry.get('fled'):
                    memory.write_memory(
                        int(monster_id), 'fled_from_party',
                        f"Fled from a battle against the party ({party_names}) at {location_name}.",
                        dict(memory_details)
                    )

                elif name_joined:
                    memory.write_memory(
                        int(monster_id), 'joined_party',
                        f"Chose to join the party ({party_names}) after words won out mid-battle at {location_name}.",
                        dict(memory_details)
                    )

                elif resolution == 'yielded':
                    memory.write_memory(
                        int(monster_id), 'yielded_to_party',
                        f"Yielded to the party ({party_names}) at {location_name} rather than fight to the end.",
                        dict(memory_details)
                    )

                elif outcome == 'defeat':
                    if resolution == 'spared':
                        memory.write_memory(
                            int(monster_id), 'spared_party',
                            f"Defeated the party ({party_names}) at {location_name} and granted their plea for mercy.",
                            dict(memory_details)
                        )
                    else:
                        fallen = ', '.join(
                            e.get('name', 'Unknown') for e in state.get('allies', {}).values()
                            if e.get('condition') == 'incapacitated'
                        )
                        details = dict(memory_details)
                        details['party_fallen'] = fallen
                        memory.write_memory(
                            int(monster_id), 'defeated_party',
                            f"Stood victorious over the party ({party_names}) at {location_name}.",
                            details
                        )

            # The run journal closes the chapter for the party's side
            journal.append_party_journal(
                f"Battle at {location_name} ended in {outcome} ({resolution})."
            )
        except Exception as memory_error:
            print(f"❌ Battle memory writing failed (battle result unaffected): {memory_error}")

        # Every victory mints a unique CoCaTok keepsake commemorating it
        # (emits inventory.cocatok_added; the frontend plays the pickup
        # ceremony from the result payload)
        cocatok_data = None
        if outcome == 'victory':
            step = "mint_victory_cocatok"
            on_update(step, progress_data)
            from backend.game.inventory.generator import generate_victory_cocatok

            defeated_names = [
                entry.get('name', 'Unknown')
                for entry in state.get('enemies', {}).values()
                if entry.get('name') not in joined_names
            ]
            battle_story = summary if dungeon.is_in_dungeon() else (
                f"A battle against {', '.join(defeated_names) or 'fearsome foes'} "
                f"ended in victory ({resolution})."
            )
            cocatok = generate_victory_cocatok(location, battle_story, defeated_names)
            cocatok_data = cocatok.to_dict()
            progress_data.update({ "cocatok": cocatok_data })

        state['phase'] = outcome
        state['resolution'] = resolution
        state['pending_actor'] = None
        state['pending_talk'] = None
        battle.save_battle_state(state)

        defeat_reflection = None
        if outcome == 'defeat':
            # The run is over. The party takes one collective lesson out
            # of the dungeon, the run's history row closes - all BEFORE
            # the wipes below destroy the run state.
            if dungeon.is_in_dungeon():
                step = "defeat_reflection"
                on_update(step, progress_data)
                try:
                    from backend.game.memory import growth
                    party_monsters = [monsters.get(mid) for mid in state.get('allies', {})]
                    defeat_reflection = growth.run_defeat_reflection(
                        [m for m in party_monsters if m], state, workflow_name
                    )
                except Exception as lesson_error:
                    print(f"❌ Defeat lesson failed (the defeat stands): {lesson_error}")

                from backend.models.dungeon_run import DungeonRun
                DungeonRun.close('defeat', summary=summary)
            battle.end_battle()
            dungeon.exit_dungeon()

        return success_response({
            "outcome": outcome,
            "resolution": resolution,
            "joined_names": joined_names,
            "outcome_text": outcome_text,
            "cocatok": cocatok_data,
            "defeat_reflection": defeat_reflection,
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
