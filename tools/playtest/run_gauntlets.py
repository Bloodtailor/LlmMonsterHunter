# Every zero-cost playtest gauntlet, one command, for CI and for the
# pre-push check. The gauntlets assert promises no unit test can reach -
# that the softlock valve fires, that defeat forfeits the run's spoils,
# that evolution keeps a monster's identity - by driving the REAL
# workflow queue with the model stubbed. Each is seeded, so a failure
# here is a real regression, not a bad roll.
#
#   PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe tools/playtest/run_gauntlets.py
#
# Exit code is the total number of failed checks. Needs MySQL and the
# test database; costs nothing and takes about twenty seconds.

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

GAUNTLETS = ('battle_gauntlet.py', 'dungeon_gauntlet.py', 'life_gauntlet.py')


def check_stub_vocabulary_is_neutral() -> int:
    """The harness must never be able to answer its own question.

    Anything measured from a stubbed run inherits the stub's vocabulary,
    so a stub word that is also a variety WATCHWORD makes the metrics
    report the harness instead of the game. A chronicle corpus once read
    as 88% silence-obsessed because 'quiet' was in the stub's word pool.
    This is enumerable, so it is a tripwire rather than a comment.
    """
    import sys as _sys

    _sys.path.insert(0, str(REPO_ROOT))
    from tools.playtest.stub_answers import CREATURES, NOUNS, WORDS
    from tools.playtest.variety_metrics import SILENCE_WORDS, TROPE_PHRASES

    watchwords = set(SILENCE_WORDS) | {p for p in TROPE_PHRASES if ' ' not in p}
    collisions = sorted(set(WORDS + NOUNS + CREATURES) & watchwords)
    if collisions:
        print(f"  ❌ stub vocabulary collides with variety watchwords: {collisions}")
        print("       (stubbed corpora would measure the harness, not the game)")
        return 1
    print('  ✅ stub vocabulary is neutral (no watchword collisions)')
    return 0


def main() -> int:
    failures = check_stub_vocabulary_is_neutral()
    for gauntlet in GAUNTLETS:
        result = subprocess.run(
            [sys.executable, str(Path('tools/playtest') / gauntlet)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        failed_checks = result.returncode
        status = '✅' if failed_checks == 0 else '❌'
        print(f"  {status} {gauntlet} ({failed_checks} failed checks)")
        if failed_checks:
            failures += failed_checks
            # Only the failures matter here - the full PASS list lives in
            # the gauntlet's own output and its JSONL findings file
            for line in (result.stdout or '').splitlines():
                if 'FAIL' in line or 'failure log' in line:
                    print(f"       {line.strip()}")
            if result.stderr:
                print(f"       {result.stderr.strip()[:500]}")
    return failures


if __name__ == '__main__':
    raise SystemExit(main())
