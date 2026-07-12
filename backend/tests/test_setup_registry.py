# Setup Registry Tests - OFFLINE (pure logic, no LLM, no DB, no subprocesses)
# Exercises the Stp-M1 layer: the required-vs-local-extras component split
# in setup/components.py and the gates built on it - a fresh API-first
# machine (no GPU, no CUDA, no model) must count as READY.
#
# Usage: python -m backend.tests.test_setup_registry   (from project root)

import contextlib
import io
import os
import tempfile
from pathlib import Path

PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = ''):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ✅ {name}")
    else:
        FAILED += 1
        print(f"  ❌ {name}{f' - {detail}' if detail else ''}")


def main():
    from setup.components import (
        ALL_COMPONENTS,
        LOCAL_EXTRA_COMPONENTS,
        REQUIRED_COMPONENTS,
        components_for,
    )

    print('🧪 SETUP REGISTRY TESTS')
    print('=' * 50)

    # ===== The split itself =====
    print('\n-- required vs local-extras split --')
    check(
        'required is exactly the API-first four',
        REQUIRED_COMPONENTS
        == ('Basic Backend', 'Node.js & npm', 'MySQL Server', 'Database Connection'),
    )
    check(
        'local extras is exactly the escape-hatch chain',
        LOCAL_EXTRA_COMPONENTS
        == ('NVIDIA GPU & CUDA', 'Visual Studio Build Tools', 'Model Directory', 'LLM Integration'),
    )
    check(
        'every component is in exactly one bucket',
        set(REQUIRED_COMPONENTS) | set(LOCAL_EXTRA_COMPONENTS) == set(ALL_COMPONENTS)
        and not set(REQUIRED_COMPONENTS) & set(LOCAL_EXTRA_COMPONENTS),
    )
    check('default run excludes local extras', components_for(False) == REQUIRED_COMPONENTS)
    check('--local-extras run covers everything', components_for(True) == ALL_COMPONENTS)
    check(
        'setup order keeps dependencies (env before database)',
        components_for(False).index('Basic Backend')
        < components_for(False).index('Database Connection'),
    )

    # ===== Registries stay in sync with the component list =====
    print('\n-- registry coverage --')
    from setup.checks import COMPONENT_CHECKS, COMPONENT_DIAGNOSTICS
    from setup.flows import COMPONENT_FLOWS

    check('every component has a check', set(ALL_COMPONENTS) == set(COMPONENT_CHECKS))
    check('every component has a flow', set(ALL_COMPONENTS) == set(COMPONENT_FLOWS))
    check('every component has a diagnostic', set(ALL_COMPONENTS) == set(COMPONENT_DIAGNOSTICS))

    # ===== The gate: fresh API-first machine counts as READY =====
    print('\n-- check_requirements gating --')
    import setup.checks as checks_module
    from setup.check_requirements import check_requirements

    real_checks = dict(checks_module.COMPONENT_CHECKS)
    try:
        # Simulate: everything the game needs works, the whole local
        # chain is absent (the machine we are designing for)
        for name in REQUIRED_COMPONENTS:
            checks_module.COMPONENT_CHECKS[name] = lambda: True
        for name in LOCAL_EXTRA_COMPONENTS:
            checks_module.COMPONENT_CHECKS[name] = lambda: False

        with contextlib.redirect_stdout(io.StringIO()):
            default_result = check_requirements()
            extras_result = check_requirements(include_local_extras=True)

        check('fresh API-first machine passes the default gate', default_result == 0)
        check('--local-extras still reports the missing chain', extras_result == 1)

        # And a machine missing a real requirement must still fail
        checks_module.COMPONENT_CHECKS['MySQL Server'] = lambda: False
        with contextlib.redirect_stdout(io.StringIO()):
            missing_mysql_result = check_requirements()
        check('missing MySQL fails the default gate', missing_mysql_result == 1)
    finally:
        checks_module.COMPONENT_CHECKS.clear()
        checks_module.COMPONENT_CHECKS.update(real_checks)

    # ===== requirements.txt stays base-only =====
    print('\n-- requirements aggregator --')
    requirements_text = Path('requirements.txt').read_text(encoding='utf-8')
    lines = [
        line.strip()
        for line in requirements_text.splitlines()
        if line.strip() and not line.strip().startswith('#')
    ]
    check('requirements.txt installs base.txt', '-r requirements/base.txt' in lines)
    check(
        'requirements.txt does NOT drag in the LLM engine',
        all('llm' not in line for line in lines),
        f'active lines: {lines}',
    )

    # ===== .env creation generates a real secret =====
    print('\n-- .env creation --')
    from setup.utils.env_utils import create_env_file_from_template, load_env_config

    original_cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            os.chdir(temp_dir)
            Path('.env.example').write_text(
                'SECRET_KEY=your-secret-key-here\nDB_PASSWORD=your_mysql_password_here\n',
                encoding='utf-8',
            )
            success, message = create_env_file_from_template()
            env_vars = load_env_config()
        finally:
            os.chdir(original_cwd)

    check('.env created from template', success, message)
    secret = env_vars.get('SECRET_KEY', '')
    check(
        'SECRET_KEY is generated, not the placeholder',
        secret != 'your-secret-key-here' and len(secret) >= 32,
    )
    check(
        'other placeholders left for their own flows',
        env_vars.get('DB_PASSWORD') == 'your_mysql_password_here',
    )

    print('\n' + '=' * 50)
    print(f'🎉 {PASSED} passed, {FAILED} failed')
    return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
