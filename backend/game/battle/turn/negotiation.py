# Mid-battle negotiation - words instead of blows. The adjudicator hears
# the exchange, answers in the enemies' voice, and DECIDES what happens.

from .context import TurnContext


def apply_talk_decision(ctx: TurnContext, decision: str):
    """Turn a negotiation decision into a battle ending (or not)"""
    from backend.game.battle import manager as battle
    from backend.models.following_monsters import FollowingMonster

    if decision == 'enemies_join':
        joined = []
        for monster_id in battle.active_ids(ctx.state, 'enemies'):
            FollowingMonster.add_follower(int(monster_id))
            joined.append(ctx.entry_name('enemies', monster_id))
        return 'victory', 'joined', joined
    if decision == 'enemies_yield':
        return 'victory', 'yielded', []
    if decision == 'enemies_flee':
        for monster_id in battle.active_ids(ctx.state, 'enemies'):
            battle.mark_fled(ctx.state, monster_id)
        return 'victory', 'fled', []
    if decision == 'party_spared':
        return 'defeat', 'spared', []
    return 'unresolved', None, []


def resolve_talk_exchange(
    ctx: TurnContext,
    exchange: str,
    initiator_name: str,
    spoken: str,
    initiator_id=None,
    initiator_side=None,
):
    """Run the negotiation adjudicator and apply its decision"""
    from backend.game.battle import manager as battle
    from backend.game.battle.generator import build_side_details, generate_battle_talk
    from backend.game.memory import journal

    talk = generate_battle_talk(
        ctx.location,
        build_side_details(ctx.monsters, ctx.state.get('enemies', {}), 'enemies'),
        build_side_details(ctx.monsters, ctx.state.get('allies', {}), 'allies'),
        exchange,
        ctx.state,
        ctx.workflow_name,
    )
    battle.append_log(
        ctx.state, f'{initiator_name} spoke: "{spoken}" The reply: "{talk["response"]}"'
    )
    battle.record_turn(
        ctx.state, initiator_name, 'talk', actor_id=initiator_id, side=initiator_side
    )
    battle.save_battle_state(ctx.state)

    # Words spoken mid-battle are exactly what growth reflections
    # want to see - who this monster talks to, and about what
    talk_note = f'Chose words over blows: said "{spoken[:70]}" - the enemy answered "{talk["response"][:60]}"'
    if initiator_side == 'allies' and initiator_id:
        journal.append_journal(initiator_id, talk_note)
    elif initiator_id is None:
        journal.append_party_journal(talk_note)

    ctx.emit_turn(
        {
            'narration': talk['response'],
            'actor_name': initiator_name,
            'action': 'talk',
            'ability_name': None,
            'target_name': None,
            'impact': 'none',
            'target_condition': None,
            'dialogue': spoken,
        }
    )
    return apply_talk_decision(ctx, talk['decision'])
