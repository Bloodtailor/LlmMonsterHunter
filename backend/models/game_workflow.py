# Game Workflow Database Model - ORCHESTRATION TRACKING
# Tracks complex multi-step game workflows through the orchestration queue
# Stores workflow state, context, and results

from .core import db
from .base import BaseModel
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from datetime import datetime
from typing import Dict, Any

class GameWorkflow(BaseModel):
    """
    Game workflow model for tracking orchestrated multi-step operations
    
    Stores:
    - Workflow type and context data
    - Current status and priority
    - Final results and error information
    - Timing information for performance analysis
    """
    
    __tablename__ = 'game_workflows'
    
    # === Core Workflow Information ===
    workflow_type = Column(String(100), nullable=False)    # 'monster_basic', 'dungeon_entry', etc.
    context_data = Column(JSON, nullable=False)            # Workflow-specific context/parameters
    priority = Column(Integer, default=5, nullable=False)  # Queue priority (1=highest, 10=lowest)
    
    # === Workflow Status ===
    status = Column(String(50), default='pending', nullable=False)  # 'pending', 'processing', 'completed', 'failed'
    
    # === Results and Error Handling ===
    result_data = Column(JSON, nullable=True)              # Final workflow results
    error_message = Column(Text, nullable=True)            # Error details if failed
    
    # === Timing Information ===
    started_at = Column(DateTime, nullable=True)           # When processing began
    completed_at = Column(DateTime, nullable=True)         # When workflow finished
    
    def to_dict(self):
        """Convert workflow to dictionary for API responses"""
        result = super().to_dict()
        
        # Calculate duration if completed
        duration_seconds = None
        if self.started_at and self.completed_at:
            duration = self.completed_at - self.started_at
            duration_seconds = duration.total_seconds()
        
        # Add workflow-specific fields
        result.update({
            'workflow_type': self.workflow_type,
            'context_data': self.context_data,
            'priority': self.priority,
            'status': self.status,
            'result_data': self.result_data,
            'error_message': self.error_message,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_seconds': duration_seconds,
            'is_completed': self.status == 'completed',
            'is_failed': self.status == 'failed',
            'is_processing': self.status == 'processing'
        })
        
        return result
    
    def mark_started(self):
        """Mark workflow as started processing"""
        self.started_at = datetime.utcnow()
        self.status = 'processing'
    
    def mark_completed(self, result_data: Dict[str, Any]):
        """Mark workflow as completed successfully"""
        self.completed_at = datetime.utcnow()
        self.status = 'completed'
        self.result_data = result_data
        self.error_message = None
    
    def mark_failed(self, error_message: str):
        """Mark workflow as failed"""
        self.completed_at = datetime.utcnow()
        self.status = 'failed'
        self.error_message = error_message
    
    @classmethod
    def create_workflow(cls, workflow_type: str, context_data: Dict[str, Any], priority: int = 5):
        """
        Create a new workflow record
        
        Args:
            workflow_type (str): Type of workflow ('monster_basic', 'dungeon_entry', etc.)
            context_data (dict): Workflow context/parameters
            priority (int): Queue priority (1=highest, 10=lowest)
            
        Returns:
            GameWorkflow: New workflow instance (not yet saved)
        """
        return cls(
            workflow_type=workflow_type,
            context_data=context_data,
            priority=priority,
            status='pending'
        )
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<GameWorkflow(id={self.id}, type='{self.workflow_type}', status='{self.status}', priority={self.priority})>"