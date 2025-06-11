# Streaming Routes - Server-Sent Events for real-time LLM updates
# Provides real-time streaming of LLM generation progress to frontend
# Uses SSE (Server-Sent Events) for one-way real-time communication

import json
import time
import threading
from flask import Blueprint, Response, request, jsonify
from backend.llm.queue import get_llm_queue

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

# Debug Endpoints
# Add these routes to backend/routes/streaming_routes.py for troubleshooting

@streaming_bp.route('/debug/sse-test')
def test_sse():
    """Test Server-Sent Events connection"""
    def test_generator():
        import time
        for i in range(5):
            yield f"data: Test message {i}\n\n"
            time.sleep(1)
        yield "data: SSE test complete\n\n"
    
    return Response(
        test_generator(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

@streaming_bp.route('/debug/queue-info')
def debug_queue_info():
    """Get detailed queue debugging info"""
    try:
        queue = get_llm_queue()
        
        # Get queue status
        status = queue.get_queue_status()
        
        # Get recent items
        items = queue.get_recent_items(10)
        
        # Get worker info
        worker_info = {
            'worker_running': queue._running,
            'current_item': queue._current_item.to_dict() if queue._current_item else None,
            'queue_size': queue._queue.qsize(),
            'items_count': len(queue._items),
            'streaming_callbacks': len(queue._streaming_callbacks)
        }
        
        return jsonify({
            'success': True,
            'data': {
                'status': status,
                'recent_items': items,
                'worker_info': worker_info,
                'timestamp': time.time()
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@streaming_bp.route('/debug/force-broadcast')
def force_broadcast():
    """Force broadcast a test message to all SSE connections"""
    try:
        broadcast_to_all_connections('debug_test', {
            'message': 'This is a test broadcast',
            'timestamp': time.time()
        })
        
        return jsonify({
            'success': True,
            'message': 'Test broadcast sent'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@streaming_bp.route('/llm-events')
def stream_llm_events():
    """
    Server-Sent Events endpoint for real-time LLM updates
    Streams queue status, generation progress, and completion events
    """
    
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
    Add a new request to the LLM queue
    Accepts JSON with prompt, max_tokens, temperature, etc.
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
        prompt_type = data.get('prompt_type', 'manual')
        priority = data.get('priority', 5)
        
        # Add to queue
        queue = get_llm_queue()
        request_id = queue.add_request(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            prompt_type=prompt_type,
            priority=priority
        )
        
        return jsonify({
            'success': True,
            'request_id': request_id,
            'message': 'Request added to queue'
        })
        
    except Exception as e:
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

@streaming_bp.route('/queue/cancel/<request_id>', methods=['POST'])
def cancel_request(request_id):
    """Cancel a specific queue request"""
    try:
        queue = get_llm_queue()
        success = queue.cancel_request(request_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Request {request_id} cancelled'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Request not found or not cancellable'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def format_sse_message(event_type: str, data: dict) -> str:
    """
    Format a Server-Sent Events message
    
    Args:
        event_type (str): Type of event (e.g., 'generation_update')
        data (dict): Event data to send
        
    Returns:
        str: Formatted SSE message
    """
    json_data = json.dumps(data)
    return f"event: {event_type}\ndata: {json_data}\n\n"

def broadcast_to_all_connections(event_type: str, data: dict):
    """
    Broadcast an event to all active SSE connections
    
    Args:
        event_type (str): Type of event
        data (dict): Event data
    """
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