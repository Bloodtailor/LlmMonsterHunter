# Streaming Routes - UPDATED FOR UNIFIED GENERATION SERVICE
# Uses event-driven SSE service for maximum efficiency
# Now supports both LLM and image generation events
print(f"🔍 Loading {__file__}")
import json
import time
from flask import Blueprint, Response, request, jsonify
from backend.services.sse_service import get_sse_service

streaming_bp = Blueprint('streaming', __name__, url_prefix='/api/streaming')

@streaming_bp.route('/llm-events')
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
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    return response


@streaming_bp.route('/connections')
def get_connections():
    """Get SSE connection info for debugging"""
    sse_service = get_sse_service()
    
    return jsonify({
        'active_connections': sse_service.get_connection_count(),
        'event_types': sse_service._event_service.get_all_event_types(),
        'streaming_method': 'event_driven_blocking',
        'efficiency': 'Only sends data when events occur (no polling!)',
        'supported_generation_types': ['llm', 'image']  # 🔧 NEW: both types supported
    })