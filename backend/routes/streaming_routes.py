# Streaming Routes - ACTUALLY THIN
# Minimal routes for streaming functionality

import json
import time
import threading
from flask import Blueprint, Response, request, jsonify
from backend.services import llm_service

streaming_bp = Blueprint('streaming', __name__, url_prefix='/api/streaming')

# Simple SSE connection tracking
_connections = set()
_connections_lock = threading.Lock()

class SSEConnection:
    def __init__(self, connection_id):
        self.id = connection_id
        self.queue = []
        self.active = True
        self.lock = threading.Lock()
    
    def send_event(self, event_type, data):
        with self.lock:
            if self.active:
                self.queue.append({'event': event_type, 'data': data})
    
    def get_events(self):
        with self.lock:
            events = self.queue[:]
            self.queue.clear()
            return events

@streaming_bp.route('/llm-events')
def stream_events():
    """SSE endpoint for real-time updates"""
    def event_generator():
        connection = SSEConnection(f"conn_{int(time.time() * 1000)}")
        
        with _connections_lock:
            _connections.add(connection)
        
        try:
            yield f"event: connected\ndata: {json.dumps({'message': 'Connected'})}\n\n"
            
            while connection.active:
                events = connection.get_events()
                for event in events:
                    yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
                
                yield f"event: ping\ndata: {json.dumps({'timestamp': time.time()})}\n\n"
                time.sleep(1)
                
        finally:
            with _connections_lock:
                _connections.discard(connection)
    
    return Response(event_generator(), mimetype='text/event-stream')

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

# Setup queue broadcasting (simplified)
def setup_broadcasting():
    try:
        from backend.llm.queue import get_llm_queue
        
        def callback(event):
            with _connections_lock:
                for conn in _connections:
                    conn.send_event(event['type'], event['data'])
        
        queue = get_llm_queue()
        queue.add_streaming_callback(callback)
    except:
        pass  # Ignore if queue not ready

setup_broadcasting()