# Streaming Routes - EVENT-DRIVEN (No polling!)
# Uses blocking SSE service for maximum efficiency
# Only sends data when events actually occur

import json
import time
from flask import Blueprint, Response, request, jsonify
from backend.services import llm_service
from backend.services.sse_service import get_sse_service

streaming_bp = Blueprint('streaming', __name__, url_prefix='/api/streaming')

@streaming_bp.route('/llm-events')
def stream_events():
    """SSE endpoint for real-time updates"""
    
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
                
                # No sleep needed - we only wake up when there's work to do!  # 50ms instead of 1000ms for near real-time updates
                
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

@streaming_bp.route('/add', methods=['POST'])
def add_request():
    """Add inference request - thin route"""
    data = request.get_json() or {}
    prompt = data.get('prompt', 'Hello')
    
    result = llm_service.inference_request(prompt, wait_for_completion=False)
    return jsonify(result)

@streaming_bp.route('/test/simple', methods=['POST'])
def test_simple():
    """Simple test - thin route"""
    result = llm_service.inference_request("Say hi", wait_for_completion=True)
    return jsonify(result)

@streaming_bp.route('/connections')
def get_connections():
    """Get SSE connection info for debugging"""
    sse_service = get_sse_service()
    
    return jsonify({
        'active_connections': sse_service.get_connection_count(),
        'event_types': sse_service._event_service.get_all_event_types(),
        'streaming_method': 'event_driven_blocking',
        'efficiency': 'Only sends data when events occur (no polling!)'
    })