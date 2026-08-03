# Headless crash driver - hundreds of full dungeon runs, stubbed LLM,
# zero cost. Hunts Problem A: crashes, softlocks, dead ends, wedged
# states. Drives the REAL workflow queue (request_workflow + poll), so
# sequencing, queued log-condense housekeeping, and the queue's
# failure handling all behave exactly as in the running game - just with
# the model's answers fabricated by stub_llm.py.
#
# Usage (from repo root):
#   ./venv/Scripts/python.exe tools/playtest/crash_driver.py --runs 100
#   ./venv/Scripts/python.exe tools/playtest/crash_driver.py --runs 30 --mode broken
#
# Modes: happy (golden path), broken (every fallback), chaos (garbage
# shapes), mixed (rotate per run - the default). Failures land in
# playtest_results/crash_driver_<stamp>.jsonl with repro context.

import argparse
import json
import random
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import backend  # noqa: F401 - loads .env
from tools.playtest.invariants import check_all
from tools.playtest.stub_llm import StubLLM
from tools.playtest.world_setup import build_world, grant_starter_item

WORKFLOW_WAIT_SECONDS = 120
PARTY_LINES = (
    'We mean no harm - we only pass through.',
    'What do you guard here?',
    'We seek the heart of this place. Stand aside or walk with us.',
    'Easy now. No one needs to get hurt.',
)


class RunAbort(Exception):
    """A run cannot continue (workflow lost, queue refused, etc.)"""


def _refresh_session():
    """End the driver's read transaction so the next query sees the
    worker thread's commits. The running game never needs this - each
    HTTP request gets a fresh session - but this driver holds one app
    context all night, and MySQL's REPEATABLE READ would otherwise pin
    every read to the first snapshot."""
    from backend.models.core import db

    db.session.rollback()


def run_workflow(queue, workflow_type: str, context: dict) -> dict:
    """Submit through the production gateway and wait for a terminal status"""
    from backend.workflow.workflow_gateway import request_workflow

    success, workflow_id = request_workflow(workflow_type, context=context)
    if not success:
        raise RunAbort(f"queue refused {workflow_type}")

    started = time.time()
    while time.time() - started < WORKFLOW_WAIT_SECONDS:
        status = queue.get_workflow_status(workflow_id)
        if status and status['status'] in ('completed', 'failed'):
            _refresh_session()
            return status
        time.sleep(0.05)
    raise RunAbort(f"{workflow_type} never finished (workflow_id={workflow_id})")


def drain_queue(queue, timeout_seconds: int = 60):
    """Wait out queued housekeeping (log condense) before swapping stubs"""
    started = time.time()
    while time.time() - started < timeout_seconds:
        counts = queue.get_queue_status().get('status_counts', {})
        if not counts.get('pending') and not counts.get('processing'):
            return
        time.sleep(0.05)


def battle_action(rng: random.Random, state: dict) -> dict:
    """A plausible player input for the current battle phase"""
    phase = state.get('phase')
    if phase == 'awaiting_player_response':
        return {'player_response': rng.choice(PARTY_LINES)}
    if phase != 'awaiting_player_turn':
        return {}  # 'ready' - opening initiative

    actor_id = str(state.get('pending_actor'))
    enemies = [eid for eid, e in (state.get('enemies') or {}).items() if not (e or {}).get('fled')]
    target_id = rng.choice(enemies) if enemies else None
    action_type = rng.choices(
        ['attack', 'defend', 'ability', 'custom', 'talk', 'item'],
        [0.5, 0.1, 0.15, 0.1, 0.1, 0.05],
    )[0]

    action = {'type': action_type, 'target_id': target_id}
    if action_type == 'ability':
        ability_id = _first_ability_id(actor_id)
        if ability_id is None:
            action['type'] = 'attack'
        else:
            action['ability_id'] = ability_id
    elif action_type == 'custom':
        action['text'] = 'Kick dust into the air and lunge from the cloud!'
    elif action_type == 'talk':
        action['text'] = rng.choice(PARTY_LINES)
    elif action_type == 'item':
        item_id = _first_usable_item_id()
        if item_id is None:
            action['type'] = 'attack'
        else:
            action['item_id'] = item_id
    return {'player_action': action}


def _first_ability_id(monster_id: str):
    from backend.models.monster import Monster

    monster = Monster.get_monster_by_id(int(monster_id))
    abilities = monster.abilities if monster else []
    return abilities[0].id if abilities else None


def _first_usable_item_id():
    from backend.models.item import Item

    item = Item.query.filter(Item.uses_remaining > 0).first()
    return item.id if item else None


def dungeon_action(rng: random.Random, actions_left: int) -> tuple:
    """(workflow_type, context) for the current out-of-battle state"""
    from backend.game.dungeon import manager

    state = manager.get_dungeon_state()
    encounter = state.get('active_encounter') or {}
    event = encounter.get('event') if encounter else None

    if event == 'monster_dialogue':
        # Real players can walk away mid-conversation (the dialogue box
        # offers Continue Exploring) - and a broken LLM answers every
        # line with continue_dialogue, so a policy that never leaves
        # would talk forever
        dialogue_length = len(encounter.get('dialogue') or [])
        if dialogue_length > 8 or rng.random() < 0.15:
            return 'continue_exploring', {}
        return 'respond_to_monster', {'message': rng.choice(PARTY_LINES)}

    if event == 'location_explore' and encounter.get('monster_ids'):
        choice = rng.choices(['talk', 'sneak', 'ambush', 'press_on'], [0.35, 0.25, 0.25, 0.15])[0]
        if choice == 'talk':
            return 'respond_to_monster', {'message': rng.choice(PARTY_LINES)}
        if choice == 'sneak':
            return 'sneak_past', {}
        if choice == 'ambush':
            return 'surprise_attack', {}
        return 'continue_exploring', {}

    if event == 'location_explore' and not encounter.get('monster_ids'):
        if not encounter.get('camped') and rng.random() < 0.3:
            return 'setup_camp', {}
        item_id = _first_usable_item_id()
        if item_id is not None and rng.random() < 0.1:
            return 'use_dungeon_item', {'item_id': item_id, 'target': 'the strange carvings'}
        return _pick_path(rng, state, actions_left)

    return _pick_path(rng, state, actions_left)


def _pick_path(rng: random.Random, state: dict, actions_left: int) -> tuple:
    paths = state.get('available_paths') or {}
    if not paths:
        return 'continue_exploring', {}
    exit_ids = [pid for pid, p in paths.items() if p.get('type') == 'exit']
    # Low on budget, head for the exit when one is offered; otherwise
    # take it sometimes so exits get real coverage
    if exit_ids and (actions_left < 6 or rng.random() < 0.25):
        return 'choose_path', {'path_id': rng.choice(exit_ids)}
    walk_ids = [pid for pid in paths if pid not in exit_ids] or list(paths)
    return 'choose_path', {'path_id': rng.choice(walk_ids)}


def drive_one_run(queue, rng: random.Random, max_actions: int, record) -> dict:
    """One full expedition: notices -> enter -> act until exit or cap"""
    from backend.game.battle import manager as battle
    from backend.game.dungeon import manager

    stats = {'actions': 0, 'battles': 0, 'exited': False, 'workflow_failures': 0}

    status = run_workflow(queue, 'generate_expedition_notices', {})
    record('generate_expedition_notices', {}, status, stats)
    notices = (status.get('result') or {}).get('notices') or []
    notice = rng.choice(notices) if notices else None

    status = run_workflow(queue, 'enter_dungeon', {'notice': notice} if notice else {})
    record('enter_dungeon', {'notice': notice}, status, stats)
    if status['status'] == 'failed':
        return stats  # an unenterable dungeon is already recorded

    for action_index in range(max_actions):
        stats['actions'] = action_index + 1

        battle_state = battle.get_battle_state()
        battle_phase = battle_state.get('phase')
        if battle_state.get('in_battle') and battle_phase in (
            'ready',
            'awaiting_player_turn',
            'awaiting_player_response',
        ):
            if battle_phase == 'ready':
                stats['battles'] += 1
            workflow_type, context = 'battle_turn', battle_action(rng, battle_state)
        elif battle_state.get('in_battle') and battle_phase in ('victory', 'defeat'):
            # The battle ended - move on, exactly what the frontend's
            # continue button does (this is also what clears the battle)
            workflow_type, context = 'continue_exploring', {}
        else:
            workflow_type, context = dungeon_action(rng, max_actions - action_index)

        status = run_workflow(queue, workflow_type, context)
        record(workflow_type, context, status, stats)

        if not manager.is_in_dungeon():
            stats['exited'] = True
            break

    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=int, default=25)
    parser.add_argument('--max-actions', type=int, default=60)
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--mode', choices=['happy', 'broken', 'chaos', 'mixed'], default='mixed')
    args = parser.parse_args()

    seed = args.seed if args.seed is not None else random.randrange(1_000_000)
    rng = random.Random(seed)

    results_dir = REPO_ROOT / 'playtest_results'
    results_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    failures_path = results_dir / f'crash_driver_{stamp}.jsonl'
    failures_file = failures_path.open('w', encoding='utf-8')

    from backend.tests.harness import build_test_app

    app = build_test_app()

    from backend.ai.queue import get_ai_queue
    from backend.workflow.workflow_queue import get_queue

    get_ai_queue().set_flask_app(app)
    queue = get_queue()
    queue.set_flask_app(app)

    totals = {'runs': 0, 'exited': 0, 'hit_cap': 0, 'violations': 0, 'workflow_failures': 0}
    print(f"🧪 CRASH DRIVER - {args.runs} runs, mode={args.mode}, seed={seed}")
    print(f"   failures -> {failures_path}")
    started = time.time()

    with app.app_context():
        from backend.models.core import create_tables

        create_tables()

        for run_index in range(args.runs):
            run_mode = (
                args.mode if args.mode != 'mixed' else ['happy', 'broken', 'chaos'][run_index % 3]
            )
            stub = StubLLM(seed=seed + run_index, mode=run_mode)
            stub.install()
            try:
                build_world(rng)
                grant_starter_item(rng)

                def record(workflow_type, context, status, stats, _run=run_index, _mode=run_mode):
                    violations = check_all(after_workflow_status=status)
                    if status['status'] == 'failed':
                        stats['workflow_failures'] += 1
                        totals['workflow_failures'] += 1
                    if violations:
                        totals['violations'] += len(violations)
                        failures_file.write(
                            json.dumps(
                                {
                                    'run': _run,
                                    'mode': _mode,
                                    'seed': seed,
                                    'workflow': workflow_type,
                                    'context': context,
                                    'status': status.get('status'),
                                    'error': status.get('error'),
                                    'violations': violations,
                                },
                                default=str,
                            )
                            + '\n'
                        )
                        failures_file.flush()

                stats = drive_one_run(queue, rng, args.max_actions, record)
                totals['runs'] += 1
                totals['exited'] += 1 if stats['exited'] else 0
                totals['hit_cap'] += 0 if stats['exited'] else 1
                marker = '🏁' if stats['exited'] else '⏸️'
                print(
                    f"  {marker} run {run_index + 1}/{args.runs} [{run_mode}] "
                    f"actions={stats['actions']} battles={stats['battles']} "
                    f"failures={stats['workflow_failures']}"
                )
                if stub.unknown_templates:
                    print(f"     ⚠️ unknown templates: {sorted(stub.unknown_templates)}")
            except RunAbort as abort:
                totals['violations'] += 1
                failures_file.write(
                    json.dumps(
                        {'run': run_index, 'mode': run_mode, 'seed': seed, 'aborted': str(abort)}
                    )
                    + '\n'
                )
                failures_file.flush()
                print(f"  ❌ run {run_index + 1} aborted: {abort}")
            finally:
                drain_queue(queue)
                stub.uninstall()

    failures_file.close()
    elapsed = time.time() - started
    print('\n' + '=' * 50)
    print(
        f"runs={totals['runs']} exited={totals['exited']} hit_cap={totals['hit_cap']} "
        f"workflow_failures={totals['workflow_failures']} violations={totals['violations']} "
        f"({elapsed:.0f}s)"
    )
    print(f"failure log: {failures_path}")
    return 1 if totals['violations'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
