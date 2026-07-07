# Resolving one combat turn - attack, ability, defend, or item - via the
# LLM referee, then applying its judgment through the word ladders.

from .context import TurnContext


def resolve_combat_turn(
    ctx: TurnContext,
    side,
    actor_id,
    action,
    ability,
    target_side,
    target_id,
    item=None,
    autonomous=False,
):
    """Resolve one attack/ability/defend/item turn via the referee.
    autonomous marks a wary ally acting on its own (turn/autonomy.py) so
    the frontend can label the turn."""
    from backend.game.battle import manager as battle
    from backend.game.battle.generator import resolve_action
    from backend.game.memory import journal

    actor_name = ctx.entry_name(side, actor_id)

    if action == 'defend':
        target_side, target_id = side, actor_id
        action_description = (
            f"{actor_name} takes a defensive stance, bracing against incoming attacks."
        )
    elif action == 'ability' and ability:
        action_description = (
            f"{actor_name} uses the ability '{ability.name}': {ability.description} "
            f"Target: {ctx.entry_name(target_side, target_id)}"
        )
    elif action == 'item' and item:
        action_description = (
            f"{actor_name} uses the party's item '{item.name}': {item.description} "
            f"Target: {ctx.entry_name(target_side, target_id)}. "
            f"One use of the item is spent regardless of the outcome."
        )
    else:
        action = 'attack'
        action_description = (
            f"{actor_name} performs a basic attack on {ctx.entry_name(target_side, target_id)}"
        )

    target_name = ctx.entry_name(target_side, target_id)
    fallback_narration = (
        f"{actor_name} uses {item.name}, and its effect washes over {target_name}."
        if action == 'item' and item
        else f"{actor_name} strikes at {target_name}, landing a solid blow."
    )
    resolution = resolve_action(
        ctx.location,
        ctx.details_of(side, actor_id),
        action_description,
        ctx.details_of(target_side, target_id),
        ctx.state,
        ctx.workflow_name,
        fallback_narration,
    )

    impact = 'none' if action == 'defend' else resolution['impact']
    if action == 'defend':
        battle.set_defending(ctx.state, side, actor_id)

    prior_condition = ctx.state.get(target_side, {}).get(str(target_id), {}).get('condition')
    new_condition = battle.apply_impact(ctx.state, target_side, target_id, impact)
    ctx.record_finishing_blow(
        prior_condition,
        new_condition,
        target_id,
        side,
        actor_id,
        action,
        ability.name if ability else (item.name if item else None),
    )

    # Reserves: the referee's judgment, or the code default when
    # it stayed silent on both pools
    stamina_delta = resolution.get('stamina_delta')
    mana_delta = resolution.get('mana_delta')
    if stamina_delta is None and mana_delta is None:
        stamina_delta, mana_delta = ctx.default_resource_deltas(action, ability)
    ctx.apply_resource_deltas(side, actor_id, target_side, target_id, stamina_delta, mana_delta)

    # Party monsters journal what they did (feeds growth reflections)
    if side == 'allies':
        used = ability.name if ability else (item.name if item else 'a basic attack')
        prefix = 'Acting on its own terms, used' if autonomous else 'Used'
        journal.append_journal(
            actor_id,
            f"{prefix} {used} on {target_name} ({impact}): {resolution['narration'][:110]}",
        )

    # A companion's healing deepens trust (first heals each run - the
    # per-run valve in affinity.py keeps this honest)
    if (
        side == 'allies'
        and target_side == 'allies'
        and str(actor_id) != str(target_id)
        and str(impact).startswith('heal')
    ):
        from backend.game.monster.affinity import step_affinity

        step_affinity(int(target_id), 'healed_by_ally')

    battle.append_log(ctx.state, resolution['narration'])
    battle.record_turn(ctx.state, actor_name, action, actor_id=actor_id, side=side)
    battle.save_battle_state(ctx.state)

    used_name = ability.name if ability else (item.name if item else None)
    ctx.emit_turn(
        {
            'narration': resolution['narration'],
            'actor_name': actor_name,
            'action': action,
            'ability_name': used_name,
            'target_name': target_name,
            'impact': impact,
            'target_condition': new_condition,
            'dialogue': None,
            'autonomous': autonomous,
        }
    )
