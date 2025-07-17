# Game Orchestration Queue - Multi-Step Workflow Processing
# Handles complex game workflows that call existing game logic
# Single worker thread processes workflows sequentially
print("🔍 Loading orchestration queue")
import threading
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from queue import Queue, Empty
from dataclasses import dataclass
from enum import Enum
from backend.utils import print_success, print_error, print_info
from backend.core.workflow_registry import get_workflow, list_workflows

_global_game_queue = None
_game_queue_lock = threading.Lock()

class WorkflowStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class WorkflowItem:
    """Represents a game workflow in the queue"""
    workflow_id: int        # Database game_workflows.id
    workflow_type: str      # "monster_generation", "dungeon_entry", etc.
    context: Dict[str, Any] # Workflow-specific context data
    priority: int           # Queue priority (lower = higher priority)
    created_at: datetime
    status: WorkflowStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self):
        return {
            'workflow_id': self.workflow_id,
            'workflow_type': self.workflow_type,
            'context': self.context,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class GameOrchestrationQueue:
    """
    Orchestrates complex multi-step game workflows
    Single worker thread processes workflows by calling existing game logic
    """
    
    def __init__(self):
        self._queue = Queue()
        self._items = {}  # workflow_id -> WorkflowItem
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
        print_success("Game Orchestration Queue worker started")
    
    def stop_worker(self):
        """Stop background worker thread"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
    
    def add_workflow(self, workflow_type: str, context: Dict[str, Any] = {"content": "no content"}, priority: int = 5) -> Optional[int]:
        """
        Add a workflow to the queue
        
        Args:
            workflow_type (str): Type of workflow ("monster_generation", "dungeon_entry", etc.)
            context (dict): Workflow context data
            priority (int): Queue priority (lower = higher priority)
            
        Returns:
            int: Workflow ID if successful, None if failed
        """
        
        fn = get_workflow(workflow_type)
        if not fn:
            print_error(f"Unknown workflow type: {workflow_type}")
            return None
        
        try:
            # Create workflow database record
            from backend.models.game_workflow import GameWorkflow
            workflow = GameWorkflow.create_workflow(workflow_type, context, priority)
            
            if not workflow or not workflow.save():
                print_error(f"Failed to create workflow record for {workflow_type}")
                return None
            
            # Create queue item
            item = WorkflowItem(
                workflow_id=workflow.id,
                workflow_type=workflow_type,
                context=context,
                priority=priority,
                created_at=datetime.utcnow(),
                status=WorkflowStatus.PENDING
            )
            
            with self._lock:
                self._items[workflow.id] = item
                # Priority queue: lower number = higher priority
                self._queue.put((priority, workflow.id))
            
            # Emit event
            self._emit_event(f'workflow.{workflow_type}.queued', {
                "workflow_id": workflow.id,
                "workflow_type": workflow_type,
                "queue_size": self._queue.qsize()
            })
            
            print_success(f"Queued {workflow_type} workflow (ID: {workflow.id})")
            return workflow.id
            
        except Exception as e:
            print_error(f"Error adding workflow {workflow_type}: {e}")
            return None
    
    def get_workflow_status(self, workflow_id: int) -> Optional[Dict[str, Any]]:
        """Get status of a specific workflow"""
        with self._lock:
            item = self._items.get(workflow_id)
            return item.to_dict() if item else None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status"""
        with self._lock:
            items = list(self._items.values())
            
            # Count by status
            status_counts = {}
            for item in items:
                status = item.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by workflow type
            type_counts = {}
            for item in items:
                workflow_type = item.workflow_type
                type_counts[workflow_type] = type_counts.get(workflow_type, 0) + 1
            
            return {
                "queue_size": self._queue.qsize(),
                "total_workflows": len(items),
                "status_counts": status_counts,
                "type_counts": type_counts,
                "current_workflow": self._current_item.to_dict() if self._current_item else None,
                "worker_running": self._running,
                "supported_workflow_types": list_workflows()
            }
    
    def _worker_loop(self):
        """Main worker loop - processes workflows sequentially"""
        print_info("Game Orchestration Queue worker loop started")
        
        while self._running:
            try:
                try:
                    # Get next workflow from queue (with timeout)
                    priority, workflow_id = self._queue.get(timeout=1.0)
                except Empty:
                    continue
                
                with self._lock:
                    item = self._items.get(workflow_id)
                
                if not item or item.status != WorkflowStatus.PENDING:
                    continue
                
                # Mark as processing
                item.status = WorkflowStatus.PROCESSING
                item.started_at = datetime.utcnow()
                self._current_item = item
                
                print_info(f"Processing workflow: {item.workflow_type} (ID: {item.workflow_id})")
                
                # Emit started event
                self._emit_event(f'workflow.{item.workflow_type}.started', {
                    "workflow_id": item.workflow_id,
                    "workflow_type": item.workflow_type
                })
                
                # Process the workflow
                self._process_workflow(item)
                
                # Clear current item
                self._current_item = None
                
            except Exception as e:
                print_error(f"Workflow worker error: {e}")
                if self._current_item:
                    self._current_item.status = WorkflowStatus.FAILED
                    self._current_item.error = str(e)
                    self._current_item.completed_at = datetime.utcnow()
                    self._current_item = None
    
    def _process_workflow(self, item: WorkflowItem):
        """Process a single workflow by calling appropriate game logic"""
        
        try:
            # Ensure Flask app context for database operations
            if not self._app:
                raise Exception('No Flask app context available')
            
            with self._app.app_context():
                # Get the workflow handler
                handler = get_workflow(item.workflow_type)
                if not handler:
                    raise Exception(f'No handler for workflow type: {item.workflow_type}')
                
                # Call the handler (this will call existing game logic)
                result = handler(item.context)
                
                # Update item with result
                item.result = result
                item.completed_at = datetime.utcnow()
                
                if result.get('success', False):
                    item.status = WorkflowStatus.COMPLETED
                    
                    # Emit completion event
                    self._emit_event(f'workflow.{item.workflow_type}.completed', {
                        "workflow_id": item.workflow_id,
                        "workflow_type": item.workflow_type,
                        "result": result
                    })
                    
                    print_success(f"Completed workflow: {item.workflow_type} (ID: {item.workflow_id})")
                else:
                    item.status = WorkflowStatus.FAILED
                    item.error = result.get('error', 'Unknown error')
                    
                    # Emit failure event
                    self._emit_event(f'workflow.{item.workflow_type}.failed', {
                        "workflow_id": item.workflow_id,
                        "workflow_type": item.workflow_type,
                        "error": item.error
                    })
                    
                    print_error(f"Failed workflow: {item.workflow_type} (ID: {item.workflow_id}) - {item.error}")
                
                # Update database
                self._update_workflow_database(item)
                
        except Exception as e:
            item.status = WorkflowStatus.FAILED
            item.error = str(e)
            item.completed_at = datetime.utcnow()
            
            # Emit failure event
            self._emit_event(f'workflow.{item.workflow_type}.failed', {
                "workflow_id": item.workflow_id,
                "workflow_type": item.workflow_type,
                "error": item.error
            })
            
            print_error(f"Workflow processing error: {e}")
            
            # Update database
            self._update_workflow_database(item)
    
    def _update_workflow_database(self, item: WorkflowItem):
        """Update workflow status in database"""
        try:
            from backend.models.game_workflow import GameWorkflow
            
            workflow = GameWorkflow.query.get(item.workflow_id)
            if workflow:
                workflow.status = item.status.value
                workflow.result_data = item.result
                workflow.error_message = item.error
                workflow.completed_at = item.completed_at
                workflow.save()
                
        except Exception as e:
            print_error(f"Failed to update workflow database: {e}")
    
    def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit event using event service"""
        try:
            from backend.services.event_service import emit_event
            emit_event(event_type, data)
        except Exception as e:
            print_error(f"Failed to emit event {event_type}: {e}")

def get_game_orchestration_queue() -> GameOrchestrationQueue:
    """Get global game orchestration queue instance"""
    global _global_game_queue
    
    with _game_queue_lock:
        if _global_game_queue is None:
            _global_game_queue = GameOrchestrationQueue()
            _global_game_queue.start_worker()
    
    return _global_game_queue