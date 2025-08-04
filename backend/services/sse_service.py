# SSE Service - CLEANED UP
# Server-Sent Events Management with minimal output
# EVENT-DRIVEN: Uses blocking queues for maximum efficiency
print(f"🔍 Loading {__file__}")
import json
import time
import threading
from typing import Dict, Any, Set, Optional
from queue import Queue, Empty
import threading
from ..core.event_bus import get_event_service

class SSEConnection:
    """
    Represents a single SSE connection with efficient event delivery
    Uses blocking queue operations - only wakes up when events occur
    """
    
    def __init__(self, connection_id: str):
        self.id = connection_id
        self.event_queue = Queue()
        self.active = True
        self.created_at = time.time()
    
    def send_event(self, event: Dict[str, Any]):
        """Add event to this connection's queue"""
        if self.active:
            try:
                self.event_queue.put_nowait(event)
            except:
                # Queue full, connection probably dead
                self.active = False
    
    def get_next_event(self, timeout=30):
        """
        Get next event, blocking until one arrives or timeout
        
        Args:
            timeout (int): Seconds to wait before timeout
            
        Returns:
            dict: Event data or None if timeout
        """
        if not self.active:
            return None
            
        try:
            return self.event_queue.get(timeout=timeout)
        except Empty:
            return None  # Timeout occurred
    
    def close(self):
        """Mark connection as closed"""
        self.active = False

class SSEService:
    """
    Manages all SSE connections and event forwarding
    Subscribes to event_service and routes to active connections
    """
    
    def __init__(self):
        self._connections: Dict[str, SSEConnection] = {}
        self._lock = threading.Lock()
        self._event_service = get_event_service()
        self._setup_event_subscriptions()
    
    def create_connection(self, connection_id: Optional[str] = None) -> SSEConnection:
        """
        Create a new SSE connection
        
        Args:
            connection_id (str): Optional connection ID, auto-generated if None
            
        Returns:
            SSEConnection: New connection instance
        """
        
        if connection_id is None:
            connection_id = f"sse_{int(time.time() * 1000)}"
        
        connection = SSEConnection(connection_id)
        
        with self._lock:
            self._connections[connection_id] = connection
        
        # Removed verbose connection creation message
        
        # Send initial connection event
        connection.send_event({
            'type': 'sse.connected',
            'data': {'message': 'Connected to Monster Hunter Game'},
            'timestamp': time.time()
        })
        
        return connection
    
    def remove_connection(self, connection_id: str):
        """Remove a connection"""
        with self._lock:
            if connection_id in self._connections:
                self._connections[connection_id].close()
                del self._connections[connection_id]
                # Removed verbose connection removal message
    
    def broadcast_event(self, event: Dict[str, Any]):
        """
        Broadcast event to all active connections
        Called by event_service subscribers
        
        Args:
            event (dict): Event data from event_service
        """
        
        with self._lock:
            active_connections = [conn for conn in self._connections.values() if conn.active]
        
        if not active_connections:
            return
        
        # Convert event to SSE format
        sse_event = self._convert_to_sse_format(event)
        
        # Send to all active connections
        for connection in active_connections:
            connection.send_event(sse_event)
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        with self._lock:
            return len([conn for conn in self._connections.values() if conn.active])
    
    def cleanup_dead_connections(self):
        """Remove connections that are no longer active"""
        with self._lock:
            dead_connections = [
                conn_id for conn_id, conn in self._connections.items() 
                if not conn.active
            ]
            
            for conn_id in dead_connections:
                del self._connections[conn_id]
                # Removed verbose cleanup message

    def _setup_event_subscriptions(self):
        """Subscribe only to frontend events"""
        from backend.core.event_registry import get_sse_events
        
        frontend_events = get_sse_events()  # Only gets send_to_frontend=True events

        print()
        print("Registering SSE events:")
        
        for event_type in frontend_events:
            self._event_service.subscribe(event_type, self.broadcast_event)
            print(f"    {event_type}")

        print()
            
    def _convert_to_sse_format(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert event_service event to SSE format
        Maintains compatibility with existing frontend
        
        Args:
            event (dict): Event from event_service
            
        Returns:
            dict: SSE-formatted event
        """
        
        return {
            'event': event['type'],
            'data': event['data'],
            'timestamp': event.get('timestamp', time.time())
        }

# Global SSE service instance
_sse_service = None
_service_lock = threading.Lock()

def get_sse_service() -> SSEService:
    """Get global SSE service instance"""
    global _sse_service
    
    with _service_lock:
        if _sse_service is None:
            _sse_service = SSEService()
    
    return _sse_service