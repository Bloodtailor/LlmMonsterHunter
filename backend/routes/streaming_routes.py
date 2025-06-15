# Streaming Routes - SIMPLIFIED
# Uses SSE service for connection management
# Clean separation of concerns

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
                # Get events from connection queue
                events = connection.get_events()
                
                # Send each event
                for event in events:
                    event_type = event.get('event', 'message')
                    event_data = json.dumps(event.get('data', {}))
                    yield f"event: {event_type}\ndata: {event_data}\n\n"
                
                # Send periodic ping to keep connection alive
                yield f"event: ping\ndata: {json.dumps({'timestamp': time.time()})}\n\n"
                
                # Brief pause to prevent excessive CPU usage
                time.sleep(1)
                
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
        'event_types': sse_service._event_service.get_all_event_types()
    })