# The battle's ending - outcome narration, carrying damage and spent
# reserves back into the run, the dungeon-log summary, what every enemy
# will remember, the victory keepsake, and the full defeat sequence.

from typing import Any

from backend.core.utils.responses import success_response

from .context import TurnContext


def finish_battle(ctx: TurnContext, outcome, resolution, joined_names) -> dict[str, Any]:
    """Everything after the last blow: narrate, persist, remember, mint"""
    from backend.game.battle import manager as battle
    from backend.game.battle.generator import (
        build_side_details,
        generate_battle_outcome_text,
        generate_battle_summary,
    )
    from backend.game.dungeon import manager as dungeon
    from backend.game.memory import journal
    from backend.game.memory import manager as memory
    from backend.game.state.manager import get_party_details

    state = ctx.state

    ctx.step.emit("determine_outcome")

    if outcome not in ('victory', 'defeat'):
        raise Exception("Battle advance loop ended without an outcome")

    resolution = resolution or 'combat'
    outcome_text = generate_battle_outcome_text(
        outcome,
        resolution,
        ctx.location,
        get_party_details(),
        build_side_details(ctx.monsters, state.get('enemies', {}), 'enemies'),
        state,
        ctx.workflow_name,
    )

    # Battle damage persists in the run
    dungeon.set_party_conditions(
        {
            monster_id: entry.get('condition', 'fresh')
            for monster_id, entry in state.get('allies', {}).items()
        }
    )

    # So do spent reserves - they refill only on the next dungeon entry
    if dungeon.is_in_dungeon():
        dungeon.set_party_resources(
            {
                monster_id: {
                    'stamina': entry.get('stamina', 'brimming'),
                    'mana': entry.get('mana', 'brimming'),
                }
                for monster_id, entry in state.get('allies', {}).items()
            }
        )

    # The dungeon log gets a summary of the battle - the detailed
    # blow-by-blow stays in the battle's own log. The LLM writes the
    # story (including lasting effects like lingering debuffs); a
    # deterministic line covers the mechanical truth either way.
    summary = None
    if dungeon.is_in_dungeon():
        ctx.step.emit("summarize_battle")

        enemy_names = ', '.join(
            entry.get('name', 'Unknown') for entry in state.get('enemies', {}).values()
        )
        ally_summary = ', '.join(
            f"{entry.get('name')}: {entry.get('condition')}"
            for entry in state.get('allies', {}).values()
        )

        summary = generate_battle_summary(
            outcome,
            resolution,
            joined_names,
            ctx.location,
            build_side_details(ctx.monsters, state.get('allies', {}), 'allies'),
            build_side_details(ctx.monsters, state.get('enemies', {}), 'enemies'),
            state,
            ctx.workflow_name,
        )
        if not summary:
            summary = f"A battle against {enemy_names} ended in {outcome} ({resolution})."
            if joined_names:
                summary += f" {', '.join(joined_names)} joined the party."

        dungeon.append_dungeon_log(f"{summary} Party condition afterward: {ally_summary}.")

        # A finished battle is a goal-check moment (won OR survived -
        # "drive out what haunts the deep halls" can complete here)
        if outcome == 'victory':
            from backend.game.dungeon import goal

            goal.check_goal_progress(ctx.workflow_name)

    # ===== WHAT THE MONSTERS WILL REMEMBER =====
    # Written BEFORE any defeat cleanup wipes the run state. A failed
    # memory must never break the battle result.
    ctx.step.emit("write_battle_memories")
    try:
        location_name = ctx.location.get('name', 'the dungeon')
        party_names = (
            ', '.join(entry.get('name', 'Unknown') for entry in state.get('allies', {}).values())
            or 'the party'
        )
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
                    int(monster_id),
                    'fled_from_party',
                    f"Fled from a battle against the party ({party_names}) at {location_name}.",
                    dict(memory_details),
                )

            elif name_joined:
                memory.write_memory(
                    int(monster_id),
                    'joined_party',
                    f"Chose to join the party ({party_names}) after words won out mid-battle at {location_name}.",
                    dict(memory_details),
                )

            elif resolution == 'yielded':
                memory.write_memory(
                    int(monster_id),
                    'yielded_to_party',
                    f"Yielded to the party ({party_names}) at {location_name} rather than fight to the end.",
                    dict(memory_details),
                )

            elif outcome == 'defeat':
                if resolution == 'spared':
                    memory.write_memory(
                        int(monster_id),
                        'spared_party',
                        f"Defeated the party ({party_names}) at {location_name} and granted their plea for mercy.",
                        dict(memory_details),
                    )
                else:
                    fallen = ', '.join(
                        e.get('name', 'Unknown')
                        for e in state.get('allies', {}).values()
                        if e.get('condition') == 'incapacitated'
                    )
                    details = dict(memory_details)
                    details['party_fallen'] = fallen
                    memory.write_memory(
                        int(monster_id),
                        'defeated_party',
                        f"Stood victorious over the party ({party_names}) at {location_name}.",
                        details,
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
        ctx.step.emit("mint_victory_cocatok")
        from backend.game.inventory.generator import generate_victory_cocatok

        defeated_names = [
            entry.get('name', 'Unknown')
            for entry in state.get('enemies', {}).values()
            if entry.get('name') not in joined_names
        ]
        battle_story = (
            summary
            if dungeon.is_in_dungeon()
            else (
                f"A battle against {', '.join(defeated_names) or 'fearsome foes'} "
                f"ended in victory ({resolution})."
            )
        )
        cocatok = generate_victory_cocatok(ctx.location, battle_story, defeated_names)
        cocatok_data = cocatok.to_dict()
        ctx.step.data.update({"cocatok": cocatok_data})

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
            ctx.step.emit("defeat_reflection")
            try:
                from backend.game.memory import growth

                party_monsters = [ctx.monsters.get(mid) for mid in state.get('allies', {})]
                defeat_reflection = growth.run_defeat_reflection(
                    [m for m in party_monsters if m], state, ctx.workflow_name
                )
            except Exception as lesson_error:
                print(f"❌ Defeat lesson failed (the defeat stands): {lesson_error}")

            from backend.models.dungeon_run import DungeonRun

            dungeon.snapshot_last_run_log('defeat')
            DungeonRun.close('defeat', summary=summary)
        battle.end_battle()
        dungeon.exit_dungeon()

    return success_response(
        {
            "outcome": outcome,
            "resolution": resolution,
            "joined_names": joined_names,
            "outcome_text": outcome_text,
            "cocatok": cocatok_data,
            "defeat_reflection": defeat_reflection,
            "battle_snapshot": battle.get_battle_snapshot(),
        }
    )
