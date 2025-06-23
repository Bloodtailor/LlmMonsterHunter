# AI Generation Queue - UNIFIED FOR ALL GENERATION TYPES
# Handles both LLM text generation and ComfyUI image generation
# Uses normalized generation_log database structure

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
    """Queue item representing a generation request"""
    generation_id: int  # References generation_logs.id
    generation_type: str  # 'llm' or 'image'
    priority: int
    created_at: datetime
    status: QueueItemStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            'generation_id': self.generation_id,
            'generation_type': self.generation_type,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class AIGenerationQueue:
    """
    Unified queue for all AI generation types (LLM + Image)
    Processes generation_log entries based on their generation_type
    """
    
    def __init__(self):
        self._queue = Queue()
        self._items = {}  # generation_id -> QueueItem
        self._lock = threading.Lock()
        self._worker_thread = None
        self._running = False
        self._current_item = None
        self._app = None
        
    def set_flask_app(self, app):
        """Set Flask app for database context"""
        self._app = app
        
    def start_worker(self):
        """Start background worker thread"""
        if self._worker_thread and self._worker_thread.is_alive():
            return
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        print("🔄 AI Generation Queue worker started")
    
    def add_request(self, generation_id: int) -> bool:
        """
        Add a generation request to the queue
        
        Args:
            generation_id (int): Database generation_logs.id
            
        Returns:
            bool: True if added successfully
        """
        
        try:
            # Get generation log entry to determine type and priority
            from backend.models.generation_log import GenerationLog
            log_entry = GenerationLog.query.get(generation_id)
            
            if not log_entry:
                print(f"❌ Generation log {generation_id} not found, cannot queue")
                return False
            
            # Create queue item
            item = QueueItem(
                generation_id=generation_id,
                generation_type=log_entry.generation_type,
                priority=log_entry.priority,
                created_at=datetime.utcnow(),
                status=QueueItemStatus.PENDING
            )
            
            with self._lock:
                self._items[generation_id] = item
                # Priority queue: lower number = higher priority
                self._queue.put((log_entry.priority, generation_id))
            
            # Emit event using event service
            self._emit_event(f'{log_entry.generation_type}.queue.update', {
                "action": "added", 
                "item": item.to_dict(),
                "queue_size": self._queue.qsize()
            })
            
            print(f"📥 Added {log_entry.generation_type} generation {generation_id} to queue (priority {log_entry.priority})")
            return True
            
        except Exception as e:
            print(f"❌ Error adding generation {generation_id} to queue: {e}")
            return False
    
    def get_request_status(self, generation_id: int) -> Optional[Dict[str, Any]]:
        """Get queue status for a specific generation_id"""
        with self._lock:
            item = self._items.get(generation_id)
            return item.to_dict() if item else None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status with breakdown by generation type"""
        with self._lock:
            items = list(self._items.values())
            
            # Count by status
            status_counts = {}
            for item in items:
                status = item.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by generation type
            type_counts = {}
            for item in items:
                gen_type = item.generation_type
                type_counts[gen_type] = type_counts.get(gen_type, 0) + 1
            
            return {
                "queue_size": self._queue.qsize(),
                "total_items": len(items),
                "status_counts": status_counts,
                "type_counts": type_counts,
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
        """Process a queue item by delegating to appropriate processor"""
        
        try:
            # Create streaming callback that emits events
            def on_stream(partial_data):
                if item.generation_type == 'llm':
                    # For LLM, partial_data is partial text
                    self._emit_event('llm.generation.update', {
                        "generation_id": item.generation_id,
                        "partial_text": partial_data,
                        "tokens_so_far": len(partial_data.split()) if partial_data else 0
                    })
                elif item.generation_type == 'image':
                    # For images, partial_data is progress message
                    self._emit_event('image.generation.update', {
                        "generation_id": item.generation_id,
                        "progress_message": partial_data
                    })
            
            # Ensure Flask app context for database operations
            if not self._app:
                raise Exception('No Flask app context available')
            
            with self._app.app_context():
                if item.generation_type == 'llm':
                    result = self._process_llm_item(item, on_stream)
                elif item.generation_type == 'image':
                    result = self._process_image_item(item, on_stream)
                else:
                    raise Exception(f'Unknown generation type: {item.generation_type}')
            
            item.result = result
            item.completed_at = datetime.utcnow()
            
            if result['success']:
                item.status = QueueItemStatus.COMPLETED
                self._emit_event(f'{item.generation_type}.generation.completed', {
                    "item": item.to_dict(),
                    "generation_id": item.generation_id,
                    "result": result
                })
            else:
                item.status = QueueItemStatus.FAILED
                item.error = result.get('error', 'Unknown error')
                self._emit_event(f'{item.generation_type}.generation.failed', {
                    "item": item.to_dict(), 
                    "generation_id": item.generation_id,
                    "error": item.error
                })
                
        except Exception as e:
            item.status = QueueItemStatus.FAILED
            item.error = str(e)
            item.completed_at = datetime.utcnow()
            self._emit_event(f'{item.generation_type}.generation.failed', {
                "item": item.to_dict(),
                "generation_id": item.generation_id, 
                "error": item.error
            })
    
    def _process_llm_item(self, item: QueueItem, callback) -> Dict[str, Any]:
        """Process LLM generation using the LLM processor"""
        from backend.ai.llm.processor import process_request
        return process_request(item.generation_id, callback=callback)
    
    def _process_image_item(self, item: QueueItem, callback) -> Dict[str, Any]:
        """Process image generation using ComfyUI processor"""

        # Unload the LLM Model
        from backend.ai.llm.core import unload_model
        unload_model()

        from backend.ai.comfyui.processor import process_request
        return process_request(item.generation_id, callback=callback)
    
    def _worker_loop(self):
        """Main worker loop - processes queue items"""
        while self._running:
            try:
                try:
                    priority, generation_id = self._queue.get(timeout=1.0)
                except Empty:
                    continue
                
                with self._lock:
                    item = self._items.get(generation_id)
                
                if not item or item.status != QueueItemStatus.PENDING:
                    continue
                
                item.status = QueueItemStatus.PROCESSING
                item.started_at = datetime.utcnow()
                self._current_item = item
                
                self._emit_event(f'{item.generation_type}.generation.started', {
                    "item": item.to_dict(),
                    "generation_id": generation_id
                })
                
                print(f"🔄 Processing {item.generation_type} generation {generation_id}")
                self._process_item(item)
                self._current_item = None
                
            except Exception as e:
                print(f"❌ Worker error: {e}")
                if self._current_item:
                    self._current_item.status = QueueItemStatus.FAILED
                    self._current_item.error = str(e)
                    self._current_item = None

def get_ai_queue() -> AIGenerationQueue:
    """Get global AI generation queue instance"""
    global _global_queue
    with _queue_lock:
        if _global_queue is None:
            _global_queue = AIGenerationQueue()
            _global_queue.start_worker()
    return _global_queue

# Backwards compatibility aliases
def get_llm_queue() -> AIGenerationQueue:
    """Backwards compatibility - get AI queue"""
    return get_ai_queue()