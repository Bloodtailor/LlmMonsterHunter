# Streaming Routes - UPDATED FOR UNIFIED GENERATION SERVICE
# Uses event-driven SSE service for maximum efficiency
# Now supports both LLM and image generation events

import json
import time
from flask import Blueprint, Response, request, jsonify
from backend.services import generation_service  # 🔧 UPDATED: was llm_service
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

@streaming_bp.route('/add', methods=['POST'])
def add_request():
    """Add LLM inference request - thin route"""
    data = request.get_json() or {}
    prompt = data.get('prompt', 'Hello')
    
    result = generation_service.text_generation_request(  # 🔧 UPDATED: new service
        prompt=prompt, 
        wait_for_completion=False
    )
    return jsonify(result)

@streaming_bp.route('/add-image', methods=['POST'])
def add_image_request():
    """Add image generation request - NEW ENDPOINT"""
    data = request.get_json() or {}
    
    monster_description = data.get('monster_description', 'A mysterious creature')
    monster_name = data.get('monster_name', '')
    monster_species = data.get('monster_species', '')
    
    result = generation_service.image_generation_request(  # 🔧 NEW: image generation
        monster_description=monster_description,
        monster_name=monster_name,
        monster_species=monster_species,
        wait_for_completion=False
    )
    return jsonify(result)

@streaming_bp.route('/test/simple', methods=['POST'])
def test_simple():
    """Simple LLM test - thin route"""
    result = generation_service.text_generation_request(  # 🔧 UPDATED: new service
        prompt="Say hi", 
        wait_for_completion=True
    )
    return jsonify(result)

@streaming_bp.route('/test/image', methods=['POST'])
def test_image():
    """Simple image generation test - NEW ENDPOINT"""
    data = request.get_json() or {}
    description = data.get('description', 'A majestic fire dragon with golden scales')
    
    result = generation_service.image_generation_request(  # 🔧 NEW: image generation test
        monster_description=description,
        monster_name="Test Dragon",
        wait_for_completion=True
    )
    return jsonify(result)

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