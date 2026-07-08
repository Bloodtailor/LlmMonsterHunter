# The exit path - walking out alive: growth ceremony, the goal's reward
# ceremony, run close, leaving

from typing import Any

from backend.core.utils.responses import success_response
from backend.core.workflow_steps import WorkflowStep


def run_exit(step: WorkflowStep, workflow_name: str) -> dict[str, Any]:
    """Play out the exit path: exit text, ceremonies, close the run, leave"""
    from backend.game.dungeon import goal as run_goal
    from backend.game.dungeon import manager
    from backend.game.dungeon.generator import generate_exit_text
    from backend.game.state.manager import get_party_summary

    step.emit("generate_exit_text")
    exit_text = generate_exit_text(get_party_summary(), workflow_name)

    # The exit ceremony: walking out alive, EVERY member reflects
    # on the whole run and grows from what the journal shows.
    # A failure here never blocks the exit itself.
    step.emit("exit_ceremony")
    growth_results = []
    try:
        from backend.game.memory import growth
        from backend.game.memory.manager import write_memory
        from backend.game.state.manager import get_party_monster_ids
        from backend.models.monster import Monster

        for monster_id in get_party_monster_ids():
            monster = Monster.get_monster_by_id(monster_id)
            if not monster:
                continue
            step.data.update({"growing": monster.name})
            step.emit_again()
            reflection = growth.run_growth_reflection(monster, 'exit', workflow_name)
            if reflection:
                growth_results.append(growth.apply_growth(monster, reflection))
            write_memory(
                monster.id,
                'run_complete',
                "Walked out of the dungeon alive with the party, carrying "
                "everything the run had made of it.",
            )
            # Surviving a run together deepens the bond one step
            from backend.game.monster.affinity import step_affinity

            step_affinity(monster.id, 'survived_run_together')
    except Exception as ceremony_error:
        print(f"❌ Exit ceremony failed (the exit itself stands): {ceremony_error}")
    step.data.update({"growth": growth_results})

    # THE GOAL'S REWARD CEREMONY: a fulfilled goal pays out at the exit -
    # one rare themed item + a bonus 'notable' growth step for the party.
    # Walking out is what makes it real (defeat forfeits everything).
    # A failure here never blocks the exit itself.
    goal_state = run_goal.goal_snapshot()
    goal_reward = None
    if goal_state and goal_state.get('status') == 'complete':
        step.emit("goal_reward_ceremony")
        try:
            import random as _random

            from backend.game.inventory.generator import generate_goal_reward_item
            from backend.game.memory import growth as growth_module
            from backend.game.state.manager import get_party_monster_ids
            from backend.models.monster import Monster

            reward_item = generate_goal_reward_item(
                goal_state['text'], goal_state.get('progress_notes', [])
            )

            # Bonus growth is CODE-owned: one 'notable' step to a random
            # stat per member (apply_growth still enforces every cap)
            bonus_growth = []
            for monster_id in get_party_monster_ids():
                monster = Monster.get_monster_by_id(monster_id)
                if not monster:
                    continue
                bonus_growth.append(
                    growth_module.apply_growth(
                        monster,
                        {
                            'reflection': f"Fulfilled the run's goal: {goal_state['text']}",
                            'stat': _random.choice(list(growth_module.GROWTH_STAT_WORDS)),
                            'tier': 'notable',
                            'memory_note': (
                                f"Fulfilled a run's goal with the party: {goal_state['text'][:150]}"
                            ),
                        },
                    )
                )

            goal_reward = {'item': reward_item.to_dict(), 'growth': bonus_growth}
            manager.append_dungeon_log(f"The fulfilled goal earned its reward: {reward_item.name}.")
        except Exception as reward_error:
            print(f"❌ Goal reward ceremony failed (the exit stands): {reward_error}")
    step.data.update({"goal_reward": goal_reward})

    # Walking out alive is what completes the guided first run - the
    # title screen's Continue button unlocks from here on
    from backend.game.dungeon.first_run import complete_first_run_if_active

    complete_first_run_if_active()

    # THE CHRONICLE: the whole run condensed into its story beat, streamed
    # to the player and stamped into the run's history row. Composed from
    # live state, so it queues BEFORE the wipes; a failure never blocks
    # the exit (the old one-line summary steps in).
    step.emit("queue_chronicle")
    from backend.game.dungeon import chronicle

    queued_chronicle = chronicle.queue_run_chronicle('victory', workflow_name)
    if queued_chronicle:
        step.data.update({"chronicle_text_generation_id": queued_chronicle['generation_id']})
        step.emit("emit_generation_id")
    chronicle_text = chronicle.await_run_chronicle(queued_chronicle)

    # Close this run's row in the history while the run state
    # still exists (exit_dungeon wipes it), and preserve the run's
    # log for conversations back home
    step.emit("close_run")
    from backend.models.dungeon_run import DungeonRun

    log_entries = manager.get_dungeon_log_entries()
    manager.snapshot_last_run_log('victory_exit')
    DungeonRun.close(
        'victory_exit',
        summary=chronicle_text or (log_entries[-1] if log_entries else None),
    )

    step.emit("exit_dungeon")
    manager.exit_dungeon()

    return success_response(
        {
            "exited": True,
            "exit_text": exit_text,
            "growth": growth_results,
            "goal": goal_state,
            "goal_reward": goal_reward,
            "chronicle": chronicle_text,
            "run_number": (queued_chronicle or {}).get('run_number'),
        }
    )
