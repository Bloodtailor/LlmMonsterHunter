# Game Orchestration Queue - Multi-Step Workflow Processing
# Handles complex game workflows that call existing game logic
# Single worker thread processes workflows sequentially

import threading
import time
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from queue import Queue, Empty
from dataclasses import dataclass
from enum import Enum
from backend.core.utils import print_success, print_error, print_info
from backend.core.workflow_registry import get_workflow, list_workflows
from backend.models.game_workflow import GameWorkflow
from backend.core.events import (
    emit_workflow_started,
    emit_workflow_completed,
    emit_workflow_failed,
    emit_workflow_update,
    emit_workflow_queue_update
)

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

class WorkflowQueue:
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
        print("Game Orchestration Queue worker started")
    
    def stop_worker(self):
        """Stop background worker thread"""
        self._running = False
        if self._worker_thread:
            self._worker_thread.join(timeout=5)
    
    def add_workflow(self, workflow_type, context, priority) -> Optional[int]:
        """
        Add a workflow to the queue
        
        Args:
            workflow_type (str): Type of workflow ("monster_generation", "dungeon_entry", etc.)
            context (dict): Workflow context data
            priority (int): Queue priority (lower = higher priority)
            
        Returns:
            int: Workflow ID if successful, None if failed
        """
        
        try:
            # Create workflow database record
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
            
            # Emit workflow queue update
            self._emit_queue_update("added")
            
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
        print("Game Orchestration Queue worker loop started")
        
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
                
                # Emit workflow started event
                emit_workflow_started(item.to_dict(), item.workflow_id)
                self._emit_queue_update("started")
                
                # Process the workflow
                self._process_workflow(item)
                
            except Exception as e:
                print_error(f"Worker loop error: {e}")
                continue
            finally:
                # Clear current item
                self._current_item = None
    
    def _process_workflow(self, item: WorkflowItem):
        """Process a single workflow item"""
        try:
            # Get workflow handler
            handler = get_workflow(item.workflow_type)
            if not handler:
                raise Exception(f"No handler found for workflow type: {item.workflow_type}")
            
            # Create update callback for workflow progress
            def on_update(step: str, data: Dict[str, Any]):
                """Callback function for workflow progress updates"""
                emit_workflow_update(
                    workflow_id=item.workflow_id,
                    workflow_type=item.workflow_type,
                    step=step,
                    data=data
                )
            
            # Execute workflow with context and update callback
            result = handler(item.context, on_update)
            
            # Check result and update item status
            item.completed_at = datetime.utcnow()
            
            if result and result.get('success', False):
                item.status = WorkflowStatus.COMPLETED
                item.result = result
                
                # Emit workflow completed event
                emit_workflow_completed(item.to_dict(), item.workflow_id, result)
                self._emit_queue_update("completed")
                
                print_success(f"Completed workflow: {item.workflow_type} (ID: {item.workflow_id})")
            else:
                item.status = WorkflowStatus.FAILED
                item.error = result.get('error', 'Unknown error') if result else 'Handler returned None'
                
                # Emit workflow failed event
                emit_workflow_failed(item.to_dict(), item.workflow_id, item.error)
                self._emit_queue_update("failed")
                
                print_error(f"Failed workflow: {item.workflow_type} (ID: {item.workflow_id}) - {item.error}")
            
            # Update database
            self._update_workflow_database(item)
            
        except Exception as e:
            item.status = WorkflowStatus.FAILED
            item.error = str(e)
            item.completed_at = datetime.utcnow()
            
            # Emit workflow failed event
            emit_workflow_failed(item.to_dict(), item.workflow_id, item.error)
            self._emit_queue_update("failed")
            
            print_error(f"Workflow processing error: {e}")
            
            # Update database
            self._update_workflow_database(item)
    
    def _update_workflow_database(self, item: WorkflowItem):
        """Update workflow status in database"""
        try:
            workflow = GameWorkflow.query.get(item.workflow_id)
            if workflow:
                workflow.status = item.status.value
                workflow.result_data = item.result
                workflow.error_message = item.error
                workflow.completed_at = item.completed_at
                workflow.save()
                
        except Exception as e:
            print_error(f"Failed to update workflow database: {e}")
    
    def _emit_queue_update(self, trigger: str):
        """Emit workflow queue update event with all current items"""
        try:
            with self._lock:
                all_items = [
                    item.to_dict() for item in self._items.values() 
                    if item.status in [WorkflowStatus.PENDING, WorkflowStatus.PROCESSING]
            ]
            
            emit_workflow_queue_update(all_items, trigger)
            
        except Exception as e:
            print_error(f"Failed to emit queue update: {e}")

def get_queue() -> WorkflowQueue:
    """Get global game orchestration queue instance"""
    global _global_game_queue
    
    with _game_queue_lock:
        if _global_game_queue is None:
            _global_game_queue = WorkflowQueue()
            _global_game_queue.start_worker()
    
    return _global_game_queue