# LLM Queue - SIMPLIFIED
# Just manages queue of database log entries - streaming removed
# Uses event_service for all event notifications

import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime
from queue import Queue, Empty
from dataclasses import dataclass
from enum import Enum

_global_queue = None
_queue_lock = threading.Lock()

class QueueItemStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class QueueItem:
    log_id: int
    priority: int
    created_at: datetime
    status: QueueItemStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            'log_id': self.log_id,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class LLMQueue:
    def __init__(self):
        self._queue = Queue()
        self._items = {}  # log_id -> QueueItem
        self._lock = threading.Lock()
        self._worker_thread = None
        self._running = False
        self._current_item = None
        self._app = None
        
    def set_flask_app(self, app):
        self._app = app
        
    def start_worker(self):
        if self._worker_thread and self._worker_thread.is_alive():
            return
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
    
    def add_request(self, log_id: int) -> bool:
        """
        Add a log entry to the queue for processing
        
        Args:
            log_id (int): Database log ID containing all parameters
            
        Returns:
            bool: True if added successfully
        """
        
        try:
            # Get priority from log entry
            from . import log as llm_log
            log_entry = llm_log.get_log(log_id)
            if not log_entry:
                print(f"❌ Log {log_id} not found, cannot queue")
                return False
            
            priority = log_entry.priority
            
            # Create queue item
            item = QueueItem(
                log_id=log_id,
                priority=priority,
                created_at=datetime.utcnow(),
                status=QueueItemStatus.PENDING
            )
            
            with self._lock:
                self._items[log_id] = item
                self._queue.put((priority, log_id))
            
            # Emit event using event service
            self._emit_event('llm.queue.update', {
                "action": "added", 
                "item": item.to_dict(),
                "queue_size": self._queue.qsize()
            })
            
            print(f"📥 Added log {log_id} to queue (priority {priority})")
            return True
            
        except Exception as e:
            print(f"❌ Error adding log {log_id} to queue: {e}")
            return False
    
    def get_request_status(self, log_id: int) -> Optional[Dict[str, Any]]:
        """Get queue status for a specific log_id"""
        with self._lock:
            item = self._items.get(log_id)
            return item.to_dict() if item else None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status"""
        with self._lock:
            items = list(self._items.values())
            status_counts = {}
            for item in items:
                status = item.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                "queue_size": self._queue.qsize(),
                "total_items": len(items),
                "status_counts": status_counts,
                "current_item": self._current_item.to_dict() if self._current_item else None,
                "worker_running": self._running
            }
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit event using event service"""
        try:
            from backend.services.event_service import emit_event
            emit_event(event_type, data)
        except Exception as e:
            print(f"⚠️ Failed to emit event {event_type}: {e}")
    
    def _process_item(self, item: QueueItem):
        """Process a queue item by delegating to processor.py"""
        from .processor import process_request
        
        try:
            # Create streaming callback that emits events
            def on_stream(partial_text):
                self._emit_event('llm.generation.update', {
                    "log_id": item.log_id,
                    "partial_text": partial_text,
                    "tokens_so_far": len(partial_text.split()) if partial_text else 0
                })
            
            # Ensure Flask app context for database operations
            if self._app:
                with self._app.app_context():
                    result = process_request(item.log_id, callback=on_stream)
            else:
                result = {'success': False, 'error': 'No Flask app context available'}
            
            item.result = result
            item.completed_at = datetime.utcnow()
            
            if result['success']:
                item.status = QueueItemStatus.COMPLETED
                self._emit_event('llm.generation.completed', {
                    "item": item.to_dict(),
                    "log_id": item.log_id,
                    "final_text": result.get('text', ''),
                    "parsing_success": result.get('parsing_success'),
                    "tokens_generated": result.get('tokens', 0),
                    "duration": result.get('duration', 0),
                    "attempt": result.get('attempt', 1)
                })
            else:
                item.status = QueueItemStatus.FAILED
                item.error = result.get('error', 'Unknown error')
                self._emit_event('llm.generation.failed', {
                    "item": item.to_dict(), 
                    "log_id": item.log_id,
                    "error": item.error
                })
                
        except Exception as e:
            item.status = QueueItemStatus.FAILED
            item.error = str(e)
            item.completed_at = datetime.utcnow()
            self._emit_event('llm.generation.failed', {
                "item": item.to_dict(),
                "log_id": item.log_id, 
                "error": item.error
            })
    
    def _worker_loop(self):
        """Main worker loop - processes queue items"""
        while self._running:
            try:
                try:
                    priority, log_id = self._queue.get(timeout=1.0)
                except Empty:
                    continue
                
                with self._lock:
                    item = self._items.get(log_id)
                
                if not item or item.status != QueueItemStatus.PENDING:
                    continue
                
                item.status = QueueItemStatus.PROCESSING
                item.started_at = datetime.utcnow()
                self._current_item = item
                
                self._emit_event('llm.generation.started', {
                    "item": item.to_dict(),
                    "log_id": log_id
                })
                
                print(f"🔄 Processing log {log_id}")
                self._process_item(item)
                self._current_item = None
                
            except Exception as e:
                print(f"❌ Worker error: {e}")
                if self._current_item:
                    self._current_item.status = QueueItemStatus.FAILED
                    self._current_item.error = str(e)
                    self._current_item = None

def get_llm_queue() -> LLMQueue:
    """Get global queue instance"""
    global _global_queue
    with _queue_lock:
        if _global_queue is None:
            _global_queue = LLMQueue()
            _global_queue.start_worker()
    return _global_queue