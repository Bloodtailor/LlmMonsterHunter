# Cost and latency, per caller and per template - reading data the game
# has been recording all along and nobody has ever read.
#
# Every generation writes a generation_logs row (prompt_type, prompt_name,
# duration_seconds, status) with an llm_logs child (exact prompt/response
# tokens, provider, model). That is a complete cost-and-latency ledger;
# this tool turns it into the two tables the roadmap actually needs:
#
#   BY CALLER    - what one player action costs in calls, tokens, seconds
#   BY TEMPLATE  - which prompt is the expensive one, and how often it
#                  fails to parse (a retry is a doubled bill)
#
# Prices are DeepSeek v4-pro list prices; --in-price/--out-price override
# them for another provider. Latency is wall time per generation, which
# on the serialized queue is what the player actually waits.
#
#   PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe tools/playtest/cost_report.py
#   ... --since 2026-08-03T19:00     # only this session's runs
#   ... --markdown playtest_results/cost_report.md

import argparse
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import backend  # noqa: F401 - loads .env

# DeepSeek v4-pro list prices, USD per 1M tokens (2026-08)
DEFAULT_INPUT_PRICE = 0.28
DEFAULT_OUTPUT_PRICE = 0.42


def collect(since: datetime = None) -> list:
    """One flat row per LLM generation: (workflow, prompt, tokens, seconds)"""
    from backend.models.generation_log import GenerationLog
    from backend.models.image_log import ImageLog  # noqa: F401 - mapper needs it
    from backend.models.llm_log import LLMLog  # noqa: F401 - mapper needs it

    query = GenerationLog.query.filter_by(generation_type='llm')
    if since:
        query = query.filter(GenerationLog.created_at >= since)

    rows = []
    for log in query.all():
        child = log.llm_log
        rows.append(
            {
                # Checked against real rows rather than assumed:
                # prompt_NAME holds the TEMPLATE (action_resolution,
                # monster_social_self) and prompt_TYPE holds the CALLER -
                # usually the workflow (battle_turn, choose_path), though
                # the monster generator labels its calls with its own
                # name. Reporting these the other way round would have
                # been a confident lie in a table of hard numbers.
                'caller': log.prompt_type or 'unknown',
                'template': log.prompt_name or 'unknown',
                'status': log.status,
                'seconds': float(log.duration_seconds or 0.0),
                'in_tokens': int(getattr(child, 'prompt_tokens', 0) or 0),
                'out_tokens': int(getattr(child, 'response_tokens', 0) or 0),
                'model': getattr(child, 'model_name', None) or 'unknown',
                'provider': getattr(child, 'provider', None) or 'unknown',
                # A generation that FAILED never produced text to parse,
                # so counting it as a parse failure double-counts one
                # problem and slanders the template: 17 'run_chronicle
                # parse failures' turned out to be one dead provider.
                'parse_ok': log.status == 'failed' or bool(getattr(child, 'parse_success', True)),
            }
        )
    return rows


def summarize(rows: list, key: str) -> list:
    """Aggregate rows by one key, worst-cost first"""
    buckets = defaultdict(
        lambda: {'calls': 0, 'in_tokens': 0, 'out_tokens': 0, 'seconds': 0.0, 'parse_fail': 0}
    )
    for row in rows:
        bucket = buckets[row[key]]
        bucket['calls'] += 1
        bucket['in_tokens'] += row['in_tokens']
        bucket['out_tokens'] += row['out_tokens']
        bucket['seconds'] += row['seconds']
        if not row['parse_ok']:
            bucket['parse_fail'] += 1

    summary = []
    for name, bucket in buckets.items():
        calls = bucket['calls'] or 1
        summary.append(
            {
                'name': name,
                'calls': bucket['calls'],
                'in_tokens': bucket['in_tokens'],
                'out_tokens': bucket['out_tokens'],
                'total_tokens': bucket['in_tokens'] + bucket['out_tokens'],
                'seconds': round(bucket['seconds'], 1),
                'avg_seconds': round(bucket['seconds'] / calls, 2),
                'avg_out_tokens': round(bucket['out_tokens'] / calls, 1),
                'parse_fail': bucket['parse_fail'],
                'parse_fail_rate': round(bucket['parse_fail'] / calls, 3),
            }
        )
    return sorted(summary, key=lambda entry: -entry['total_tokens'])


def cost_usd(in_tokens: int, out_tokens: int, in_price: float, out_price: float) -> float:
    return (in_tokens * in_price + out_tokens * out_price) / 1_000_000


def render(rows: list, in_price: float, out_price: float) -> str:
    if not rows:
        return "No LLM generations recorded in this window.\n"

    total_in = sum(r['in_tokens'] for r in rows)
    total_out = sum(r['out_tokens'] for r in rows)
    total_seconds = sum(r['seconds'] for r in rows)
    models = sorted({r['model'] for r in rows})
    failures = sum(1 for r in rows if r['status'] == 'failed')
    parse_failures = sum(1 for r in rows if not r['parse_ok'])

    lines = [
        '# Cost & latency report',
        '',
        f"- **{len(rows)} LLM calls** across {len(models)} model(s): {', '.join(models)}",
        f"- **{total_in:,} in + {total_out:,} out = {total_in + total_out:,} tokens**",
        f"- **${cost_usd(total_in, total_out, in_price, out_price):.4f}** at "
        f"${in_price}/M in, ${out_price}/M out",
        f"- **{total_seconds / 60:.1f} minutes** of generation wall time "
        f"({total_seconds / max(len(rows), 1):.1f}s per call average)",
        f"- {failures} failed generations, {parse_failures} parse failures",
        '',
        '## By caller — what one player action costs',
        '(the workflow that asked; monster generation labels its own calls)',
        '',
        '| caller | calls | tokens | $ | wall s | avg s/call |',
        '|---|---:|---:|---:|---:|---:|',
    ]
    for entry in summarize(rows, 'caller'):
        lines.append(
            f"| {entry['name']} | {entry['calls']} | {entry['total_tokens']:,} | "
            f"{cost_usd(entry['in_tokens'], entry['out_tokens'], in_price, out_price):.4f} | "
            f"{entry['seconds']} | {entry['avg_seconds']} |"
        )

    lines += [
        '',
        '## By template — where the tokens actually go',
        '',
        '| template | calls | tokens | avg out | avg s | parse fails |',
        '|---|---:|---:|---:|---:|---:|',
    ]
    for entry in summarize(rows, 'template'):
        lines.append(
            f"| {entry['name']} | {entry['calls']} | {entry['total_tokens']:,} | "
            f"{entry['avg_out_tokens']} | {entry['avg_seconds']} | "
            f"{entry['parse_fail']} ({entry['parse_fail_rate']:.0%}) |"
        )
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--since', default=None, help='ISO timestamp, e.g. 2026-08-03T19:00')
    parser.add_argument('--markdown', default=None, help='also write the report here')
    parser.add_argument('--in-price', type=float, default=DEFAULT_INPUT_PRICE)
    parser.add_argument('--out-price', type=float, default=DEFAULT_OUTPUT_PRICE)
    args = parser.parse_args()

    since = datetime.fromisoformat(args.since) if args.since else None

    from tools.playtest.rig import build_rig

    app, _ = build_rig()
    with app.app_context():
        rows = collect(since)
        report = render(rows, args.in_price, args.out_price)

    print(report)
    if args.markdown:
        Path(args.markdown).write_text(report, encoding='utf-8')
        print(f"wrote {args.markdown}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
