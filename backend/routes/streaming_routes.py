# Streaming Routes - FIXED to ensure ALL requests are logged
# 🔧 CRITICAL FIX: Every queue request now creates a log entry
# No more unlogged requests - everything flows through the same path

import json
import time
import threading
from flask import Blueprint, Response, request, jsonify
from backend.llm.queue import get_llm_queue
from backend.models.llm_log import LLMLog

# Create blueprint for streaming routes
streaming_bp = Blueprint('streaming', __name__, url_prefix='/api/streaming')

# Global set to track active SSE connections
_active_connections = set()
_connections_lock = threading.Lock()

class SSEConnection:
    """Represents an active Server-Sent Events connection"""
    
    def __init__(self, connection_id: str):
        self.id = connection_id
        self.queue = []  # Buffer for messages
        self.active = True
        self.lock = threading.Lock()
    
    def send_event(self, event_type: str, data: dict):
        """Send an event to this connection"""
        with self.lock:
            if self.active:
                self.queue.append({
                    'event': event_type,
                    'data': data,
                    'timestamp': time.time()
                })
    
    def get_and_clear_events(self):
        """Get all pending events and clear the queue"""
        with self.lock:
            events = self.queue[:]
            self.queue.clear()
            return events
    
    def close(self):
        """Mark connection as closed"""
        self.active = False

@streaming_bp.route('/llm-events')
def stream_llm_events():
    """Server-Sent Events endpoint for real-time LLM updates"""
    
    def event_generator():
        """Generator function for SSE events"""
        
        # Create connection tracking
        connection_id = f"conn_{int(time.time() * 1000)}"
        connection = SSEConnection(connection_id)
        
        # Add to active connections
        with _connections_lock:
            _active_connections.add(connection)
        
        try:
            # Send initial connection event
            yield format_sse_message("connected", {
                "connection_id": connection_id,
                "message": "LLM streaming connected"
            })
            
            # Send current queue status
            queue = get_llm_queue()
            queue_status = queue.get_queue_status()
            yield format_sse_message("queue_status", queue_status)
            
            # Main event loop
            while connection.active:
                # Get pending events for this connection
                events = connection.get_and_clear_events()
                
                # Send each event
                for event in events:
                    yield format_sse_message(event['event'], event['data'])
                
                # Keep-alive ping every 30 seconds
                yield format_sse_message("ping", {"timestamp": time.time()})
                
                # Sleep briefly to prevent busy waiting
                time.sleep(1)
                
        except GeneratorExit:
            # Client disconnected
            pass
        finally:
            # Clean up connection
            connection.close()
            with _connections_lock:
                _active_connections.discard(connection)
    
    # Set up SSE response headers
    response = Response(
        event_generator(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control'
        }
    )
    
    return response

@streaming_bp.route('/queue/add', methods=['POST'])
def add_to_queue():
    """
    🔧 CRITICAL FIX: Add request to queue WITH MANDATORY LOGGING
    Every single request now creates a log entry - no exceptions
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing prompt in request'
            }), 400
        
        # Extract parameters
        prompt = data['prompt']
        max_tokens = data.get('max_tokens', 256)
        temperature = data.get('temperature', 0.8)
        prompt_type = data.get('prompt_type', 'manual_test')
        priority = data.get('priority', 5)
        
        # 🔧 CRITICAL: Create LLM log entry for EVERY request
        log = LLMLog.create_log(
            prompt_type='streaming_request',
            prompt_name=prompt_type,
            prompt_text=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if not log.save():
            return jsonify({
                'success': False,
                'error': 'Could not create log entry'
            }), 500
        
        print(f"📋 Created log entry for streaming request: {log.id}")
        
        # Add to queue with log reference
        queue = get_llm_queue()
        request_id = queue.add_request(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            prompt_type=prompt_type,
            priority=priority,
            log_id=log.id  # 🔧 CRITICAL: Always pass log_id
        )
        
        # Associate log with queue request
        log.entity_type = 'streaming_request'
        log.entity_id = request_id
        log.save()
        
        return jsonify({
            'success': True,
            'request_id': request_id,
            'log_id': log.id,
            'message': 'Request added to queue with logging'
        })
        
    except Exception as e:
        print(f"❌ Error adding to queue: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@streaming_bp.route('/queue/status')
def get_queue_status():
    """Get current queue status"""
    try:
        queue = get_llm_queue()
        status = queue.get_queue_status()
        
        return jsonify({
            'success': True,
            'data': status
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@streaming_bp.route('/queue/items')
def get_queue_items():
    """Get recent queue items"""
    try:
        limit = int(request.args.get('limit', 20))
        queue = get_llm_queue()
        items = queue.get_recent_items(limit)
        
        return jsonify({
            'success': True,
            'data': {
                'items': items,
                'count': len(items)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 🔧 NEW: Simple test endpoint that goes through proper flow
@streaming_bp.route('/test/simple', methods=['POST'])
def test_simple():
    """
    Simple test that ensures everything is logged and streamed
    This replaces the old "test queue generation" button functionality
    """
    try:
        # Simple test prompt
        test_prompt = "Generate a simple test response about a friendly dragon named Spark."
        
        # 🔧 Use the same flow as everything else
        log = LLMLog.create_log(
            prompt_type='simple_test',
            prompt_name='streaming_test',
            prompt_text=test_prompt,
            max_tokens=100,
            temperature=0.8
        )
        
        if not log.save():
            return jsonify({
                'success': False,
                'error': 'Could not create log entry'
            }), 500
        
        # Add to queue
        queue = get_llm_queue()
        request_id = queue.add_request(
            prompt=test_prompt,
            max_tokens=100,
            temperature=0.8,
            prompt_type='simple_test',
            priority=2,  # High priority for tests
            log_id=log.id
        )
        
        # Associate log with request
        log.entity_type = 'simple_test'
        log.entity_id = request_id
        log.save()
        
        return jsonify({
            'success': True,
            'request_id': request_id,
            'log_id': log.id,
            'message': 'Simple test started - watch streaming display!',
            'instructions': 'Check the streaming display and LLM log viewer for real-time progress'
        })
        
    except Exception as e:
        print(f"❌ Simple test error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def format_sse_message(event_type: str, data: dict) -> str:
    """Format a Server-Sent Events message"""
    json_data = json.dumps(data)
    return f"event: {event_type}\ndata: {json_data}\n\n"

def broadcast_to_all_connections(event_type: str, data: dict):
    """Broadcast an event to all active SSE connections"""
    with _connections_lock:
        for connection in _active_connections:
            connection.send_event(event_type, data)

# Register the queue callback to broadcast events to all connections
def _queue_event_callback(event):
    """Callback function to handle queue events and broadcast to SSE clients"""
    broadcast_to_all_connections(event['type'], event['data'])

# Initialize the callback when this module is imported
def setup_queue_broadcasting():
    """Set up broadcasting from queue to SSE connections"""
    queue = get_llm_queue()
    queue.add_streaming_callback(_queue_event_callback)

# Call setup when module is imported
setup_queue_broadcasting()