# Corpus generator - N real monsters + M real expedition notices, dumped
# as JSONL for variety analysis (Pt-M1). This is the baseline artifact
# the imagination engine will one day be measured against
# (docs/design/imagination-engine/01-why-generic-happens.md), so it uses
# the REAL generation chain against the real provider - no stubs, no
# themes, no run context: pure cold-start generation, which is exactly
# the disease being measured.
#
# Costs real DeepSeek calls (~6 per monster with one ability, ~1 per 3
# notices). The --max-llm-calls guard stops generation before the
# night's budget is at risk; progress is appended per monster, so an
# interrupted run keeps everything generated so far.
#
# Usage: ./venv/Scripts/python.exe tools/playtest/generate_corpus.py \
#            --monsters 150 --notices 60

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import backend  # noqa: F401 - loads .env
from tools.playtest.rig import build_rig, drain_queue, run_workflow


def llm_call_count() -> int:
    from backend.models.llm_log import LLMLog

    return LLMLog.query.count()


def dump_monster(monster, ability_names: list) -> dict:
    """Everything the variety analysis needs, flat and readable"""
    persona = monster.persona or {}
    appearance = monster.appearance or {}
    ecology = monster.ecology or {}
    taxonomy = monster.taxonomy or {}
    return {
        'kind': 'monster',
        'id': monster.id,
        'name': monster.name,
        'species': monster.species,
        'rarity': monster.rarity,
        'party_role': monster.party_role,
        'taxonomy': taxonomy,
        'ecology': ecology,
        'personality_traits': monster.personality_traits or [],
        'persona': persona,
        'description': monster.description,
        'backstory': monster.backstory,
        'appearance': appearance,
        'abilities': ability_names,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate the variety-baseline corpus')
    parser.add_argument('--monsters', type=int, default=150)
    parser.add_argument('--notices', type=int, default=60)
    parser.add_argument('--abilities-per-monster', type=int, default=1)
    parser.add_argument('--max-llm-calls', type=int, default=1600)
    parser.add_argument('--out', default=None, help='output JSONL (default: timestamped)')
    args = parser.parse_args()

    results_dir = REPO_ROOT / 'playtest_results'
    results_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_path = Path(args.out) if args.out else results_dir / f'corpus_{stamp}.jsonl'

    app, workflow_queue = build_rig()

    with app.app_context():
        from backend.ai.llm.provider_settings import resolve_llm_settings
        from backend.models.core import create_tables

        create_tables()

        settings = resolve_llm_settings()
        if settings['provider'] != 'deepseek':
            print(
                "❌ Provider resolves to 'local' - run tools/playtest/seed_provider.py "
                "first (the corpus must come from the real generator)."
            )
            return 1

        calls_at_start = llm_call_count()
        print(
            f"🧪 CORPUS GENERATION - {args.monsters} monsters, {args.notices} notices "
            f"({settings['model_name']}) -> {out_path}"
        )
        started = time.time()
        generated = {'monsters': 0, 'notices': 0, 'failures': 0}

        def calls_spent() -> int:
            from tools.playtest.rig import refresh_session

            refresh_session()
            return llm_call_count() - calls_at_start

        with out_path.open('a', encoding='utf-8') as out_file:

            def write_row(row: dict):
                out_file.write(json.dumps(row, default=str) + '\n')
                out_file.flush()

            # ===== monsters: the real staged chain, cold start each =====
            from backend.game.monster.generator import (
                generate_ability,
                generate_base_monster,
            )

            for index in range(args.monsters):
                if calls_spent() >= args.max_llm_calls:
                    print(f"🛑 Budget guard: {calls_spent()} calls - stopping early.")
                    break
                try:
                    monster = generate_base_monster()
                    ability_names = []
                    for _ in range(args.abilities_per_monster):
                        try:
                            ability = generate_ability(monster)
                            ability_names.append(
                                {'name': ability.name, 'description': ability.description}
                            )
                        except Exception as ability_error:
                            print(f"  ⚠️ ability failed: {ability_error}")
                    write_row(dump_monster(monster, ability_names))
                    generated['monsters'] += 1
                    if (index + 1) % 10 == 0:
                        rate = (time.time() - started) / (index + 1)
                        print(
                            f"  🐲 {index + 1}/{args.monsters} monsters "
                            f"({calls_spent()} calls, {rate:.0f}s each)"
                        )
                except Exception as monster_error:
                    generated['failures'] += 1
                    write_row({'kind': 'monster_failure', 'error': str(monster_error)})
                    print(f"  ❌ monster {index + 1} failed: {monster_error}")

            # ===== notices: the real workflow, board cleared between =====
            from backend.game.dungeon.run_context import clear_pending_notices

            while generated['notices'] < args.notices:
                if calls_spent() >= args.max_llm_calls:
                    print(f"🛑 Budget guard: {calls_spent()} calls - stopping early.")
                    break
                try:
                    status = run_workflow(workflow_queue, 'generate_expedition_notices', {})
                    board = (status.get('result') or {}).get('notices') or []
                    for notice in board:
                        write_row({'kind': 'notice', **notice})
                    generated['notices'] += len(board)
                    clear_pending_notices()
                    print(f"  📜 {generated['notices']}/{args.notices} notices")
                except Exception as notice_error:
                    generated['failures'] += 1
                    write_row({'kind': 'notice_failure', 'error': str(notice_error)})
                    print(f"  ❌ notice batch failed: {notice_error}")

        drain_queue(workflow_queue)
        elapsed = time.time() - started
        print('\n' + '=' * 50)
        print(
            f"monsters={generated['monsters']} notices={generated['notices']} "
            f"failures={generated['failures']} llm_calls={calls_spent()} "
            f"({elapsed / 60:.1f} min)"
        )
        print(f'corpus: {out_path}')
        print(
            f'Analyze with: ./venv/Scripts/python.exe tools/playtest/analyze_corpus.py {out_path}'
        )

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
