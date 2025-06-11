# LLM Prompt Queue System
# Handles queuing multiple LLM requests and processing them sequentially
# 🔧 FIXED: Proper log status updates throughout the entire lifecycle

import threading
import time
import uuid
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from queue import Queue, Empty
from dataclasses import dataclass, asdict
from enum import Enum

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
    
    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Streaming
    streaming_callback: Optional[Callable] = None
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
        # Remove non-serializable callback
        data.pop('streaming_callback', None)
        return data

class LLMQueue:
    """
    Thread-safe LLM prompt queue with streaming support and MANDATORY logging
    🔧 FIXED: Proper Flask context handling for database operations
    """
    
    def __init__(self):
        self._queue = Queue()
        self._items = {}  # id -> QueueItem
        self._lock = threading.Lock()
        self._worker_thread = None
        self._running = False
        self._current_item = None
        self._streaming_callbacks = []  # Global streaming callbacks
        self._app = None  # 🔧 NEW: Store Flask app for context
        
    def set_flask_app(self, app):
        """🔧 NEW: Set Flask app for database operations"""
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
                   streaming_callback: Optional[Callable] = None,
                   log_id: Optional[int] = None) -> str:
        """
        Add a new request to the queue with optional log linking
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
            streaming_callback=streaming_callback,
            log_id=log_id
        )
        
        with self._lock:
            self._items[request_id] = item
            self._queue.put((priority, request_id))
        
        # Broadcast queue update
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
                if item.log_id:
                    self._update_log_status(item.log_id, 'cancelled', 'Request cancelled by user')
                
                self._notify_streaming("queue_update", {
                    "action": "cancelled", 
                    "item": item.to_dict(),
                    "queue_size": self._queue.qsize()
                })
                return True
        return False
    

    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status with proper counting"""
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
                status_key = item.status.value if hasattr(item.status, 'value') else str(item.status)
                if status_key in status_counts:
                    status_counts[status_key] += 1
            
            # Handle processing vs generating
            if self._current_item:
                status_counts['processing'] = 1
                if 'pending' in status_counts:
                    status_counts['pending'] = max(0, status_counts['pending'] - 1)
            
            return {
                "queue_size": self._queue.qsize(),
                "total_items": len(items),
                "status_counts": status_counts,
                "current_item": self._current_item.to_dict() if self._current_item else None,
                "worker_running": self._running,
                "active_connections": len(getattr(self, '_streaming_callbacks', []))
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
        
        # More robust callback handling
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
        
        # Debug output
        print(f"📡 Broadcast {event_type} to {len(self._streaming_callbacks)} connections")
    
    def _update_log_status(self, log_id: int, status: str, error_msg: str = None, response_text: str = None, tokens: int = None):
        """🔧 COMPLETELY REWRITTEN: Proper log status updates with Flask context"""
        if not log_id:
            return
            
        try:
            # 🔧 CRITICAL FIX: Ensure Flask app context
            if not self._app:
                print("⚠️ No Flask app available for log update")
                return
                
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
                elif status == 'failed':
                    log.mark_failed(error_msg or "Failed in queue")
                elif status == 'cancelled':
                    log.status = 'failed'
                    log.error_message = error_msg or "Cancelled"
                    log.end_time = datetime.utcnow()
                
                if log.save():
                    print(f"✅ Log {log_id} updated successfully: {status}")
                else:
                    print(f"❌ Failed to save log {log_id}")
                    
        except Exception as e:
            print(f"❌ Error updating log {log_id}: {e}")
            import traceback
            traceback.print_exc()
    
    def _worker_loop(self):
        """🔧 ENHANCED: Main worker loop with proper Flask context"""
        from backend.llm.core import generate_text, ensure_model_loaded
        
        print("🔄 LLM Queue worker loop started")
        
        while self._running:
            try:
                # Wait for next item (with timeout to check _running periodically)
                try:
                    priority, request_id = self._queue.get(timeout=1.0)
                except Empty:
                    continue
                
                # Get the item
                with self._lock:
                    item = self._items.get(request_id)
                
                if not item or item.status != QueueItemStatus.PENDING:
                    continue
                
                # 🔧 CRITICAL: Set up Flask context for this entire operation
                if self._app:
                    with self._app.app_context():
                        self._process_item(item, request_id)
                else:
                    print("⚠️ No Flask app context - processing without database updates")
                    self._process_item(item, request_id)
                    
            except Exception as e:
                print(f"❌ Worker loop error: {e}")
                import traceback
                traceback.print_exc()
                
                if self._current_item:
                    self._current_item.status = QueueItemStatus.FAILED
                    self._current_item.error = f"Worker error: {str(e)}"
                    self._current_item.completed_at = datetime.utcnow()
                    
                    # Update log
                    if self._current_item.log_id:
                        self._update_log_status(self._current_item.log_id, 'failed', self._current_item.error)
                    
                    self._notify_streaming("generation_failed", {
                        "item": self._current_item.to_dict(),
                        "error": self._current_item.error
                    })
                    self._current_item = None
    
    def _process_item(self, item, request_id):
        """🔧 NEW: Process a single queue item (extracted for cleaner code)"""
        from backend.llm.core import ensure_model_loaded
        
        # Mark as processing
        item.status = QueueItemStatus.PROCESSING
        item.started_at = datetime.utcnow()
        self._current_item = item
        
        # 🔧 Update log to started status
        if item.log_id:
            self._update_log_status(item.log_id, 'started')
        
        # Enhanced generation_started event
        self._notify_streaming("generation_started", {
            "item": item.to_dict(),
            "request_id": request_id,
            "prompt_type": item.prompt_type,
            "max_tokens": item.max_tokens
        })
        
        # Ensure model is loaded
        if not ensure_model_loaded():
            error_msg = "Failed to load LLM model"
            item.status = QueueItemStatus.FAILED
            item.error = error_msg
            item.completed_at = datetime.utcnow()
            self._current_item = None
            
            # 🔧 Update log to failed status
            if item.log_id:
                self._update_log_status(item.log_id, 'failed', error_msg)
            
            self._notify_streaming("generation_failed", {
                "item": item.to_dict(),
                "error": error_msg
            })
            return
        
        # Create streaming callback wrapper
        def streaming_wrapper(partial_text):
            item.partial_response = partial_text
            
            # Call item-specific callback
            if item.streaming_callback:
                try:
                    item.streaming_callback(partial_text)
                except Exception as e:
                    print(f"⚠️ Item streaming callback error: {e}")
            
            # Enhanced generation_update event
            self._notify_streaming("generation_update", {
                "request_id": request_id,
                "partial_text": partial_text,
                "item": item.to_dict(),
                "tokens_so_far": len(partial_text.split()) if partial_text else 0
            })
        
        # Generate with streaming
        print(f"🎲 Processing request {request_id}: {item.prompt_type}")
        
        result = self._generate_with_streaming(
            item.prompt,
            item.max_tokens,
            item.temperature,
            item.prompt_type,
            streaming_wrapper
        )
        
        # Update item with results
        item.result = result
        item.completed_at = datetime.utcnow()
        
        if result['success']:
            item.status = QueueItemStatus.COMPLETED
            
            # 🔧 Update log with full results
            if item.log_id:
                self._update_log_status(
                    item.log_id, 
                    'completed',
                    response_text=result.get('text', ''),
                    tokens=result.get('tokens', 0)
                )
            
            # Enhanced generation_completed event
            self._notify_streaming("generation_completed", {
                "item": item.to_dict(),
                "result": result,
                "final_text": result.get('text', ''),
                "tokens_generated": result.get('tokens', 0),
                "duration": result.get('duration', 0)
            })
        else:
            item.status = QueueItemStatus.FAILED
            item.error = result.get('error', 'Unknown error')
            
            # 🔧 Update log to failed status
            if item.log_id:
                self._update_log_status(item.log_id, 'failed', item.error)
            
            # Enhanced generation_failed event
            self._notify_streaming("generation_failed", {
                "item": item.to_dict(),
                "error": item.error,
                "result": result
            })
        
        self._current_item = None
        
        # Send queue status update after completion
        self._notify_streaming("queue_status", self.get_queue_status())
    
    def _generate_with_streaming(self, prompt: str, max_tokens: int, temperature: float,
                            prompt_type: str, streaming_callback: Callable) -> Dict[str, Any]:
        """
        Generate text with REAL streaming updates using llama-cpp-python streaming
        """
        from backend.llm.core import _model, _model_info, ensure_model_loaded
        import time
        
        # Ensure model is loaded
        if not ensure_model_loaded():
            return {
                'success': False,
                'error': 'Model not loaded',
                'text': None,
                'tokens': 0,
                'duration': 0
            }
        
        if not _model_info['loaded'] or _model is None:
            return {
                'success': False,
                'error': 'Model not available',
                'text': None,
                'tokens': 0,
                'duration': 0
            }
        
        try:
            print(f"🌊 Starting REAL streaming generation for {prompt_type}")
            start_time = time.time()
            
            # Configure generation parameters
            stop_sequences = ["</s>"]  # Simple stop sequence
            
            # Initialize streaming variables
            accumulated_text = ""
            token_count = 0
            
            # Call the streaming callback with empty initial state
            streaming_callback("")
            
            # Create the streaming generator
            stream = _model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=stop_sequences,
                echo=False,
                stream=True  # 🔥 Enable streaming!
            )
            
            # Process the stream with better error handling
            try:
                for output in stream:
                    try:
                        # Extract the token from the streaming output
                        if 'choices' in output and len(output['choices']) > 0:
                            choice = output['choices'][0]
                            
                            if 'text' in choice:
                                new_token = choice['text']
                                accumulated_text += new_token
                                token_count += 1
                                
                                # Send streaming update
                                streaming_callback(accumulated_text)
                                
                                # Small delay for visibility
                                time.sleep(0.01)  # 10ms delay
                                
                            # Check if we're done
                            if choice.get('finish_reason') is not None:
                                print(f"🏁 Streaming finished: {choice.get('finish_reason')}")
                                break
                                
                    except Exception as e:
                        print(f"⚠️ Error processing stream token: {e}")
                        continue
                        
            except Exception as e:
                print(f"❌ Error in streaming loop: {e}")
                # Continue with whatever we have so far
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ Streaming completed: {token_count} tokens in {duration:.1f}s")
            
            # Send final update
            streaming_callback(accumulated_text)
            
            return {
                'success': True,
                'error': None,
                'text': accumulated_text,
                'tokens': token_count,
                'duration': duration,
                'tokens_per_second': round(token_count / duration, 2) if duration > 0 else 0
            }
            
        except Exception as e:
            error_msg = f"Streaming generation failed: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'text': accumulated_text if 'accumulated_text' in locals() else None,
                'tokens': token_count if 'token_count' in locals() else 0,
                'duration': time.time() - start_time if 'start_time' in locals() else 0
            }

# Global queue instance
_global_queue = None
_queue_lock = threading.Lock()

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