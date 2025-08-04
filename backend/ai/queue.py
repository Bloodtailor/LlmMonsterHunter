# AI Generation Queue - UPDATED WITH UNIFIED QUEUE EVENTS
# Handles both LLM text generation and ComfyUI image generation
# Uses normalized generation_log database structure with unified queue events
print(f"🔍 Loading {__file__}")
import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime
from queue import Queue, Empty
from dataclasses import dataclass
from enum import Enum
from backend.core.utils import print_error
from backend.models.generation_log import GenerationLog
from backend.ai.llm.processor import process_llm_request
from backend.ai.llm.core import unload_model
from backend.ai.comfyui.processor import process_image_request

# Import event emission functions from new events package
from backend.core.events import (
    emit_llm_generation_started,
    emit_llm_generation_update,
    emit_llm_generation_completed,
    emit_llm_generation_failed,
    emit_image_generation_started,
    emit_image_generation_update,
    emit_image_generation_completed,
    emit_image_generation_failed,
    emit_ai_queue_update
)

_global_queue = None
_queue_lock = threading.Lock()

class QueueItemStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class QueueItem:
    """Queue item representing a generation request - ENHANCED with prompt details"""
    generation_id: int  # References generation_logs.id
    generation_type: str  # 'llm' or 'image'
    prompt_type: str  # From GenerationLog.prompt_type
    prompt_name: str  # From GenerationLog.prompt_name
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
            'prompt_type': self.prompt_type,
            'prompt_name': self.prompt_name,
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
    
    def add_request(self, generation_id: int) -> bool:
        """
        Add a generation request to the queue
        
        Args:
            generation_id (int): Database generation_logs.id
            
        Returns:
            bool: True if added successfully
        """
        
        try:
            # Get generation log entry (service layer already validated it exists)
            log_entry = GenerationLog.query.get(generation_id)
            
            if not log_entry:
                return False
            
            # Create queue item with enhanced data
            item = QueueItem(
                generation_id=generation_id,
                generation_type=log_entry.generation_type,
                prompt_type=log_entry.prompt_type,
                prompt_name=log_entry.prompt_name,
                priority=log_entry.priority,
                created_at=datetime.utcnow(),
                status=QueueItemStatus.PENDING
            )
            
            with self._lock:
                self._items[generation_id] = item
                # Priority queue: lower number = higher priority
                self._queue.put((log_entry.priority, generation_id))
            
            # Emit unified queue update event
            self._emit_queue_update('added')
            
            return True
            
        except Exception:
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
    
    def _emit_queue_update(self, trigger: str):
        """Emit unified queue update with only active items (pending or processing)"""
        with self._lock:
            # Filter to only active queue items
            active_items = [
                item.to_dict() for item in self._items.values() 
                if item.status in [QueueItemStatus.PENDING, QueueItemStatus.PROCESSING]
            ]
        
        emit_ai_queue_update(all_items=active_items, trigger=trigger)
    
    def _process_item(self, item: QueueItem):
        """Process a queue item by delegating to appropriate processor"""
        
        try:
            # Create streaming callback that emits events
            def on_stream(streaming_data):
                if item.generation_type == 'llm':
                    # For LLM, partial_data is partial text
                    emit_llm_generation_update(
                        generation_id=item.generation_id,
                        partial_text=streaming_data,
                        tokens_so_far=len(streaming_data.split()) if streaming_data else 0
                    )
                elif item.generation_type == 'image':
                    emit_image_generation_update(
                        item=item.to_dict(),
                        generation_id=item.generation_id,
                        elapsed_seconds=streaming_data
                    )
                    pass
            
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
                
                # Emit completion event using registry functions
                if item.generation_type == 'llm':
                    emit_llm_generation_completed(
                        item=item.to_dict(),
                        generation_id=item.generation_id,
                        result=result
                    )
                elif item.generation_type == 'image':
                    emit_image_generation_completed(
                        item=item.to_dict(),
                        generation_id=item.generation_id,
                        result=result
                    )
                
                # Emit unified queue update
                self._emit_queue_update('completed')
            else:
                item.status = QueueItemStatus.FAILED
                item.error = result.get('error', 'Unknown error')
                
                # Emit failure event using registry functions
                if item.generation_type == 'llm':
                    emit_llm_generation_failed(
                        item=item.to_dict(),
                        generation_id=item.generation_id,
                        error=item.error
                    )
                elif item.generation_type == 'image':
                    emit_image_generation_failed(
                        item=item.to_dict(),
                        generation_id=item.generation_id,
                        error=item.error
                    )
                
                # Emit unified queue update
                self._emit_queue_update('failed')
                
        except Exception as e:
            item.status = QueueItemStatus.FAILED
            item.error = str(e)
            item.completed_at = datetime.utcnow()
            
            # Emit failure event using registry functions
            if item.generation_type == 'llm':
                emit_llm_generation_failed(
                    item=item.to_dict(),
                    generation_id=item.generation_id,
                    error=item.error
                )
            elif item.generation_type == 'image':
                emit_image_generation_failed(
                    item=item.to_dict(),
                    generation_id=item.generation_id,
                    error=item.error
                )
            
            # Emit unified queue update
            self._emit_queue_update('failed')
    
    def _process_llm_item(self, item: QueueItem, callback) -> Dict[str, Any]:
        """Process LLM generation using the LLM processor"""
        return process_llm_request(item.generation_id, callback=callback)
    
    def _process_image_item(self, item: QueueItem, callback) -> Dict[str, Any]:
        """Process image generation using ComfyUI processor"""

        # Unload the LLM Model
        unload_model()
        return process_image_request(item.generation_id, callback=callback)
    
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
                
                # Emit started event using registry functions
                if item.generation_type == 'llm':
                    emit_llm_generation_started(
                        item=item.to_dict(),
                        generation_id=generation_id
                    )
                elif item.generation_type == 'image':
                    emit_image_generation_started(
                        item=item.to_dict(),
                        generation_id=generation_id
                    )
                
                # Emit unified queue update
                self._emit_queue_update('started')
                
                self._process_item(item)
                self._current_item = None
                
            except Exception as e:
                print_error(f"Worker error: {e}")
                if self._current_item:
                    self._current_item.status = QueueItemStatus.FAILED
                    self._current_item.error = str(e)
                    self._emit_queue_update('failed')
                    self._current_item = None

def get_ai_queue() -> AIGenerationQueue:
    """Get global AI generation queue instance"""
    global _global_queue
    with _queue_lock:
        if _global_queue is None:
            _global_queue = AIGenerationQueue()
            _global_queue.start_worker()
    return _global_queue