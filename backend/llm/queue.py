# LLM Queue - SIMPLIFIED
# Just queue management, much shorter

import threading
import time
import uuid
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from queue import Queue, Empty
from dataclasses import dataclass, asdict
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
    id: str
    prompt: str
    max_tokens: int
    temperature: float
    prompt_type: str
    created_at: datetime
    status: QueueItemStatus
    priority: int = 5
    log_id: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    partial_response: str = ""
    
    def to_dict(self):
        data = asdict(self)
        for field in ['created_at', 'started_at', 'completed_at']:
            if data[field]:
                data[field] = data[field].isoformat()
        data['status'] = data['status'].value
        return data

class LLMQueue:
    def __init__(self):
        self._queue = Queue()
        self._items = {}
        self._lock = threading.Lock()
        self._worker_thread = None
        self._running = False
        self._current_item = None
        self._callbacks = []
        self._app = None
        
    def set_flask_app(self, app):
        self._app = app
        
    def start_worker(self):
        if self._worker_thread and self._worker_thread.is_alive():
            return
        self._running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
    
    def add_request(self, prompt: str, max_tokens: int = 256, temperature: float = 0.8,
                   prompt_type: str = "unknown", priority: int = 5, log_id: Optional[int] = None) -> str:
        request_id = str(uuid.uuid4())
        
        item = QueueItem(
            id=request_id, prompt=prompt, max_tokens=max_tokens,
            temperature=temperature, prompt_type=prompt_type,
            created_at=datetime.utcnow(), status=QueueItemStatus.PENDING,
            priority=priority, log_id=log_id
        )
        
        with self._lock:
            self._items[request_id] = item
            self._queue.put((priority, request_id))
        
        self._notify("queue_update", {"action": "added", "item": item.to_dict()})
        return request_id
    
    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            item = self._items.get(request_id)
            return item.to_dict() if item else None
    
    def get_queue_status(self) -> Dict[str, Any]:
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
    
    def add_streaming_callback(self, callback: Callable):
        self._callbacks.append(callback)
    
    def _notify(self, event_type: str, data: Dict[str, Any]):
        event = {"type": event_type, "data": data, "timestamp": datetime.utcnow().isoformat()}
        for callback in self._callbacks[:]:  # Copy list to avoid issues
            try:
                callback(event)
            except:
                pass  # Ignore callback errors
    
    def _update_log(self, log_id: int, status: str, error_msg: str = None, text: str = None, tokens: int = None):
        if not log_id or not self._app:
            return
        try:
            with self._app.app_context():
                from backend.models.llm_log import LLMLog
                log = LLMLog.query.get(log_id)
                if not log:
                    return
                
                if status == 'started':
                    log.mark_started()
                elif status == 'completed':
                    log.mark_completed(text or "Completed", tokens or 0)
                elif status == 'failed':
                    log.mark_failed(error_msg or "Failed")
                log.save()
        except:
            pass  # Ignore log errors
    
    def _process_item(self, item: QueueItem):
        from backend.llm.core import ensure_model_loaded
        from backend.llm.inference import generate_streaming
        
        try:
            if not ensure_model_loaded():
                raise Exception("Model not loaded")
            
            def on_stream(partial_text):
                item.partial_response = partial_text
                self._notify("generation_update", {
                    "request_id": item.id,
                    "partial_text": partial_text,
                    "tokens_so_far": len(partial_text.split()) if partial_text else 0
                })
            
            result = generate_streaming(
                prompt=item.prompt,
                max_tokens=item.max_tokens,
                temperature=item.temperature,
                callback=on_stream
            )
            
            item.result = result
            item.completed_at = datetime.utcnow()
            
            if result['success']:
                item.status = QueueItemStatus.COMPLETED
                if item.log_id:
                    self._update_log(item.log_id, 'completed', None, result.get('text'), result.get('tokens'))
                self._notify("generation_completed", {
                    "item": item.to_dict(),
                    "final_text": result.get('text', ''),
                    "tokens_generated": result.get('tokens', 0),
                    "duration": result.get('duration', 0)
                })
            else:
                item.status = QueueItemStatus.FAILED
                item.error = result.get('error', 'Unknown error')
                if item.log_id:
                    self._update_log(item.log_id, 'failed', item.error)
                self._notify("generation_failed", {"item": item.to_dict(), "error": item.error})
                
        except Exception as e:
            item.status = QueueItemStatus.FAILED
            item.error = str(e)
            item.completed_at = datetime.utcnow()
            if item.log_id:
                self._update_log(item.log_id, 'failed', item.error)
            self._notify("generation_failed", {"item": item.to_dict(), "error": item.error})
    
    def _worker_loop(self):
        while self._running:
            try:
                try:
                    priority, request_id = self._queue.get(timeout=1.0)
                except Empty:
                    continue
                
                with self._lock:
                    item = self._items.get(request_id)
                
                if not item or item.status != QueueItemStatus.PENDING:
                    continue
                
                item.status = QueueItemStatus.PROCESSING
                item.started_at = datetime.utcnow()
                self._current_item = item
                
                if item.log_id:
                    self._update_log(item.log_id, 'started')
                
                self._notify("generation_started", {
                    "item": item.to_dict(),
                    "request_id": request_id
                })
                
                self._process_item(item)
                self._current_item = None
                
            except Exception as e:
                if self._current_item:
                    self._current_item.status = QueueItemStatus.FAILED
                    self._current_item.error = str(e)
                    self._current_item = None

def get_llm_queue() -> LLMQueue:
    global _global_queue
    with _queue_lock:
        if _global_queue is None:
            _global_queue = LLMQueue()
            _global_queue.start_worker()
    return _global_queue