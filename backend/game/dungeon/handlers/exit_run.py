# The exit path - walking out alive: growth ceremony, run close, leaving

from typing import Any

from backend.core.utils.responses import success_response
from backend.core.workflow_steps import WorkflowStep


def run_exit(step: WorkflowStep, workflow_name: str) -> dict[str, Any]:
    """Play out the exit path: exit text, ceremony, close the run, leave"""
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
    except Exception as ceremony_error:
        print(f"❌ Exit ceremony failed (the exit itself stands): {ceremony_error}")
    step.data.update({"growth": growth_results})

    # Close this run's row in the history while the run state
    # still exists (exit_dungeon wipes it), and preserve the run's
    # log for conversations back home
    step.emit("close_run")
    from backend.models.dungeon_run import DungeonRun

    log_entries = manager.get_dungeon_log_entries()
    manager.snapshot_last_run_log('victory_exit')
    DungeonRun.close('victory_exit', summary=log_entries[-1] if log_entries else None)

    step.emit("exit_dungeon")
    manager.exit_dungeon()

    return success_response({"exited": True, "exit_text": exit_text, "growth": growth_results})
