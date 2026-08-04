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


def main() -> int:
    failures = 0
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
