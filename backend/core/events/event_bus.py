# Event Service - Central Event Bus
# Simple pub/sub system for real-time game events
# Thread-safe for solo player game
print(f"🔍 Loading {__file__}")
import threading
from typing import Dict, List, Callable, Any
from collections import defaultdict

class EventService:
    """
    Central event bus for the Monster Hunter Game
    Handles all real-time events with clean separation of concerns
    """
    
    def __init__(self):
        self._subscribers = defaultdict(list)  # event_type -> [callback, callback, ...]
        self._lock = threading.Lock()
    
    def emit(self, event_type: str, data: Dict[str, Any]) -> bool:
        """
        Emit an event to all subscribers
        
        Args:
            event_type (str): Event type (e.g. 'llm.generation.started')
            data (dict): Event data
            
        Returns:
            bool: True if all subscribers notified successfully
        """
        
        with self._lock:
            subscribers = self._subscribers[event_type].copy()
        
        if not subscribers:
            return True  # No subscribers, that's fine
        
        # Add metadata to event
        event = {
            'type': event_type,
            'data': data,
            'timestamp': self._get_timestamp()
        }
        
        success_count = 0
        
        # Notify all subscribers (continue if one fails)
        for callback in subscribers:
            try:
                callback(event)
                success_count += 1
            except Exception as e:
                print(f"⚠️ Event subscriber failed for {event_type}: {e}")
                # Continue notifying other subscribers
        
        return success_count == len(subscribers)
    
    def subscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Subscribe to an event type
        
        Args:
            event_type (str): Event type to subscribe to
            callback (callable): Function to call when event occurs
            
        Returns:
            bool: True if subscribed successfully
        """
        
        try:
            with self._lock:
                self._subscribers[event_type].append(callback)
            return True
        except Exception as e:
            print(f"❌ Failed to subscribe to {event_type}: {e}")
            return False
    
    def unsubscribe(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Unsubscribe from an event type
        
        Args:
            event_type (str): Event type
            callback (callable): Callback to remove
            
        Returns:
            bool: True if unsubscribed successfully
        """
        
        try:
            with self._lock:
                if callback in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(callback)
                    return True
                return False
        except Exception as e:
            print(f"❌ Failed to unsubscribe from {event_type}: {e}")
            return False
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for an event type"""
        with self._lock:
            return len(self._subscribers[event_type])
    
    def get_all_event_types(self) -> List[str]:
        """Get all event types that have subscribers"""
        with self._lock:
            return list(self._subscribers.keys())
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()

# Global event service instance
_event_service = None
_service_lock = threading.Lock()

def get_event_service() -> EventService:
    """Get global event service instance"""
    global _event_service
    
    with _service_lock:
        if _event_service is None:
            _event_service = EventService()
    
    return _event_service

# Convenience functions for common usage
def emit_event(event_type: str, data: Dict[str, Any]) -> bool:
    """Emit an event (convenience function)"""
    return get_event_service().emit(event_type, data)

def subscribe_to_event(event_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
    """Subscribe to an event (convenience function)"""
    return get_event_service().subscribe(event_type, callback)