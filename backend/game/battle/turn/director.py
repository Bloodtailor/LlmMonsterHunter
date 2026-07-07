# Phase B - the advance loop: the LLM turn director picks who acts next
# inside Python guardrails (softlock valve, fairness force-pick), enemy
# turns resolve, and control returns to the player when an ally is up or
# an enemy starts talking.

import random

from backend.core.utils.responses import success_response

from .actions import resolve_combat_turn
from .context import TurnContext


def advance_until_player_or_end(ctx: TurnContext, outcome, resolution):
    """
    Advance turns until an ally's turn (returns a pending response), an
    enemy opens talks (pending response), or the battle ends.
    Returns (pending_response_or_None, outcome, resolution).
    """
    from backend.game.battle import manager as battle
    from backend.game.battle.constants import (
        MAX_CONSECUTIVE_ENEMY_TURNS,
        OVERDUE_WAIT_MULTIPLIER,
    )
    from backend.game.battle.context_blocks import build_combatant_summary, build_side_details
    from backend.game.battle.generator import (
        generate_enemy_turn,
        generate_next_turn,
        generate_turn_vanity_text,
    )
    from backend.game.memory import journal

    ctx.step.mark("advance_turns")
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
            (s, mid) for s in ('allies', 'enemies') for mid in battle.active_ids(ctx.state, s)
        ]
        overdue_threshold = OVERDUE_WAIT_MULTIPLIER * max(len(living), 1)
        overdue = sorted(
            (
                (battle.turns_waiting(ctx.state, mid), s, mid)
                for s, mid in living
                if s in eligible_sides and battle.turns_waiting(ctx.state, mid) >= overdue_threshold
            ),
            reverse=True,
        )

        if overdue:
            _, side, actor_id = overdue[0]
        else:
            picked = generate_next_turn(
                build_combatant_summary(ctx.monsters, ctx.state), ctx.state, ctx.workflow_name
            )
            side, actor_id = ctx.find_by_name(picked, sides=eligible_sides)

        if not actor_id:
            # Fallback: longest-waiting first, fastest breaks ties
            candidates = []
            for s in eligible_sides:
                for mid in battle.active_ids(ctx.state, s):
                    speed = ctx.monsters[mid].speed if ctx.monsters.get(mid) else 0
                    candidates.append((-battle.turns_waiting(ctx.state, mid), -speed, s, mid))
            if not candidates:
                break
            candidates.sort()
            _, _, side, actor_id = candidates[0]

        if side == 'allies':
            # A WARY ally never waits for orders - it acts on its own
            # terms and the loop moves on (the player watches)
            from backend.game.monster.affinity import is_autonomous

            monster = ctx.monsters.get(str(actor_id))
            if monster and is_autonomous(monster):
                from . import autonomy

                autonomy.resolve_autonomous_ally_turn(ctx, actor_id)
                consecutive_enemy_turns = 0  # an ally still acted
                outcome = battle.derive_outcome(ctx.state)
                if outcome != 'unresolved':
                    resolution = 'combat'
                continue

            # The player's monster - hand control back
            ctx.state['pending_actor'] = actor_id
            ctx.state['phase'] = 'awaiting_player_turn'
            battle.save_battle_state(ctx.state)

            # Streamed one-sentence thought for the acting monster - what
            # it is thinking at this moment (the player still decides the
            # action). Failure can never block the turn.
            try:
                ctx.step.mark("queue_turn_vanity")
                turn_vanity_generation_id = generate_turn_vanity_text(
                    ctx.details_of('allies', actor_id), ctx.location, ctx.state, ctx.workflow_name
                )
                ctx.step.data.update({"turn_vanity_generation_id": turn_vanity_generation_id})
                ctx.step.emit("emit_generation_id")
            except Exception:
                pass

            pending = success_response(
                {
                    "pending": "player_turn",
                    "pending_actor": actor_id,
                    "pending_actor_name": ctx.entry_name('allies', actor_id),
                    "battle_snapshot": battle.get_battle_snapshot(ctx.state),
                }
            )
            return pending, outcome, resolution

        # An enemy's turn
        consecutive_enemy_turns += 1
        actor_name = ctx.entry_name('enemies', actor_id)
        battle.clear_defending(ctx.state, 'enemies', actor_id)

        raw = generate_enemy_turn(
            ctx.details_of('enemies', actor_id),
            build_side_details(ctx.monsters, ctx.state.get('allies', {}), 'allies'),
            build_side_details(ctx.monsters, ctx.state.get('enemies', {}), 'enemies'),
            ctx.state,
            ctx.workflow_name,
        )
        action = str(raw.get('action', 'attack')).strip().lower()
        if action not in ('attack', 'ability', 'defend', 'talk', 'flee'):
            action = 'attack'

        if action == 'talk':
            dialogue = str(raw.get('dialogue') or '').strip()
            if dialogue:
                ctx.state['pending_talk'] = {'speaker_id': actor_id, 'dialogue': dialogue}
                ctx.state['phase'] = 'awaiting_player_response'
                battle.record_turn(ctx.state, actor_name, 'talk', actor_id=actor_id, side='enemies')
                battle.save_battle_state(ctx.state)
                # The whole party hears an enemy reaching for words
                journal.append_party_journal(
                    f'Enemy {actor_name} spoke to the party mid-battle: "{dialogue[:90]}"'
                )
                pending = success_response(
                    {
                        "pending": "player_response",
                        "pending_talk": {"speaker_name": actor_name, "dialogue": dialogue},
                        "battle_snapshot": battle.get_battle_snapshot(ctx.state),
                    }
                )
                return pending, outcome, resolution
            action = 'attack'  # talk without words - degrade

        if action == 'flee':
            battle.mark_fled(ctx.state, actor_id)
            narration = f"{actor_name} breaks away from the fight and vanishes into the shadows of {ctx.location.get('name', 'the dungeon')}."
            battle.append_log(ctx.state, narration)
            battle.record_turn(ctx.state, actor_name, 'flee', actor_id=actor_id, side='enemies')
            battle.save_battle_state(ctx.state)
            ctx.emit_turn(
                {
                    'narration': narration,
                    'actor_name': actor_name,
                    'action': 'flee',
                    'ability_name': None,
                    'target_name': None,
                    'impact': 'none',
                    'target_condition': None,
                    'dialogue': None,
                }
            )
        else:
            ability = None
            if action == 'ability':
                monster = ctx.monsters.get(actor_id)
                wanted = str(raw.get('ability_name') or '').strip().lower()
                ability = next(
                    (
                        a
                        for a in (monster.abilities if monster else [])
                        if a.name.strip().lower() == wanted
                    ),
                    None,
                )
                if not ability:
                    action = 'attack'

            target_side, target_id = (None, None)
            if action != 'defend':
                target_side, target_id = ctx.find_by_name(raw.get('target'))
                if not target_id or (target_side == 'enemies' and action == 'attack'):
                    living = battle.active_ids(ctx.state, 'allies')
                    if not living:
                        break
                    target_side, target_id = 'allies', random.choice(living)

            resolve_combat_turn(ctx, 'enemies', actor_id, action, ability, target_side, target_id)

        outcome = battle.derive_outcome(ctx.state)
        if outcome != 'unresolved':
            resolution = 'combat'

    return None, outcome, resolution
