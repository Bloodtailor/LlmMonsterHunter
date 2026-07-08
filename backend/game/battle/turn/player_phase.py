# Phase A - resolving the player's input: either the pending ally's turn
# (attack/ability/defend/custom/item/talk) or a reply to enemy talk.

from .actions import resolve_combat_turn
from .context import TurnContext
from .negotiation import resolve_talk_exchange


def resolve_player_input(ctx: TurnContext, context: dict, phase: str):
    """Returns the (outcome, resolution, joined_names) the input decided"""
    from backend.game.battle import manager as battle

    outcome, resolution, joined_names = 'unresolved', None, []

    if phase == 'awaiting_player_turn':
        outcome, resolution, joined_names = _resolve_player_turn(ctx, context)

    elif phase == 'awaiting_player_response':
        outcome, resolution, joined_names = _resolve_player_response(ctx, context)

    else:  # 'ready' - opening initiative, straight to the advance loop
        ctx.state['phase'] = 'processing'
        battle.save_battle_state(ctx.state)

    return outcome, resolution, joined_names


def _resolve_player_turn(ctx: TurnContext, context: dict):
    """The pending ally acts on the player's instruction"""
    from backend.game.battle import manager as battle
    from backend.game.battle.generator import resolve_freeform_action
    from backend.game.memory import journal

    ctx.step.emit("resolve_player_turn")

    outcome, resolution, joined_names = 'unresolved', None, []

    player_action = context.get('player_action')
    actor_id = str(ctx.state.get('pending_actor'))
    if not player_action or actor_id not in ctx.state.get('allies', {}):
        raise Exception("No valid player action for the pending turn")

    ctx.state['pending_actor'] = None
    ctx.state['phase'] = 'processing'
    battle.clear_defending(ctx.state, 'allies', actor_id)  # stance ends as the turn begins
    battle.save_battle_state(ctx.state)

    actor_name = ctx.entry_name('allies', actor_id)
    action_type = player_action.get('type')

    if action_type in ('attack', 'ability', 'defend'):
        ability = None
        if action_type == 'ability':
            monster = ctx.monsters.get(actor_id)
            ability = next(
                (
                    a
                    for a in (monster.abilities if monster else [])
                    if a.id == player_action.get('ability_id')
                ),
                None,
            )
            if not ability:
                action_type = 'attack'
        target_id = (
            str(player_action.get('target_id'))
            if player_action.get('target_id') is not None
            else None
        )
        target_side = ctx.find_side(target_id) if target_id else None
        resolve_combat_turn(ctx, 'allies', actor_id, action_type, ability, target_side, target_id)

    elif action_type == 'custom':
        target_id = (
            str(player_action.get('target_id'))
            if player_action.get('target_id') is not None
            else None
        )
        target_name = ctx.entry_name(ctx.find_side(target_id), target_id) if target_id else ''
        result = resolve_freeform_action(
            ctx.location,
            ctx.details_of('allies', actor_id),
            str(player_action.get('text', '')),
            target_name,
            str(player_action.get('info', '')),
            ctx.state,
            ctx.workflow_name,
        )

        # Apply the impact to the referee's named target (validated)
        impact, impacted_side, impacted_id = result['impact'], None, None
        if result['possible'] and impact != 'none':
            impacted_side, impacted_id = ctx.find_by_name(result.get('impact_target'))
            if not impacted_id and target_id:
                impacted_side, impacted_id = ctx.find_side(target_id), target_id
        prior_condition = (
            ctx.state.get(impacted_side, {}).get(str(impacted_id), {}).get('condition')
            if impacted_id
            else None
        )
        new_condition = (
            battle.apply_impact(ctx.state, impacted_side, impacted_id, impact)
            if impacted_id
            else None
        )
        if impacted_id:
            ctx.record_finishing_blow(
                prior_condition,
                new_condition,
                impacted_id,
                'allies',
                actor_id,
                'custom',
                None,
            )

        # A custom action costs something even when it fails - the
        # referee's word first, light exertion otherwise (free failed
        # attempts would reward probing the referee with wild ideas)
        stamina_delta = result.get('stamina_delta')
        mana_delta = result.get('mana_delta')
        if stamina_delta is None and mana_delta is None:
            stamina_delta, mana_delta = 'minor', None
        ctx.apply_resource_deltas(
            'allies', actor_id, impacted_side, impacted_id, stamina_delta, mana_delta
        )

        attempted = str(player_action.get('text', ''))[:70]
        journal.append_journal(
            actor_id,
            f"Tried something of its own ('{attempted}'): "
            f"{'it worked - ' if result['possible'] else 'it failed - '}{result['narration'][:80]}",
        )

        battle.append_log(ctx.state, result['narration'])
        battle.record_turn(
            ctx.state,
            actor_name,
            'custom action' if result['possible'] else 'a failed attempt',
            actor_id=actor_id,
            side='allies',
        )
        battle.save_battle_state(ctx.state)

        ctx.emit_turn(
            {
                'narration': result['narration'],
                'actor_name': actor_name,
                'action': 'custom' if result['possible'] else 'skipped',
                'ability_name': None,
                'target_name': ctx.entry_name(impacted_side, impacted_id) if impacted_id else None,
                'impact': impact if impacted_id else 'none',
                'target_condition': new_condition,
                'dialogue': None,
            }
        )

    elif action_type == 'item':
        from backend.game.inventory.manager import spend_item_use
        from backend.models.item import Item

        item = Item.get_item_by_id(int(player_action.get('item_id')))
        if not item or item.uses_remaining < 1:
            raise Exception("That item is not in the party's inventory")

        # No chosen target = the actor uses it on itself
        target_id = (
            str(player_action.get('target_id'))
            if player_action.get('target_id') is not None
            else None
        )
        target_side = ctx.find_side(target_id) if target_id else None
        if not target_id:
            target_side, target_id = 'allies', actor_id

        resolve_combat_turn(
            ctx, 'allies', actor_id, 'item', None, target_side, target_id, item=item
        )

        # The turn is spent, and so is one use of the item
        # (emits inventory.item_updated or inventory.item_consumed)
        spend_item_use(item)

    elif action_type == 'talk':
        spoken = str(player_action.get('text', ''))
        outcome, resolution, joined_names = resolve_talk_exchange(
            ctx,
            f'The adventuring party says to the hostile monsters: "{spoken}"',
            actor_name,
            spoken,
            initiator_id=actor_id,
            initiator_side='allies',
        )

    else:
        raise Exception(f"Unknown player action type: {action_type}")

    return outcome, resolution, joined_names


def _resolve_player_response(ctx: TurnContext, context: dict):
    """The party answers an enemy that reached for words"""
    from backend.game.battle import manager as battle

    ctx.step.emit("resolve_player_response")

    player_response = str(context.get('player_response') or '')
    pending_talk = ctx.state.get('pending_talk') or {}
    speaker_name = ctx.entry_name('enemies', pending_talk.get('speaker_id'))
    if not player_response:
        raise Exception("No player response for the pending talk")

    ctx.state['pending_talk'] = None
    ctx.state['phase'] = 'processing'
    battle.save_battle_state(ctx.state)

    return resolve_talk_exchange(
        ctx,
        f'{speaker_name} said to the adventuring party: "{pending_talk.get("dialogue", "")}"\n'
        f'The party replied: "{player_response}"',
        'The party',
        player_response,
    )
