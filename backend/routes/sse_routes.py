# Streaming Routes - UPDATED FOR UNIFIED GENERATION SERVICE
# Uses event-driven SSE service for maximum efficiency
# Now supports both LLM and image generation events

import json
import time

from flask import Blueprint, Response

from backend.services.sse_service import get_sse_service

sse_bp = Blueprint('sse', __name__, url_prefix='/api/sse')


@sse_bp.route('/events')
def stream_events():
    """SSE endpoint for real-time updates - supports LLM and image events"""

    sse_service = get_sse_service()
    connection = sse_service.create_connection()

    def event_generator():
        try:
            # Send initial ping
            yield f"event: ping\ndata: {json.dumps({'timestamp': time.time()})}\n\n"

            while connection.active:
                # Block waiting for next event (30 second timeout)
                event = connection.get_next_event(timeout=30)

                if event is not None:
                    # We got a real event - send it immediately
                    event_type = event.get('event', 'message')
                    event_data = json.dumps(event.get('data', {}))
                    yield f"event: {event_type}\ndata: {event_data}\n\n"
                else:
                    # Timeout occurred (30 seconds) - send keep-alive ping
                    yield f"event: ping\ndata: {json.dumps({'timestamp': time.time()})}\n\n"

        except GeneratorExit:
            # Client disconnected
            pass
        except Exception as e:
            print(f"❌ SSE stream error: {e}")
        finally:
            # Clean up connection
            sse_service.remove_connection(connection.id)

    response = Response(event_generator(), mimetype='text/event-stream')
    # no-transform matters: the CRA dev proxy gzip-compresses responses by
    # default, and gzip would buffer the event stream into silence - this
    # tells every intermediary to pass events through untouched. The stream
    # is same-origin through that proxy, so no Access-Control header needed.
    response.headers['Cache-Control'] = 'no-cache, no-transform'
    response.headers['Connection'] = 'keep-alive'

    return response
