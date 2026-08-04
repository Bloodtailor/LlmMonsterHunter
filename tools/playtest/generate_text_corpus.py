# Corpora for the text nobody has ever counted: ITEMS and CHRONICLES.
#
# The monster corpus (generate_corpus.py) is expensive because monsters
# ARE expensive - six staged calls each. Items and chronicles are one
# call each, but they only exist inside a full run, and a live run costs
# ~40 calls to reach one chronicle. So this tool runs the game stubbed
# and lets exactly ONE family of templates through to the real provider
# (ScriptedStub's passthrough): a 30-chronicle corpus costs ~30 real
# calls instead of ~1,200, and every chronicle is still composed from a
# REAL run's real log by the real prompt.
#
#   PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe tools/playtest/generate_text_corpus.py --chronicles 30
#   ... --items 40
#   ... --chronicles 5 --dry-run     # fully stubbed rehearsal, zero cost
#
# Output: playtest_results/text_corpus_<stamp>.jsonl, analyzed by
# analyze_text_corpus.py.

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
from tools.playtest.rig import (
    build_rig,
    drain_queue,
    refresh_session,
    require_cloud_provider,
    run_workflow,
)
from tools.playtest.scripted_stub import ForcedEvents, ScriptedStub
from tools.playtest.world_setup import build_world

# What each corpus kind lets through to the real model
PASSTHROUGH = {
    'chronicle': ('run_chronicle',),
    'item': ('treasure_item', 'reward_item'),
}


def harvest_chronicle(queue, rng) -> dict:
    """One full stubbed run whose CHRONICLE is real: walk a couple of
    locations so the log has something to condense, then exit alive."""
    from backend.game.dungeon import manager as dungeon

    run_workflow(queue, 'generate_expedition_notices', {})
    status = run_workflow(queue, 'enter_dungeon', {})
    if status['status'] != 'completed':
        return {'kind': 'chronicle_failure', 'error': str(status.get('error'))}

    with ForcedEvents(event='location_explore', monsters_present=False, include_exit=False):
        for _ in range(2):
            state = dungeon.get_dungeon_state()
            walk = [
                pid
                for pid, p in (state.get('available_paths') or {}).items()
                if p.get('type') != 'exit'
            ]
            if walk:
                run_workflow(queue, 'choose_path', {'path_id': rng.choice(walk)})
            run_workflow(queue, 'continue_exploring', {})

    with ForcedEvents(event='location_explore', monsters_present=False, include_exit=True):
        for _ in range(4):
            state = dungeon.get_dungeon_state()
            exits = [
                pid
                for pid, p in (state.get('available_paths') or {}).items()
                if p.get('type') == 'exit'
            ]
            if exits:
                status = run_workflow(queue, 'choose_path', {'path_id': exits[0]})
                result = status.get('result') or {}
                return {
                    'kind': 'chronicle',
                    'text': result.get('chronicle') or '',
                    'run_number': result.get('run_number'),
                    'goal': (result.get('goal') or {}).get('text'),
                }
            run_workflow(queue, 'continue_exploring', {})
    return {'kind': 'chronicle_failure', 'error': 'never found an exit'}


def harvest_items(queue, rng, wanted: int) -> list:
    """Stubbed runs whose TREASURE items are real - one item per
    treasure path, which is one real call each"""
    from backend.game.dungeon import manager as dungeon

    harvested = []
    if not dungeon.is_in_dungeon():
        run_workflow(queue, 'generate_expedition_notices', {})
        run_workflow(queue, 'enter_dungeon', {})

    # Every junction is regenerated INSIDE the pin: arriving retires the
    # previous location's paths, and paths rolled outside the pin carry
    # random events (which is how a first attempt harvested one treasure
    # and fifteen shrugs)
    while len(harvested) < wanted:
        with ForcedEvents(event='treasure', include_exit=False):
            state = dungeon.get_dungeon_state()
            walk = [
                pid
                for pid, p in (state.get('available_paths') or {}).items()
                if p.get('type') != 'exit'
            ]
            if not walk:
                run_workflow(queue, 'continue_exploring', {})
                continue
            status = run_workflow(queue, 'choose_path', {'path_id': rng.choice(walk)})
        result = status.get('result') or {}
        item = result.get('item')
        if item:
            harvested.append(
                {
                    'kind': 'item',
                    'name': item.get('name'),
                    'description': item.get('description'),
                    'emoji': item.get('emoji'),
                    'source': 'treasure',
                }
            )
        else:
            harvested.append({'kind': 'item_failure', 'error': str(status.get('error'))})
    return harvested


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chronicles', type=int, default=0)
    parser.add_argument('--items', type=int, default=0)
    parser.add_argument('--seed', type=int, default=2026)
    parser.add_argument('--dry-run', action='store_true', help='stub everything (zero cost)')
    parser.add_argument('--out', default=None)
    args = parser.parse_args()

    if not args.chronicles and not args.items:
        print('Nothing to harvest - pass --chronicles N and/or --items N')
        return 1

    results_dir = REPO_ROOT / 'playtest_results'
    results_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = Path(args.out) if args.out else results_dir / f'text_corpus_{stamp}.jsonl'

    passthrough = ()
    if not args.dry_run:
        passthrough = tuple(
            name
            for kind, names in PASSTHROUGH.items()
            for name in names
            if (kind == 'chronicle' and args.chronicles) or (kind == 'item' and args.items)
        )

    app, queue = build_rig()
    with app.app_context():
        from backend.models.core import create_tables
        from backend.models.llm_log import LLMLog

        create_tables()
        if not args.dry_run and not require_cloud_provider():
            return 1
        calls_before = LLMLog.query.count()

        stub = ScriptedStub(seed=args.seed, mode='happy', passthrough=passthrough)
        stub.install()
        rng = random.Random(args.seed)
        random.seed(args.seed)
        started = time.time()
        rows = []

        print(
            f"📚 TEXT CORPUS - {args.chronicles} chronicles, {args.items} items "
            f"({'DRY RUN, stubbed' if args.dry_run else 'real: ' + ', '.join(passthrough)})"
        )

        try:
            with out_path.open('a', encoding='utf-8') as out_file:

                def write(row: dict):
                    out_file.write(json.dumps(row, default=str) + '\n')
                    out_file.flush()
                    rows.append(row)

                for index in range(args.chronicles):
                    build_world(rng)
                    row = harvest_chronicle(queue, rng)
                    write(row)
                    print(f"  📜 chronicle {index + 1}/{args.chronicles}: {row['kind']}")

                if args.items:
                    build_world(rng)
                    for row in harvest_items(queue, rng, args.items):
                        write(row)
                    print(f"  🗝️ {args.items} items harvested")
        finally:
            drain_queue(queue, timeout_seconds=120)
            stub.uninstall()

        refresh_session()
        spent = LLMLog.query.count() - calls_before
        print('\n' + '=' * 50)
        print(
            f"rows={len(rows)} real_llm_calls={spent} "
            f"passthrough_hits={stub.passthrough_calls} ({(time.time() - started) / 60:.1f} min)"
        )
        print(f'corpus: {out_path}')
        print(
            'Analyze with: PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe '
            f'tools/playtest/analyze_text_corpus.py {out_path}'
        )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
