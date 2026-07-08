# Autonomous ally turns - a WARY monster fights on its own terms.
# When the turn director picks a party monster whose affinity is 'wary'
# (game/monster/affinity.py), control never reaches the player: the LLM
# chooses its action like an enemy turn (attack/ability/defend, never
# against the party), the turn resolves, and the advance loop moves on.
# The player watches - trust is earned, not assumed.

import random

from .actions import resolve_combat_turn
from .context import TurnContext


def resolve_autonomous_ally_turn(ctx: TurnContext, actor_id: str) -> None:
    """One wary ally's self-directed turn - always resolves something"""
    from backend.game.battle import manager as battle
    from backend.game.battle.context_blocks import build_side_details
    from backend.game.battle.generator import (
        generate_ally_autonomous_turn,
        generate_turn_vanity_text,
    )

    battle.clear_defending(ctx.state, 'allies', actor_id)

    # The one-sentence thought still streams - the player sees the mood
    # of the companion acting without them. Failure never blocks the turn.
    try:
        ctx.step.mark("queue_turn_vanity")
        turn_vanity_generation_id = generate_turn_vanity_text(
            ctx.details_of('allies', actor_id), ctx.location, ctx.state, ctx.workflow_name
        )
        ctx.step.data.update({"turn_vanity_generation_id": turn_vanity_generation_id})
        ctx.step.emit("emit_generation_id")
    except Exception:
        pass

    ctx.step.mark("resolve_autonomous_turn")
    raw = generate_ally_autonomous_turn(
        ctx.details_of('allies', actor_id),
        build_side_details(ctx.monsters, ctx.state.get('allies', {}), 'allies'),
        build_side_details(ctx.monsters, ctx.state.get('enemies', {}), 'enemies'),
        ctx.state,
        ctx.workflow_name,
    )

    action = str(raw.get('action', 'attack')).strip().lower()
    if action not in ('attack', 'ability', 'defend'):
        action = 'attack'

    ability = None
    if action == 'ability':
        monster = ctx.monsters.get(str(actor_id))
        wanted = str(raw.get('ability_name') or '').strip().lower()
        ability = next(
            (a for a in (monster.abilities if monster else []) if a.name.strip().lower() == wanted),
            None,
        )
        if not ability:
            action = 'attack'

    target_side, target_id = (None, None)
    if action != 'defend':
        target_side, target_id = ctx.find_by_name(raw.get('target'))
        # It fights BESIDE the party: a basic attack may never land on
        # an ally, and a missing target becomes a random enemy
        if not target_id or (target_side == 'allies' and action == 'attack'):
            living = battle.active_ids(ctx.state, 'enemies')
            if not living:
                return  # no enemies left - the loop will settle the outcome
            target_side, target_id = 'enemies', random.choice(living)

    resolve_combat_turn(
        ctx, 'allies', actor_id, action, ability, target_side, target_id, autonomous=True
    )
