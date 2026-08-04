# Session scorer - objective numbers from a play.py transcript, so the
# model comparison (Pt-M3) rests on counts, not on what each model SAYS
# it did. Models under test overreport success; the transcript is the
# ground truth their reports get checked against.
#
# Usage: ./venv/Scripts/python.exe tools/playtest/score_session.py \
#            playtest_results/play_sessions/haiku_run1.jsonl [more.jsonl ...]

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


def score(path: Path) -> dict:
    entries = []
    with path.open(encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

    acts = [e for e in entries if e.get('workflow')]
    failed = [e for e in acts if e.get('workflow_status') == 'failed']
    battles = sum(1 for e in acts if e.get('workflow') == 'battle_turn')
    exited = any('outside the dungeon' in (e.get('status_text') or '') for e in entries[-3:])
    goal_done = any('Run goal (complete)' in (e.get('status_text') or '') for e in entries)

    # An "invalid action" is a workflow the game refused because the
    # command did not fit the current state (unknown path, nothing to
    # sneak past, battle not awaiting input...) - the model misread the
    # status text. Provider failures are not the model's fault and are
    # counted separately.
    def error_text(entry) -> str:
        return json.dumps(entry.get('workflow_error'), default=str).lower()

    invalid = [
        e
        for e in failed
        if any(
            marker in error_text(e)
            for marker in (
                'unknown path',
                'no monsters here',
                'not in a talking mood',
                'no place to camp',
                'cannot camp',
                'already camped',
                'not awaiting input',
                'no valid player action',
                'no player response',
                'not currently in a dungeon',
                'no such notice',
                'not in the party',
                'unknown player action',
            )
        )
    ]

    return {
        'session': path.stem,
        'commands': len(entries),
        'workflow_actions': len(acts),
        'workflow_failures': len(failed),
        'invalid_actions': len(invalid),
        'invalid_rate': round(len(invalid) / len(acts), 3) if acts else 0.0,
        'battle_turns': battles,
        'exited_alive': exited,
        'goal_fulfilled': goal_done,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Score play.py session transcripts')
    parser.add_argument('sessions', nargs='+')
    args = parser.parse_args()

    for session in args.sessions:
        path = Path(session)
        if not path.exists():
            print(f'No such transcript: {path}')
            continue
        row = score(path)
        print(json.dumps(row, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
