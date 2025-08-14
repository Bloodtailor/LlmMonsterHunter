# Game Workflow Database Model - ORCHESTRATION TRACKING
# Tracks complex multi-step game workflows through the orchestration queue
# Stores workflow state, context, and results

from .core import db
from .base import BaseModel
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from datetime import datetime
from typing import Dict, Any, Optional

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
    
    @classmethod
    def get_workflow_by_id(cls, workflow_id: int):
        """Get workflow by ID"""
        try:
            return cls.query.get(workflow_id)
        except Exception as e:
            print(f"❌ Error fetching workflow {workflow_id}: {e}")
            return None
    
    @classmethod
    def get_recent_workflows(cls, limit: int = 50, workflow_type: Optional[str] = None):
        """Get recent workflows, optionally filtered by type"""
        try:
            query = cls.query
            
            if workflow_type:
                query = query.filter_by(workflow_type=workflow_type)
            
            return query.order_by(cls.created_at.desc()).limit(limit).all()
        except Exception as e:
            print(f"❌ Error fetching recent workflows: {e}")
            return []
    
    @classmethod
    def get_pending_workflows(cls):
        """Get all pending workflows"""
        try:
            return cls.query.filter_by(status='pending').order_by(cls.priority.asc(), cls.created_at.asc()).all()
        except Exception as e:
            print(f"❌ Error fetching pending workflows: {e}")
            return []
    
    @classmethod
    def get_workflow_stats(cls):
        """Get workflow statistics for monitoring"""
        try:
            total = cls.query.count()
            completed = cls.query.filter_by(status='completed').count()
            failed = cls.query.filter_by(status='failed').count()
            pending = cls.query.filter_by(status='pending').count()
            processing = cls.query.filter_by(status='processing').count()
            
            # Get stats by workflow type
            from sqlalchemy import func
            type_stats = db.session.query(
                cls.workflow_type, 
                func.count(cls.id).label('count')
            ).group_by(cls.workflow_type).all()
            
            return {
                'total_workflows': total,
                'by_status': {
                    'pending': pending,
                    'processing': processing,
                    'completed': completed,
                    'failed': failed
                },
                'success_rate': round(completed / total * 100, 1) if total > 0 else 0,
                'by_type': {workflow_type: count for workflow_type, count in type_stats}
            }
        except Exception as e:
            print(f"❌ Error getting workflow stats: {e}")
            return {}
    
    @classmethod
    def cleanup_old_workflows(cls, days_old: int = 30):
        """Clean up old completed workflows (for maintenance)"""
        try:
            from datetime import timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            old_workflows = cls.query.filter(
                cls.completed_at < cutoff_date,
                cls.status.in_(['completed', 'failed'])
            ).all()
            
            count = len(old_workflows)
            for workflow in old_workflows:
                workflow.delete()
            
            return count
        except Exception as e:
            print(f"❌ Error cleaning up old workflows: {e}")
            return 0
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<GameWorkflow(id={self.id}, type='{self.workflow_type}', status='{self.status}', priority={self.priority})>"