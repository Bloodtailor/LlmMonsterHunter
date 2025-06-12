# LLM Queue Module - REFACTORED
# ONLY handles queue management and worker coordination
# No LLM inference, no logging - pure queue operations

import threading
import time
import uuid
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from queue import Queue, Empty
from dataclasses import dataclass, asdict
from enum import Enum

# Global queue instance
_global_queue = None
_queue_lock = threading.Lock()

class QueueItemStatus(Enum):
    """Status of items in the queue"""
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class QueueItem:
    """Represents a single queued LLM request"""
    id: str
    prompt: str
    max_tokens: int
    temperature: float
    prompt_type: str
    created_at: datetime
    status: QueueItemStatus
    priority: int = 5  # 1=highest, 10=lowest
    log_id: Optional[int] = None  # Link to LLM log entry
    
    # Results (set by worker)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Streaming data
    partial_response: str = ""
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for field in ['created_at', 'started_at', 'completed_at']:
            if data[field]:
                data[field] = data[field].isoformat()
        # Convert enum to string
        data['status'] = data['status'].value
        return data

class LLMQueue:
    """
    Thread-safe LLM prompt queue - SIMPLIFIED
    Only handles queue operations, delegates generation to other modules
    """
    
    def __init__(self):
        self._queue = Queue()
        self._items = {}  # id -> QueueItem
        self._lock = threading.Lock()
        self._worker_thread = None
        self._running = False
        self._current_item = None
        self._streaming_callbacks = []  # For UI notifications
        self._app = None  # Flask app for database context
        
    def set_flask_app(self, app):
        """Set Flask app for database operations"""
        self._app = app
        print(f"📱 Flask app set for queue: {app}")
        
    def start_worker(self):
        """Start the background worker thread"""
        if self._worker_thread and self._worker_thread.is_alive():
            return
        
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        print("✅ LLM Queue worker started")
    
    def stop_worker(self):
        """Stop the background worker thread"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
        print("⏹️ LLM Queue worker stopped")
    
    def add_request(self, prompt: str, max_tokens: int = 256, temperature: float = 0.8,
                   prompt_type: str = "unknown", priority: int = 5,
                   log_id: Optional[int] = None) -> str:
        """
        Add a new request to the queue
        
        Returns:
            str: Request ID for tracking
        """
        request_id = str(uuid.uuid4())
        
        item = QueueItem(
            id=request_id,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            prompt_type=prompt_type,
            created_at=datetime.utcnow(),
            status=QueueItemStatus.PENDING,
            priority=priority,
            log_id=log_id
        )
        
        with self._lock:
            self._items[request_id] = item
            self._queue.put((priority, request_id))
        
        # Notify streaming callbacks
        self._notify_streaming("queue_update", {
            "action": "added", 
            "item": item.to_dict(),
            "queue_size": self._queue.qsize(),
            "total_items": len(self._items)
        })
        
        print(f"📥 Added request {request_id} to queue (priority: {priority}, log_id: {log_id})")
        return request_id
    
    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific request"""
        with self._lock:
            item = self._items.get(request_id)
            return item.to_dict() if item else None
    
    def cancel_request(self, request_id: str) -> bool:
        """Cancel a pending request"""
        with self._lock:
            item = self._items.get(request_id)
            if item and item.status == QueueItemStatus.PENDING:
                item.status = QueueItemStatus.CANCELLED
                
                # Update associated log if exists
                if item.log_id and self._app:
                    self._update_log_status(item.log_id, 'cancelled', 'Request cancelled by user')
                
                self._notify_streaming("queue_update", {
                    "action": "cancelled", 
                    "item": item.to_dict(),
                    "queue_size": self._queue.qsize()
                })
                return True
        return False
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status"""
        with self._lock:
            items = list(self._items.values())
            
            # Count by status
            status_counts = {
                'pending': 0,
                'processing': 0, 
                'completed': 0,
                'failed': 0,
                'cancelled': 0
            }
            
            for item in items:
                status_key = item.status.value
                if status_key in status_counts:
                    status_counts[status_key] += 1
            
            return {
                "queue_size": self._queue.qsize(),
                "total_items": len(items),
                "status_counts": status_counts,
                "current_item": self._current_item.to_dict() if self._current_item else None,
                "worker_running": self._running,
                "active_connections": len(self._streaming_callbacks)
            }
    
    def get_recent_items(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent queue items"""
        with self._lock:
            items = sorted(self._items.values(), key=lambda x: x.created_at, reverse=True)
            return [item.to_dict() for item in items[:limit]]
    
    def add_streaming_callback(self, callback: Callable):
        """Add global streaming callback for all updates"""
        self._streaming_callbacks.append(callback)
        print(f"🔗 Added streaming callback, total: {len(self._streaming_callbacks)}")
    
    def remove_streaming_callback(self, callback: Callable):
        """Remove global streaming callback"""
        if callback in self._streaming_callbacks:
            self._streaming_callbacks.remove(callback)
            print(f"🔗 Removed streaming callback, total: {len(self._streaming_callbacks)}")
    
    def _notify_streaming(self, event_type: str, data: Dict[str, Any]):
        """Notify all streaming callbacks of an event"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Robust callback handling
        callbacks_to_remove = []
        
        for callback in self._streaming_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"⚠️ Streaming callback error: {e}")
                callbacks_to_remove.append(callback)
        
        # Remove failed callbacks
        for callback in callbacks_to_remove:
            self._streaming_callbacks.remove(callback)
        
        print(f"📡 Broadcast {event_type} to {len(self._streaming_callbacks)} connections")
    
    def _update_log_status(self, log_id: int, status: str, error_msg: str = None, 
                          response_text: str = None, tokens: int = None):
        """Update associated LLM log status"""
        if not log_id or not self._app:
            return
            
        try:
            with self._app.app_context():
                from backend.models.llm_log import LLMLog
                
                log = LLMLog.query.get(log_id)
                if not log:
                    print(f"⚠️ Log {log_id} not found for update")
                    return
                
                print(f"📋 Updating log {log_id}: {status}")
                
                if status == 'started':
                    log.mark_started()
                elif status == 'completed':
                    log.mark_completed(
                        response_text=response_text or "Completed via queue", 
                        response_tokens=tokens or 0
                    )
                elif status == 'failed' or status == 'cancelled':
                    log.mark_failed(error_msg or f"Request {status}")
                
                if log.save():
                    print(f"✅ Log {log_id} updated successfully: {status}")
                else:
                    print(f"❌ Failed to save log {log_id}")
                    
        except Exception as e:
            print(f"❌ Error updating log {log_id}: {e}")
    
    def _worker_loop(self):
        """Main worker loop - delegates actual generation to generation service"""
        from .generation_service import process_queue_item
        
        print("🔄 LLM Queue worker loop started")
        
        while self._running:
            try:
                # Wait for next item
                try:
                    priority, request_id = self._queue.get(timeout=1.0)
                except Empty:
                    continue
                
                # Get the item
                with self._lock:
                    item = self._items.get(request_id)
                
                if not item or item.status != QueueItemStatus.PENDING:
                    continue
                
                # Mark as processing
                item.status = QueueItemStatus.PROCESSING
                item.started_at = datetime.utcnow()
                self._current_item = item
                
                # Update log
                if item.log_id and self._app:
                    with self._app.app_context():
                        self._update_log_status(item.log_id, 'started')
                
                # Notify streaming
                self._notify_streaming("generation_started", {
                    "item": item.to_dict(),
                    "request_id": request_id,
                    "prompt_type": item.prompt_type,
                    "max_tokens": item.max_tokens
                })
                
                # Delegate actual processing to generation service
                if self._app:
                    with self._app.app_context():
                        process_queue_item(item, self._notify_streaming, self._update_log_status)
                else:
                    process_queue_item(item, self._notify_streaming, None)
                
                self._current_item = None
                
                # Send queue status update
                self._notify_streaming("queue_status", self.get_queue_status())
                    
            except Exception as e:
                print(f"❌ Worker loop error: {e}")
                
                if self._current_item:
                    self._current_item.status = QueueItemStatus.FAILED
                    self._current_item.error = f"Worker error: {str(e)}"
                    self._current_item.completed_at = datetime.utcnow()
                    
                    # Update log
                    if self._current_item.log_id and self._app:
                        with self._app.app_context():
                            self._update_log_status(self._current_item.log_id, 'failed', self._current_item.error)
                    
                    self._notify_streaming("generation_failed", {
                        "item": self._current_item.to_dict(),
                        "error": self._current_item.error
                    })
                    self._current_item = None

def get_llm_queue() -> LLMQueue:
    """Get the global LLM queue instance (singleton)"""
    global _global_queue
    
    with _queue_lock:
        if _global_queue is None:
            _global_queue = LLMQueue()
            _global_queue.start_worker()
    
    return _global_queue

def shutdown_queue():
    """Shutdown the global queue (for cleanup)"""
    global _global_queue
    
    with _queue_lock:
        if _global_queue:
            _global_queue.stop_worker()
            _global_queue = None