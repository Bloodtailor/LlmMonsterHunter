# Step Contract Tests - OFFLINE (pure logic, no LLM, no DB, no subprocesses)
# Workflow on_update step names are the contract docs/architecture.md warns
# is breaking-if-renamed: the frontend keys progress labels and branching
# logic off them. They are also the least protected thing in the repo -
# bare string literals on both sides, sometimes in a different domain
# folder than the workflow that emits them (the player creation forge
# reads steps emitted by game/player, the evolution ceremony by game/monster).
#
# The contract is one-directional. A backend step no one displays is
# ordinary - most steps are just progress pings. A frontend reference to a
# step the backend cannot emit is the bug: the label silently never fires.
# This suite asserts that direction, so renaming a step on the backend
# fails here instead of quietly blanking a screen.
#
# Usage: python -m backend.tests.test_step_contract   (from project root)

import re
from pathlib import Path

PASSED = 0
FAILED = 0

# Resolved from this file rather than the working directory so the suite
# behaves the same from pytest, the command line, and the Developer screen
REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / 'backend'
FRONTEND_DIR = REPO_ROOT / 'frontend' / 'src'
WORKFLOW_STEP_MODULE = BACKEND_DIR / 'core' / 'workflow_steps.py'

# Backend emits steps two ways. The older workflows keep a local `step`
# variable and pass it to on_update; workflows split across handler modules
# share a WorkflowStep pointer and call step.emit / .mark / .emit_event.
LOCAL_STEP_PATTERN = re.compile(r"""\bstep\s*=\s*['"]([a-z_]+)['"]""")
STEP_POINTER_PATTERN = re.compile(r"""\bstep\.(?:emit|mark|emit_event)\(\s*['"]([a-z_]+)['"]""")
# WorkflowStep's constructor seeds the pointer before any step is emitted
STEP_DEFAULT_PATTERN = re.compile(r"""self\.name\s*=\s*['"]([a-z_]+)['"]""")

# Frontend references steps two ways: label maps keyed by step name, and
# inline comparisons in the event hooks.
STEP_LABEL_MAP_PATTERN = re.compile(r"""[A-Z_]*STEP_LABELS\s*=\s*\{(.*?)\}""", re.DOTALL)
STEP_LABEL_KEY_PATTERN = re.compile(r"""^\s*([a-z_]+)\s*:""", re.MULTILINE)
STEP_COMPARISON_PATTERN = re.compile(r"""\bstep\s*(?:===|!==)\s*['"]([a-z_]+)['"]""")

# Guards against a scanner that silently stops matching: if a refactor
# changes how steps are written, the suite must fail loudly rather than
# pass vacuously forever. These floors are well under today's counts.
MINIMUM_BACKEND_STEPS = 40
MINIMUM_LABEL_MAPS = 2


def check(name: str, condition: bool, detail: str = ''):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ✅ {name}")
    else:
        FAILED += 1
        print(f"  ❌ {name}{f' - {detail}' if detail else ''}")


def describe(steps) -> str:
    """Render a set of step names for a failure message"""
    return ', '.join(sorted(steps)) if steps else '(none)'


def python_sources():
    for path in sorted(BACKEND_DIR.rglob('*.py')):
        if '__pycache__' in path.parts:
            continue
        yield path


def javascript_sources():
    yield from sorted(FRONTEND_DIR.rglob('*.js'))


def collect_emitted_steps() -> set:
    """Every step name the backend can report through on_update"""
    emitted = set()
    for path in python_sources():
        source = path.read_text(encoding='utf-8')
        emitted.update(LOCAL_STEP_PATTERN.findall(source))
        emitted.update(STEP_POINTER_PATTERN.findall(source))
        if path == WORKFLOW_STEP_MODULE:
            emitted.update(STEP_DEFAULT_PATTERN.findall(source))
    return emitted


def collect_referenced_steps() -> tuple:
    """Every step name the frontend keys off, and the label maps it found"""
    referenced = {}
    label_maps_found = 0
    for path in javascript_sources():
        source = path.read_text(encoding='utf-8')
        where = path.relative_to(REPO_ROOT).as_posix()

        for map_body in STEP_LABEL_MAP_PATTERN.findall(source):
            label_maps_found += 1
            for step_name in STEP_LABEL_KEY_PATTERN.findall(map_body):
                referenced.setdefault(step_name, where)

        for step_name in STEP_COMPARISON_PATTERN.findall(source):
            referenced.setdefault(step_name, where)

    return referenced, label_maps_found


def main():
    print('🧪 STEP CONTRACT TESTS')
    print('=' * 50)

    emitted_steps = collect_emitted_steps()
    referenced_steps, label_maps_found = collect_referenced_steps()

    # ===== The scanners still work =====
    # A tripwire that quietly stops finding anything is worse than none
    print('\n-- scanners --')
    check(
        'backend step scan finds the workflow steps',
        len(emitted_steps) >= MINIMUM_BACKEND_STEPS,
        f'found {len(emitted_steps)}, expected at least {MINIMUM_BACKEND_STEPS} - '
        'has the emission style changed?',
    )
    check(
        'frontend scan finds the step label maps',
        label_maps_found >= MINIMUM_LABEL_MAPS,
        f'found {label_maps_found} *_STEP_LABELS maps, expected at least {MINIMUM_LABEL_MAPS}',
    )
    check(
        'frontend scan finds step references',
        bool(referenced_steps),
        'no step names referenced anywhere in frontend/src',
    )

    # ===== The contract itself =====
    # Every step the frontend keys off must be one the backend can emit.
    # A reference to a step that no longer exists never fires: the label
    # stays blank, or the branch never runs, and nothing errors.
    print('\n-- frontend -> backend --')
    dangling = {
        step: where for step, where in referenced_steps.items() if step not in emitted_steps
    }
    check(
        'every referenced step is one the backend emits',
        not dangling,
        'referenced but never emitted: '
        + ', '.join(f'{step} ({where})' for step, where in sorted(dangling.items())),
    )

    # Context, not a rule: most steps are progress pings with no label.
    unreferenced = emitted_steps - set(referenced_steps)
    print(
        f'\n  ℹ️  {len(referenced_steps)} of {len(emitted_steps)} steps are referenced by the '
        f'frontend; {len(unreferenced)} are backend-only progress pings'
    )

    print('\n' + '=' * 50)
    print(f'🎉 {PASSED} passed, {FAILED} failed')
    return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
