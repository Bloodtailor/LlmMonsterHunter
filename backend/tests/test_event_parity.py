# Event Parity Tests - OFFLINE (pure logic, no LLM, no DB, no subprocesses)
# The SSE event contract is mirrored by hand in four places: the backend
# registry declares an event, a frontend handler file consumes it, the
# EventProvider spreads that handler file into the live SSE map, and
# docs/api/events-and-sse.md documents it for anyone working the frontend.
# Nothing connected those four, so they could - and did - drift apart
# silently (monster.affinity_changed shipped with no frontend handler).
#
# This suite is the tripwire. It reads all four sources and fails the
# moment any of them stops agreeing with the registry, which is the
# single source of truth for what the backend can emit.
#
# Usage: python -m backend.tests.test_event_parity   (from project root)

import re
from pathlib import Path

PASSED = 0
FAILED = 0

# Resolved from this file rather than the working directory so the suite
# behaves the same from pytest, the command line, and the Developer screen
REPO_ROOT = Path(__file__).resolve().parents[2]
HANDLER_DIR = REPO_ROOT / 'frontend' / 'src' / 'api' / 'events'
EVENT_PROVIDER = REPO_ROOT / 'frontend' / 'src' / 'app' / 'contexts' / 'EventContext' / 'EventProvider.js'
EVENT_CATALOG_DOC = REPO_ROOT / 'docs' / 'api' / 'events-and-sse.md'

# An event name is always dotted and lower-case ('monster.art_ready',
# 'llm.generation.started'). Requiring the dot keeps these patterns from
# matching the camelCase broadcast names that live alongside them.
EVENT_NAME = r"[a-z_]+(?:\.[a-z_]+)+"

# Handler files register events as quoted object keys: 'monster.created': (eventData) => {
HANDLER_KEY_PATTERN = re.compile(rf"^\s*'({EVENT_NAME})'\s*:", re.MULTILINE)

# EventProvider builds the live SSE map by spreading each handler export: ...monsterEventHandlers,
HANDLER_SPREAD_PATTERN = re.compile(r"\.\.\.([A-Za-z]+EventHandlers)\b")

# The doc's catalog entries are bullets that lead with the event name in
# backticks. Anchoring to the line start skips prose mentions of events.
DOC_EVENT_PATTERN = re.compile(rf"^-\s+`({EVENT_NAME})`", re.MULTILINE)


def check(name: str, condition: bool, detail: str = ''):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ✅ {name}")
    else:
        FAILED += 1
        print(f"  ❌ {name}{f' - {detail}' if detail else ''}")


def describe(events) -> str:
    """Render a set of event names for a failure message, newest problem first"""
    return ', '.join(sorted(events)) if events else '(none)'


def read_frontend_handlers() -> dict:
    """Map each *EventHandlers.js file stem to the event names it handles"""
    handlers_by_file = {}
    for handler_file in sorted(HANDLER_DIR.glob('*EventHandlers.js')):
        source = handler_file.read_text(encoding='utf-8')
        handlers_by_file[handler_file.stem] = set(HANDLER_KEY_PATTERN.findall(source))
    return handlers_by_file


def main():
    # Importing the events package runs every *_events.py module, which is
    # what populates EVENT_REGISTRY - no app context or database needed
    from backend.core.events import get_internal_events, get_sse_events

    print('🧪 EVENT PARITY TESTS')
    print('=' * 50)

    sse_events = set(get_sse_events())
    internal_events = set(get_internal_events())
    handlers_by_file = read_frontend_handlers()
    handled_events = set().union(*handlers_by_file.values()) if handlers_by_file else set()

    # ===== The sources are readable at all =====
    print('\n-- sources --')
    check('backend registry declares SSE events', bool(sse_events), 'registry came back empty')
    check('frontend handler files found', bool(handlers_by_file), f'looked in {HANDLER_DIR}')
    check('EventProvider is where we expect it', EVENT_PROVIDER.exists(), str(EVENT_PROVIDER))
    check('event catalog doc is where we expect it', EVENT_CATALOG_DOC.exists(), str(EVENT_CATALOG_DOC))

    # ===== Backend declares it -> frontend handles it =====
    # This is the drift that ships silently: the backend announces something
    # over SSE and nothing on the other end is listening, so the UI quietly
    # shows stale state until an unrelated refetch happens to fix it.
    print('\n-- backend -> frontend --')
    unhandled = sse_events - handled_events
    check(
        'every send_to_frontend event has a handler',
        not unhandled,
        f'declared but never handled: {describe(unhandled)}',
    )

    # The reverse: a handler for an event the backend cannot emit is dead
    # code, and usually means an event was renamed or removed on one side.
    orphaned = handled_events - sse_events - internal_events
    check(
        'every handler maps to a registered event',
        not orphaned,
        f'handled but never declared: {describe(orphaned)}',
    )

    # Internal events deliberately never reach SSE, so a handler for one
    # would wait forever for a message that is not coming.
    listening_to_internal = handled_events & internal_events
    check(
        'no handler listens for an internal-only event',
        not listening_to_internal,
        f'internal events with handlers: {describe(listening_to_internal)}',
    )

    # ===== Handler files -> the live SSE map =====
    # A handler file that nobody spreads into EventProvider is inert: every
    # event in it is effectively unhandled no matter how correct it looks.
    print('\n-- handler files -> EventProvider --')
    provider_source = EVENT_PROVIDER.read_text(encoding='utf-8')
    spread_handlers = set(HANDLER_SPREAD_PATTERN.findall(provider_source))
    unwired = set(handlers_by_file) - spread_handlers
    check(
        'every handler file is spread into EventProvider',
        not unwired,
        f'file exists but is never wired up: {describe(unwired)}',
    )
    missing_files = spread_handlers - set(handlers_by_file)
    check(
        'every spread handler has a handler file',
        not missing_files,
        f'spread but no matching file: {describe(missing_files)}',
    )

    # ===== The documented catalog -> the registry =====
    # docs/api/events-and-sse.md is the reference a frontend developer reads
    # instead of the backend source. It is only worth reading if it cannot
    # quietly fall behind, so it is checked like code.
    print('\n-- documented catalog -> registry --')
    doc_source = EVENT_CATALOG_DOC.read_text(encoding='utf-8')
    documented_events = set(DOC_EVENT_PATTERN.findall(doc_source))
    undocumented = sse_events - documented_events
    check(
        'every SSE event appears in the catalog',
        not undocumented,
        f'emitted but undocumented: {describe(undocumented)}',
    )
    invented = documented_events - sse_events - internal_events
    check(
        'the catalog documents no event that does not exist',
        not invented,
        f'documented but never declared: {describe(invented)}',
    )

    print('\n' + '=' * 50)
    print(f'🎉 {PASSED} passed, {FAILED} failed')
    return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
