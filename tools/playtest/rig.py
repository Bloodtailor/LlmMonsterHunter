# The headless rig - the one piece of startup.py the playtest tools
# repeat: a test-DB app with both queue workers wired to it. No routes,
# no SSE, no local model load; the provider seam still resolves
# game_settings per request, so a seeded test DB speaks real DeepSeek
# and an unseeded one falls to the local floor (see seed_provider.py).

import time


def build_rig():
    """(app, workflow_queue) against the TEST database, workers wired"""
    from backend.tests.harness import build_test_app

    app = build_test_app()

    from backend.ai.queue import get_ai_queue
    from backend.workflow.workflow_queue import get_queue

    get_ai_queue().set_flask_app(app)
    workflow_queue = get_queue()
    workflow_queue.set_flask_app(app)
    return app, workflow_queue


def refresh_session():
    """End the driver's read transaction so the next query sees the
    worker thread's commits. The running game never needs this - each
    HTTP request gets a fresh session - but these tools hold one app
    context for a whole process, and MySQL's REPEATABLE READ would
    otherwise pin every read to the first snapshot."""
    from backend.models.core import db

    db.session.rollback()


def run_workflow(workflow_queue, workflow_type: str, context: dict, timeout_seconds: int = 900):
    """Submit through the production gateway; wait for a terminal status.
    Returns the queue's status dict, or raises TimeoutError."""
    from backend.workflow.workflow_gateway import request_workflow

    success, workflow_id = request_workflow(workflow_type, context=context)
    if not success:
        raise RuntimeError(f"queue refused {workflow_type}")

    started = time.time()
    while time.time() - started < timeout_seconds:
        status = workflow_queue.get_workflow_status(workflow_id)
        if status and status['status'] in ('completed', 'failed'):
            refresh_session()
            return status
        time.sleep(0.05)
    raise TimeoutError(f"{workflow_type} never finished (workflow_id={workflow_id})")


def drain_queue(workflow_queue, timeout_seconds: int = 300):
    """Wait out queued housekeeping (log condense) before process exit"""
    started = time.time()
    while time.time() - started < timeout_seconds:
        counts = workflow_queue.get_queue_status().get('status_counts', {})
        if not counts.get('pending') and not counts.get('processing'):
            return
        time.sleep(0.05)
