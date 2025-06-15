# LLM Log Database Model - COMPLETE PARAMETER STORAGE
# Stores ALL inference parameters, queue settings, and generation attempts
# Single source of truth for all LLM operations

from backend.models.base import BaseModel
from backend.config.database import db
from sqlalchemy import Column, Integer, String, Text, JSON, Float, Boolean
from datetime import datetime

class LLMLog(BaseModel):
    """
    Complete LLM Log model - stores everything needed for inference
    
    Philosophy: Store all parameters in database, pass only log_id between modules
    This gives us complete audit trail and eliminates parameter passing
    """
    
    __tablename__ = 'llm_logs'
    
    # === Request Information ===
    prompt_type = Column(String(100), nullable=False)  # 'monster_generation', 'chat', etc.
    prompt_name = Column(String(100), nullable=False)  # Specific prompt used
    prompt_text = Column(Text, nullable=False)         # Full prompt sent to model
    
    # === All Inference Parameters (stored for audit and retry) ===
    max_tokens = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    top_p = Column(Float, nullable=False)
    top_k = Column(Integer, nullable=False)
    repeat_penalty = Column(Float, nullable=False)
    frequency_penalty = Column(Float, nullable=False)
    presence_penalty = Column(Float, nullable=False)
    tfs_z = Column(Float, nullable=False)
    typical_p = Column(Float, nullable=False)
    mirostat_mode = Column(Integer, nullable=False)
    mirostat_tau = Column(Float, nullable=False)
    mirostat_eta = Column(Float, nullable=False)
    seed = Column(Integer, nullable=False)
    stop_sequences = Column(JSON, nullable=False)      # List of stop sequences
    echo = Column(Boolean, nullable=False)
    
    # === Queue Parameters ===
    priority = Column(Integer, nullable=False)
    
    # === Model Information ===
    model_name = Column(String(200), nullable=True)    # Model file name
    
    # === Generation Tracking ===
    generation_attempt = Column(Integer, default=1)    # Current attempt (1, 2, or 3)
    max_attempts = Column(Integer, default=3)          # Maximum attempts allowed
    
    # === Response Data (updated each attempt) ===
    response_text = Column(Text, nullable=True)        # Raw model response (latest attempt)
    response_tokens = Column(Integer, nullable=True)   # Tokens generated (latest attempt)
    
    # === Timing Metrics ===
    start_time = Column(db.DateTime, nullable=False)   # When generation started
    end_time = Column(db.DateTime, nullable=True)      # When generation completed
    duration_seconds = Column(Float, nullable=True)    # Total generation time
    
    # === Parsing Results ===
    parse_success = Column(Boolean, default=False)     # Did parsing succeed?
    parsed_data = Column(JSON, nullable=True)          # Successfully parsed JSON
    parse_error = Column(Text, nullable=True)          # Parsing error message
    parser_config = Column(JSON, nullable=True)        # Parser configuration used
    
    # === Status and Error Handling ===
    status = Column(String(50), default='pending')     # 'pending', 'generating', 'completed', 'failed'
    error_message = Column(Text, nullable=True)        # Any error that occurred
    
    def to_dict(self):
        """Convert to dictionary with additional computed fields"""
        result = super().to_dict()
        
        # Add computed fields
        result.update({
            'duration_seconds': self.duration_seconds,
            'tokens_per_second': self.get_tokens_per_second(),
            'is_completed': self.status == 'completed',
            'is_successful': self.parse_success and self.status == 'completed',
            'attempts_remaining': max(0, self.max_attempts - self.generation_attempt)
        })
        
        return result
    
    def get_tokens_per_second(self):
        """Calculate generation speed in tokens per second"""
        if self.duration_seconds and self.response_tokens:
            return round(self.response_tokens / self.duration_seconds, 2)
        return None
    
    def get_inference_params(self):
        """
        Get all inference parameters as a dictionary
        Perfect for passing to inference functions
        """
        return {
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'top_k': self.top_k,
            'repeat_penalty': self.repeat_penalty,
            'frequency_penalty': self.frequency_penalty,
            'presence_penalty': self.presence_penalty,
            'tfs_z': self.tfs_z,
            'typical_p': self.typical_p,
            'mirostat_mode': self.mirostat_mode,
            'mirostat_tau': self.mirostat_tau,
            'mirostat_eta': self.mirostat_eta,
            'seed': self.seed,
            'stop': self.stop_sequences,
            'echo': self.echo
        }
    
    def mark_started(self):
        """Mark the generation as started"""
        self.start_time = datetime.utcnow()
        self.status = 'generating'
    
    def mark_attempt_completed(self, response_text, response_tokens=None):
        """Mark current attempt as completed (may retry)"""
        self.response_text = response_text
        self.response_tokens = response_tokens
        
        # Update timing for this attempt
        if self.start_time:
            self.end_time = datetime.utcnow()
            duration = self.end_time - self.start_time
            self.duration_seconds = duration.total_seconds()
    
    def mark_generation_completed(self):
        """Mark entire generation as completed (no more retries)"""
        self.status = 'completed'
        if not self.end_time:
            self.end_time = datetime.utcnow()
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
    
    def mark_parsed(self, parsed_data):
        """Mark parsing as successful"""
        self.parse_success = True
        self.parsed_data = parsed_data
        self.parse_error = None
    
    def mark_parse_failed(self, error_message):
        """Mark parsing as failed"""
        self.parse_success = False
        self.parse_error = error_message
    
    def increment_attempt(self):
        """Increment generation attempt counter"""
        self.generation_attempt += 1
        self.parse_success = False
        self.parse_error = None
    
    def can_retry(self):
        """Check if more attempts are allowed"""
        return self.generation_attempt < self.max_attempts
    
    @classmethod
    def create_complete_log(cls, prompt_type, prompt_name, prompt_text, 
                           inference_params, parser_config=None, **kwargs):
        """
        Create a new LLM log entry with ALL parameters
        
        Args:
            prompt_type (str): Type of prompt
            prompt_name (str): Specific prompt name
            prompt_text (str): Full prompt text
            inference_params (dict): ALL inference parameters
            parser_config (dict): Parser configuration
            **kwargs: Additional fields
        
        Returns:
            LLMLog: New log instance (not yet saved)
        """
        log = cls(
            prompt_type=prompt_type,
            prompt_name=prompt_name,
            prompt_text=prompt_text,
            start_time=datetime.utcnow(),
            status='pending',
            generation_attempt=1,
            
            # Store all inference parameters
            max_tokens=inference_params['max_tokens'],
            temperature=inference_params['temperature'],
            top_p=inference_params['top_p'],
            top_k=inference_params['top_k'],
            repeat_penalty=inference_params['repeat_penalty'],
            frequency_penalty=inference_params['frequency_penalty'],
            presence_penalty=inference_params['presence_penalty'],
            tfs_z=inference_params['tfs_z'],
            typical_p=inference_params['typical_p'],
            mirostat_mode=inference_params['mirostat_mode'],
            mirostat_tau=inference_params['mirostat_tau'],
            mirostat_eta=inference_params['mirostat_eta'],
            seed=inference_params['seed'],
            stop_sequences=inference_params['stop'],
            echo=inference_params['echo'],
            priority=inference_params['priority'],
            
            # Store parser config
            parser_config=parser_config,
            
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
        return f"<LLMLog(id={self.id}, type='{self.prompt_type}', attempt={self.generation_attempt}, status='{self.status}')>"