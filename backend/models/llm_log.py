# LLM Log Database Model
# Stores all prompt/response pairs for debugging and monitoring
# Tracks model performance, parsing success/failure, and generation history

from backend.models.base import BaseModel
from backend.config.database import db
from sqlalchemy import Column, Integer, String, Text, JSON, Float, Boolean
from datetime import datetime

class LLMLog(BaseModel):
    """
    LLM Log model for storing all AI interactions
    
    Stores:
    - Prompt and response data
    - Model and generation settings
    - Timing and performance metrics
    - Parsing results and errors
    - Associated game entities (monsters, etc.)
    """
    
    __tablename__ = 'llm_logs'
    
    # Request Information
    prompt_type = Column(String(100), nullable=False)  # 'monster_generation', 'chat', etc.
    prompt_name = Column(String(100), nullable=False)  # Specific prompt used
    prompt_text = Column(Text, nullable=False)         # Full prompt sent to model
    
    # Model Configuration
    model_name = Column(String(200), nullable=True)    # Model file name
    max_tokens = Column(Integer, nullable=False)       # Token limit for generation
    temperature = Column(Float, default=0.8)          # Sampling temperature
    
    # Response Data
    response_text = Column(Text, nullable=True)        # Raw model response
    response_tokens = Column(Integer, nullable=True)   # Actual tokens generated
    
    # Timing Metrics
    start_time = Column(db.DateTime, nullable=False)   # When generation started
    end_time = Column(db.DateTime, nullable=True)      # When generation completed
    duration_seconds = Column(Float, nullable=True)    # Total generation time
    
    # Parsing Results
    parse_success = Column(Boolean, default=False)     # Did parsing succeed?
    parsed_data = Column(JSON, nullable=True)          # Successfully parsed JSON
    parse_error = Column(Text, nullable=True)          # Parsing error message
    parser_used = Column(String(100), nullable=True)   # Which parser was used
    
    # Status and Error Handling
    status = Column(String(50), default='pending')     # 'pending', 'generating', 'completed', 'failed'
    error_message = Column(Text, nullable=True)        # Any error that occurred
    
    # Game Entity Associations
    entity_type = Column(String(50), nullable=True)    # 'monster', 'chat', etc.
    entity_id = Column(Integer, nullable=True)         # ID of created entity
    
    def to_dict(self):
        """Convert to dictionary with additional computed fields"""
        result = super().to_dict()
        
        # Add computed fields
        result.update({
            'duration_seconds': self.duration_seconds,
            'tokens_per_second': self.get_tokens_per_second(),
            'is_completed': self.status == 'completed',
            'is_successful': self.parse_success and self.status == 'completed'
        })
        
        return result
    
    def get_tokens_per_second(self):
        """Calculate generation speed in tokens per second"""
        if self.duration_seconds and self.response_tokens:
            return round(self.response_tokens / self.duration_seconds, 2)
        return None
    
    def mark_started(self):
        """Mark the generation as started"""
        self.start_time = datetime.utcnow()
        self.status = 'generating'
    
    def mark_completed(self, response_text, response_tokens=None):
        """Mark the generation as completed"""
        self.end_time = datetime.utcnow()
        self.response_text = response_text
        self.response_tokens = response_tokens
        self.status = 'completed'
        
        if self.start_time:
            duration = self.end_time - self.start_time
            self.duration_seconds = duration.total_seconds()
    
    def mark_failed(self, error_message):
        """Mark the generation as failed"""
        self.end_time = datetime.utcnow()
        self.status = 'failed'
        self.error_message = error_message
        
        if self.start_time:
            duration = self.end_time - self.start_time
            self.duration_seconds = duration.total_seconds()
    
    def mark_parsed(self, parsed_data, parser_name):
        """Mark parsing as successful"""
        self.parse_success = True
        self.parsed_data = parsed_data
        self.parser_used = parser_name
    
    def mark_parse_failed(self, error_message, parser_name):
        """Mark parsing as failed"""
        self.parse_success = False
        self.parse_error = error_message
        self.parser_used = parser_name
    
    @classmethod
    def create_log(cls, prompt_type, prompt_name, prompt_text, max_tokens, **kwargs):
        """
        Create a new LLM log entry
        
        Args:
            prompt_type (str): Type of prompt ('monster_generation', etc.)
            prompt_name (str): Specific prompt name
            prompt_text (str): Full prompt text
            max_tokens (int): Maximum tokens to generate
            **kwargs: Additional fields (temperature, model_name, etc.)
        
        Returns:
            LLMLog: New log instance (not yet saved)
        """
        log = cls(
            prompt_type=prompt_type,
            prompt_name=prompt_name,
            prompt_text=prompt_text,
            max_tokens=max_tokens,
            start_time=datetime.utcnow(),
            status='pending',
            **kwargs
        )
        
        return log
    
    @classmethod
    def get_recent_logs(cls, limit=50):
        """Get recent LLM logs for monitoring"""
        try:
            return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
        except Exception as e:
            print(f"❌ Error fetching recent logs: {e}")
            return []
    
    @classmethod
    def get_current_generation(cls):
        """Get the currently running generation, if any"""
        try:
            return cls.query.filter_by(status='generating').first()
        except Exception as e:
            print(f"❌ Error fetching current generation: {e}")
            return None
    
    @classmethod
    def get_stats(cls):
        """Get generation statistics"""
        try:
            total = cls.query.count()
            completed = cls.query.filter_by(status='completed').count()
            failed = cls.query.filter_by(status='failed').count()
            successful_parse = cls.query.filter_by(parse_success=True).count()
            
            return {
                'total_generations': total,
                'completed': completed,
                'failed': failed,
                'success_rate': round(completed / total * 100, 1) if total > 0 else 0,
                'parse_success_rate': round(successful_parse / total * 100, 1) if total > 0 else 0
            }
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {}
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<LLMLog(id={self.id}, type='{self.prompt_type}', status='{self.status}')>"