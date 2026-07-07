#!/usr/bin/env python3
"""File-size ceiling check - no source file over 500 lines.

Big files hide big functions; the ceiling forces splits BEFORE a module
becomes a monolith. Run from the repo root (CI runs it on every push):

    python tools/check_file_sizes.py

Files that predate the rule are grandfathered below with their size at
the time. The list may only SHRINK: fix one under 500 (or split it) and
delete its line. Never add to it.
"""

import sys
from pathlib import Path

# Emoji output survives Windows consoles that default to cp1252
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

MAX_LINES = 500

SOURCE_GLOBS = (
    'backend/**/*.py',
    'setup/**/*.py',
    'tools/**/*.py',
    'frontend/src/**/*.js',
)

# path -> line count when grandfathered (a file may shrink, never grow)
GRANDFATHERED = {
    'backend/game/dungeon/generator.py': 685,
    'backend/game/monster/evolution.py': 556,
    'backend/tests/test_chat_and_summaries.py': 548,
    'backend/tests/test_evolution.py': 522,
    'setup/user_messages.py': 1092,
    # Dev/example screens, measured after prettier's one-time reformat
    'frontend/src/screens/developer/BYOComponentTestScreen.js': 1133,
    'frontend/src/screens/developer/ExplosionDemo.js': 801,
    'frontend/src/screens/developer/StyleTestScreen.js': 545,
    'frontend/src/components/UiExamples/TableExample.js': 808,
    'frontend/src/components/UiExamples/ExplosionExamples.js': 682,
    'frontend/src/components/UiExamples/ButtonExample.js': 663,
    'frontend/src/components/UiExamples/CardExamples.js': 603,
    'frontend/src/components/UiExamples/ExpandableTableExample.js': 592,
    'frontend/src/components/UiExamples/PaginationExample.js': 563,
    'frontend/src/components/UiExamples/FeedbackExamples.js': 536,
}


def count_lines(path: Path) -> int:
    with open(path, encoding='utf-8', errors='replace') as f:
        return sum(1 for _ in f)


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    failures = []
    stale_grandfathers = []

    for pattern in SOURCE_GLOBS:
        for path in sorted(root.glob(pattern)):
            rel = path.relative_to(root).as_posix()
            lines = count_lines(path)
            allowed = GRANDFATHERED.get(rel, MAX_LINES)
            if lines > allowed:
                failures.append((rel, lines, allowed))
            elif rel in GRANDFATHERED and lines <= MAX_LINES:
                stale_grandfathers.append(rel)

    for rel in stale_grandfathers:
        print(f'🎉 {rel} is under {MAX_LINES} lines - remove it from GRANDFATHERED')

    missing = [rel for rel in GRANDFATHERED if not (root / rel).exists()]
    for rel in missing:
        print(f'🧹 {rel} no longer exists - remove it from GRANDFATHERED')

    if failures:
        print(
            f'\n❌ Files over their line ceiling (max {MAX_LINES}, grandfathered files may only shrink):'
        )
        for rel, lines, allowed in failures:
            print(f'   {lines:5} lines (allowed {allowed}): {rel}')
        return 1

    if stale_grandfathers or missing:
        # Tidiness nudge, not a failure
        print('\n✅ No files over the ceiling (but tidy the grandfather list above)')
        return 0

    print(f'✅ No source file exceeds {MAX_LINES} lines (grandfather list: {len(GRANDFATHERED)})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
