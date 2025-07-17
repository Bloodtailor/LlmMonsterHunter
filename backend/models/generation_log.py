# Generation Log Base Model - NORMALIZED DATABASE DESIGN
# Parent table for all generation types with separate child tables
# Follows database normalization principles
print(f"🔍 Loading {__file__}")
from backend.models.base import BaseModel
from backend.core.config.database import db
from sqlalchemy import Column, Integer, String, Text, JSON, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, Optional

class GenerationLog(BaseModel):
    """
    Base generation log - parent table for all generation types
    Contains common fields shared by all generation types
    
    Child tables: LLMLog, ImageLog (and future: AudioLog, etc.)
    """
    
    __tablename__ = 'generation_logs'
    
    # === Core Generation Information ===
    generation_type = Column(String(50), nullable=False)  # 'llm', 'image', 'audio', etc.
    prompt_type = Column(String(100), nullable=False)     # 'monster_generation', 'ability_generation', etc.
    prompt_name = Column(String(100), nullable=False)     # Specific prompt/template used
    prompt_text = Column(Text, nullable=False)            # Full prompt text
    
    # === Generation Tracking ===
    status = Column(String(50), default='pending', nullable=False)  # 'pending', 'generating', 'completed', 'failed'
    priority = Column(Integer, default=5, nullable=False)           # Queue priority (1=highest, 10=lowest)
    
    generation_attempt = Column(Integer, default=1, nullable=False)  # Current attempt number
    max_attempts = Column(Integer, default=3, nullable=False)        # Maximum attempts allowed
    
    # === Timing Metrics ===
    start_time = Column(DateTime, nullable=True)          # When generation started
    end_time = Column(DateTime, nullable=True)            # When generation completed
    duration_seconds = Column(Float, nullable=True)       # Total generation time
    
    # === Status and Error Handling ===
    error_message = Column(Text, nullable=True)           # Any error that occurred
    
    # === Relationships to Child Tables ===
    llm_log = relationship("LLMLog", back_populates="generation_log", uselist=False, cascade="all, delete-orphan")
    image_log = relationship("ImageLog", back_populates="generation_log", uselist=False, cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary with child data included"""
        result = super().to_dict()
        
        # Add computed fields
        result.update({
            'generation_type': self.generation_type,
            'prompt_type': self.prompt_type,
            'prompt_name': self.prompt_name,
            'status': self.status,
            'priority': self.priority,
            'duration_seconds': self.duration_seconds,
            'attempts_used': self.generation_attempt,
            'max_attempts': self.max_attempts,
            'is_completed': self.status == 'completed',
            'is_failed': self.status == 'failed'
        })
        
        # Include child table data
        if self.llm_log:
            result['llm_data'] = self.llm_log.to_dict()
        
        if self.image_log:
            result['image_data'] = self.image_log.to_dict()
        
        return result
    
    def mark_started(self):
        """Mark generation as started"""
        self.start_time = datetime.utcnow()
        self.status = 'generating'
    
    def mark_completed(self):
        """Mark generation as completed"""
        self.end_time = datetime.utcnow()
        self.status = 'completed'
        
        if self.start_time:
            duration = self.end_time - self.start_time
            self.duration_seconds = duration.total_seconds()
    
    def mark_failed(self, error_message: str):
        """Mark generation as failed"""
        self.end_time = datetime.utcnow()
        self.status = 'failed'
        self.error_message = error_message
        
        if self.start_time:
            duration = self.end_time - self.start_time
            self.duration_seconds = duration.total_seconds()
    
    def increment_attempt(self):
        """Increment attempt counter"""
        self.generation_attempt += 1
    
    def can_retry(self) -> bool:
        """Check if more attempts are allowed"""
        return self.generation_attempt < self.max_attempts
    
    def get_child_data(self):
        """Get the appropriate child table data"""
        if self.generation_type == 'llm' and self.llm_log:
            return self.llm_log
        elif self.generation_type == 'image' and self.image_log:
            return self.image_log
        return None
    
    @classmethod
    def create_llm_log(cls, prompt_type: str, prompt_name: str, prompt_text: str, 
                       inference_params: Dict[str, Any], parser_config: Optional[Dict[str, Any]] = None, 
                       **kwargs):
        """
        Create a new LLM generation log with child LLM data
        
        Args:
            prompt_type (str): Type of prompt
            prompt_name (str): Specific prompt name
            prompt_text (str): Full prompt text
            inference_params (dict): All inference parameters
            parser_config (dict): Parser configuration
            **kwargs: Additional fields
            
        Returns:
            GenerationLog: New generation log with LLM child data (not yet saved)
        """
        # Create parent log
        generation_log = cls(
            generation_type='llm',
            prompt_type=prompt_type,
            prompt_name=prompt_name,
            prompt_text=prompt_text,
            status='pending',
            generation_attempt=1,
            priority=inference_params.get('priority', 5),
            max_attempts=kwargs.get('max_attempts', 3)
        )
        
        # Create child LLM log (will be saved when parent is saved due to cascade)
        from backend.models.llm_log import LLMLog
        llm_data = LLMLog.create_from_params(inference_params, parser_config)
        generation_log.llm_log = llm_data
        
        return generation_log
    
    @classmethod
    def create_image_log(cls, prompt_type: str, prompt_name: str, prompt_text: str,
                        image_params: Dict[str, Any], **kwargs):
        """
        Create a new image generation log with child image data
        
        Args:
            prompt_type (str): Type of prompt
            prompt_name (str): Specific prompt name (workflow name)
            prompt_text (str): Monster description or image prompt
            image_params (dict): Image generation parameters
            **kwargs: Additional fields
            
        Returns:
            GenerationLog: New generation log with image child data (not yet saved)
        """
        # Create parent log
        generation_log = cls(
            generation_type='image',
            prompt_type=prompt_type,
            prompt_name=prompt_name,
            prompt_text=prompt_text,
            status='pending',
            generation_attempt=1,
            priority=kwargs.get('priority', 7),  # Lower priority than LLM
            max_attempts=kwargs.get('max_attempts', 2)  # Fewer retries for images
        )
        
        # Create child image log
        from backend.models.image_log import ImageLog
        image_data = ImageLog.create_from_params(image_params)
        generation_log.image_log = image_data
        
        return generation_log
    
    @classmethod
    def get_pending_by_type(cls, generation_type: str):
        """Get all pending logs of a specific type"""
        return cls.query.filter_by(
            generation_type=generation_type,
            status='pending'
        ).order_by(cls.priority.asc(), cls.created_at.asc()).all()
    
    @classmethod
    def get_recent_logs(cls, limit: int = 50, generation_type: Optional[str] = None):
        """Get recent logs, optionally filtered by type"""
        query = cls.query
        
        if generation_type:
            query = query.filter_by(generation_type=generation_type)
        
        return query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_stats(cls):
        """Get generation statistics across all types"""
        try:
            total = cls.query.count()
            completed = cls.query.filter_by(status='completed').count()
            failed = cls.query.filter_by(status='failed').count()
            
            # Stats by type
            llm_count = cls.query.filter_by(generation_type='llm').count()
            image_count = cls.query.filter_by(generation_type='image').count()
            
            return {
                'total_generations': total,
                'completed': completed,
                'failed': failed,
                'success_rate': round(completed / total * 100, 1) if total > 0 else 0,
                'by_type': {
                    'llm': llm_count,
                    'image': image_count
                }
            }
        except Exception as e:
            print(f"❌ Error getting generation stats: {e}")
            return {}
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<GenerationLog(id={self.id}, type='{self.generation_type}', status='{self.status}', attempt={self.generation_attempt})>"