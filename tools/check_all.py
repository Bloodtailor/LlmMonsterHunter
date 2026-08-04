#!/usr/bin/env python3
"""Run every check CI runs, in one command, before pushing.

    ./venv/Scripts/python.exe tools/check_all.py            # everything
    ./venv/Scripts/python.exe tools/check_all.py backend    # skip npm
    ./venv/Scripts/python.exe tools/check_all.py frontend   # only npm

`.github/workflows/ci.yml` runs exactly these checks, so a green run
here means a green PR. This script is a local convenience only - CI does
not call it, so the workflow stays the source of truth for what must pass.
If you add a step to the workflow, add it here too.

Every check runs even after one fails, so a single pass shows everything
that needs fixing. Two of them have a fix mode worth knowing:

    python -m ruff format backend setup tools    # fixes 'format'
    npx prettier --write src                     # fixes 'prettier' (in frontend/)

MySQL must be running for the offline suites.
"""

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Emoji output survives Windows consoles that default to cp1252
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = REPO_ROOT / 'frontend'

# sys.executable is whichever interpreter is running this script, so the
# checks use the same venv the caller used - no hardcoded venv path
PYTHON = sys.executable


def backend_checks():
    return [
        ('lint', [PYTHON, '-m', 'ruff', 'check', 'backend', 'setup', 'tools'], REPO_ROOT),
        (
            'format',
            [PYTHON, '-m', 'ruff', 'format', '--check', 'backend', 'setup', 'tools'],
            REPO_ROOT,
        ),
        ('file sizes', [PYTHON, 'tools/check_file_sizes.py'], REPO_ROOT),
        ('offline suites', [PYTHON, '-m', 'pytest'], REPO_ROOT),
        # The playtest gauntlets drive the real workflow queue with the
        # LLM stubbed - they catch regressions in promises no unit test
        # reaches (softlock valve, defeat stakes, evolution identity)
        ('playtest gauntlets', [PYTHON, 'tools/playtest/run_gauntlets.py'], REPO_ROOT),
    ]


def frontend_checks():
    # npm ships as npm.cmd / npx.cmd on Windows; which() resolves either
    npx = shutil.which('npx')
    npm = shutil.which('npm')
    if not npx or not npm:
        return None
    return [
        ('prettier', [npx, 'prettier', '--check', 'src'], FRONTEND_DIR),
        (
            'jest',
            [npm, 'test', '--', '--watchAll=false', '--passWithNoTests'],
            FRONTEND_DIR,
        ),
    ]


def run(name: str, command: list, cwd: Path) -> bool:
    """Run one check, print its verdict, return whether it passed"""
    started = time.monotonic()
    result = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        # CI sets both; pytest needs the encoding, jest needs CI=true to
        # run once instead of entering watch mode
        env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'CI': 'true'},
    )
    elapsed = time.monotonic() - started

    if result.returncode == 0:
        print(f"  ✅ {name} ({elapsed:.1f}s)")
        return True

    print(f"  ❌ {name} ({elapsed:.1f}s)")
    output = (result.stdout or '') + (result.stderr or '')
    for line in output.strip().splitlines():
        print(f"       {line}")
    return False


def main():
    requested = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if requested not in ('all', 'backend', 'frontend'):
        print(f"Unknown argument {requested!r} - expected 'backend', 'frontend', or nothing")
        return 2

    checks = []
    if requested in ('all', 'backend'):
        checks += backend_checks()
    if requested in ('all', 'frontend'):
        frontend = frontend_checks()
        if frontend is None:
            print('❌ npm/npx not found on PATH - cannot run the frontend checks')
            return 2
        checks += frontend

    print(f"🔍 RUNNING {len(checks)} CI CHECKS")
    print('=' * 50)

    failed = [name for name, command, cwd in checks if not run(name, command, cwd)]

    print('=' * 50)
    if failed:
        print(f"❌ {len(checks) - len(failed)} passed, {len(failed)} failed: {', '.join(failed)}")
        print('   Fix these before pushing - CI runs the same checks.')
        return 1

    print(f"🎉 all {len(checks)} checks passed - safe to push")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
