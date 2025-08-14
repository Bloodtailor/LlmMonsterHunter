# LLM Log Child Table - LLM-Specific Data
# Contains only LLM inference parameters, responses, and parsing data
# Linked to GenerationLog parent table

from backend.models.base import BaseModel
from backend.core.config.database import db
from sqlalchemy import Column, Integer, String, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from typing import Dict, Any, Optional

class LLMLog(BaseModel):
    """
    LLM-specific generation data - child table of GenerationLog
    Contains all inference parameters, parsing config, and LLM responses
    """
    
    __tablename__ = 'llm_logs'
    
    # === Foreign Key to Parent ===
    generation_id = Column(Integer, ForeignKey('generation_logs.id'), nullable=False, unique=True)
    generation_log = relationship("GenerationLog", back_populates="llm_log")
    
    # === LLM Inference Parameters ===
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
    
    # === Model Information ===
    model_name = Column(String(200), nullable=True)    # Model file name
    
    # === LLM Response Data ===
    response_text = Column(Text, nullable=True)        # Raw model response (latest attempt)
    response_tokens = Column(Integer, nullable=True)   # Tokens generated (latest attempt)
    tokens_per_second = Column(Float, nullable=True)   # Generation speed
    
    # === Parsing Configuration and Results ===
    parser_config = Column(JSON, nullable=True)        # Parser configuration used
    parse_success = Column(Boolean, default=False)     # Did parsing succeed?
    parsed_data = Column(JSON, nullable=True)          # Successfully parsed JSON
    parse_error = Column(Text, nullable=True)          # Parsing error message
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        result = super().to_dict()
        
        # Add computed fields
        result.update({
            'generation_id': self.generation_id,
            'model_name': self.model_name,
            'response_tokens': self.response_tokens,
            'tokens_per_second': self.tokens_per_second,
            'parse_success': self.parse_success,
            'inference_params': self.get_inference_params(),
            'has_response': bool(self.response_text),
            'has_parsed_data': bool(self.parsed_data)
        })
        
        return result
    
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
    
    def mark_response_completed(self, response_text: str, response_tokens: int = None, tokens_per_second: float = None):
        """Mark LLM response as completed"""
        self.response_text = response_text
        self.response_tokens = response_tokens
        self.tokens_per_second = tokens_per_second
    
    def mark_parsed(self, parsed_data: Any):
        """Mark parsing as successful"""
        self.parse_success = True
        self.parsed_data = parsed_data
        self.parse_error = None
    
    def mark_parse_failed(self, error_message: str):
        """Mark parsing as failed"""
        self.parse_success = False
        self.parse_error = error_message
        # Keep parsed_data as None
    
    def reset_parse_status(self):
        """Reset parsing status for retry"""
        self.parse_success = False
        self.parse_error = None
        self.parsed_data = None
    
    @classmethod
    def create_from_params(cls, inference_params: Dict[str, Any], parser_config: Optional[Dict[str, Any]] = None):
        """
        Create LLM log from inference parameters
        
        Args:
            inference_params (dict): All inference parameters
            parser_config (dict): Parser configuration
            
        Returns:
            LLMLog: New LLM log instance (not yet saved)
        """
        return cls(
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
            
            # Store parser configuration
            parser_config=parser_config,
            
            # Initialize parsing state
            parse_success=False,
            parsed_data=None,
            parse_error=None
        )
    
    @classmethod
    def get_by_generation_id(cls, generation_id: int):
        """Get LLM log by generation ID"""
        return cls.query.filter_by(generation_id=generation_id).first()
    
    @classmethod
    def get_recent_with_responses(cls, limit: int = 20):
        """Get recent LLM logs that have responses"""
        return cls.query.filter(cls.response_text.isnot(None)).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_parsing_stats(cls):
        """Get parsing success statistics"""
        try:
            total_with_responses = cls.query.filter(cls.response_text.isnot(None)).count()
            successful_parses = cls.query.filter_by(parse_success=True).count()
            
            return {
                'total_with_responses': total_with_responses,
                'successful_parses': successful_parses,
                'parse_success_rate': round(successful_parses / total_with_responses * 100, 1) if total_with_responses > 0 else 0,
                'failed_parses': total_with_responses - successful_parses
            }
        except Exception as e:
            print(f"❌ Error getting parsing stats: {e}")
            return {}
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<LLMLog(id={self.id}, generation_id={self.generation_id}, tokens={self.response_tokens}, parsed={self.parse_success})>"