# Pytest bridge - runs every offline suite as one pytest test each.
# The suites stay readable check()-style scripts (runnable standalone and
# from the in-app Developer screen); this file is how pytest and CI see
# them. A suite passes when its main() reports zero failed checks.
#
# Usage: python -m pytest          (from project root; MySQL must be running)

import importlib

import pytest

SUITES = [
    'test_resources',
    'test_monster_templates',
    'test_memory_foundation',
    'test_growth',
    'test_returning',
    'test_evolution',
    'test_chat_and_summaries',
    'test_expedition',
    'test_stakes',
    'test_affinity',
    'test_first_run',
]


@pytest.mark.parametrize('suite_name', SUITES)
def test_offline_suite(suite_name):
    suite = importlib.import_module(f'backend.tests.{suite_name}')
    failed_checks = suite.main()
    assert not failed_checks, f'{suite_name}: {failed_checks} check(s) failed'
