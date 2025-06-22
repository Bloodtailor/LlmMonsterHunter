# Image Log Child Table - ComfyUI-Specific Data
# Contains only image generation parameters, workflow info, and results
# Linked to GenerationLog parent table

from backend.models.base import BaseModel
from backend.config.database import db
from sqlalchemy import Column, Integer, String, Text, JSON, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from typing import Dict, Any, Optional

class ImageLog(BaseModel):
    """
    Image-specific generation data - child table of GenerationLog
    Contains ComfyUI workflow parameters, generation metadata, and image results
    """
    
    __tablename__ = 'image_logs'
    
    # === Foreign Key to Parent ===
    generation_id = Column(Integer, ForeignKey('generation_logs.id'), nullable=False, unique=True)
    generation_log = relationship("GenerationLog", back_populates="image_log")
    
    # === ComfyUI Generation Parameters ===
    workflow_name = Column(String(100), nullable=False)    # e.g., "monster_generation"
    monster_name = Column(String(100), nullable=True)      # Monster name for prompt
    monster_species = Column(String(100), nullable=True)   # Monster species for prompt
    
    # === Generation Configuration ===
    seed = Column(Integer, nullable=True)                  # Random seed used
    steps = Column(Integer, nullable=True)                 # Generation steps
    cfg_scale = Column(Float, nullable=True)               # CFG scale
    width = Column(Integer, nullable=True)                 # Image width
    height = Column(Integer, nullable=True)                # Image height
    
    # === ComfyUI Workflow Data ===
    workflow_metadata = Column(JSON, nullable=True)        # Full workflow JSON
    positive_prompt = Column(Text, nullable=True)          # Final positive prompt used
    negative_prompt = Column(Text, nullable=True)          # Negative prompt used
    
    # === ComfyUI Processing ===
    comfyui_prompt_id = Column(String(100), nullable=True) # ComfyUI prompt ID
    comfyui_execution_time = Column(Float, nullable=True)  # ComfyUI execution time
    
    # === Image Results ===
    image_path = Column(String(500), nullable=True)        # Path to generated image
    image_filename = Column(String(200), nullable=True)    # Just the filename
    image_size_bytes = Column(Integer, nullable=True)      # File size in bytes
    
    # === Generation Metadata ===
    generation_metadata = Column(JSON, nullable=True)      # Additional metadata from ComfyUI
    model_used = Column(String(200), nullable=True)        # Specific model checkpoint used
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        result = super().to_dict()
        
        # Add computed fields
        result.update({
            'generation_id': self.generation_id,
            'workflow_name': self.workflow_name,
            'monster_name': self.monster_name,
            'monster_species': self.monster_species,
            'image_path': self.image_path,
            'image_filename': self.image_filename,
            'comfyui_prompt_id': self.comfyui_prompt_id,
            'comfyui_execution_time': self.comfyui_execution_time,
            'generation_params': self.get_generation_params(),
            'has_image': bool(self.image_path),
            'image_size_mb': round(self.image_size_bytes / 1024 / 1024, 2) if self.image_size_bytes else None
        })
        
        return result
    
    def get_generation_params(self):
        """
        Get image generation parameters as dictionary
        """
        return {
            'workflow_name': self.workflow_name,
            'seed': self.seed,
            'steps': self.steps,
            'cfg_scale': self.cfg_scale,
            'width': self.width,
            'height': self.height,
            'positive_prompt': self.positive_prompt,
            'negative_prompt': self.negative_prompt,
            'model_used': self.model_used
        }
    
    def mark_image_generated(self, image_path: str, 
                            comfyui_prompt_id: str = None,
                            execution_time: float = None,
                            metadata: Dict[str, Any] = None):
        """Mark image generation as completed with results"""
        self.image_path = image_path
        self.comfyui_prompt_id = comfyui_prompt_id
        self.comfyui_execution_time = execution_time
        
        if metadata:
            self.generation_metadata = metadata
        
        # Extract filename from path
        if image_path:
            from pathlib import Path
            self.image_filename = Path(image_path).name
            
            # Get file size if possible
            try:
                file_path = Path(image_path)
                if file_path.exists():
                    self.image_size_bytes = file_path.stat().st_size
            except Exception as e:
                print(f"⚠️ Could not get image file size: {e}")
    
    def update_workflow_results(self, workflow_metadata: Dict[str, Any], 
                               positive_prompt: str = None,
                               negative_prompt: str = None):
        """Update workflow execution results"""
        self.workflow_metadata = workflow_metadata
        
        if positive_prompt:
            self.positive_prompt = positive_prompt
        
        if negative_prompt:
            self.negative_prompt = negative_prompt
    
    @classmethod
    def create_from_params(cls, image_params: Dict[str, Any]):
        """
        Create Image log from image parameters
        
        Args:
            image_params (dict): Image generation parameters
            
        Returns:
            ImageLog: New image log instance (not yet saved)
        """
        return cls(
            # Core generation info
            workflow_name=image_params.get('workflow_name', 'monster_generation'),
            monster_name=image_params.get('monster_name', ''),
            monster_species=image_params.get('monster_species', ''),
            
            # Generation parameters (will be filled in during processing)
            seed=image_params.get('seed'),
            steps=image_params.get('steps'),
            cfg_scale=image_params.get('cfg_scale'),
            width=image_params.get('width', 1024),
            height=image_params.get('height', 1024),
            
            # Metadata
            generation_metadata=image_params.get('metadata', {}),
            
            # Initialize as not yet generated
            image_path=None,
            comfyui_prompt_id=None,
            comfyui_execution_time=None
        )
    
    @classmethod
    def get_by_generation_id(cls, generation_id: int):
        """Get Image log by generation ID"""
        return cls.query.filter_by(generation_id=generation_id).first()
    
    @classmethod
    def get_recent_with_images(cls, limit: int = 20):
        """Get recent image logs that have generated images"""
        return cls.query.filter(cls.image_path.isnot(None)).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_by_monster_info(cls, monster_name: str = None, monster_species: str = None):
        """Get image logs for specific monster name/species"""
        query = cls.query
        
        if monster_name:
            query = query.filter(cls.monster_name.ilike(f'%{monster_name}%'))
        
        if monster_species:
            query = query.filter(cls.monster_species.ilike(f'%{monster_species}%'))
        
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_workflow_stats(cls):
        """Get workflow usage statistics"""
        try:
            total_images = cls.query.count()
            successful_generations = cls.query.filter(cls.image_path.isnot(None)).count()
            
            # Get workflow usage counts
            from sqlalchemy import func
            workflow_counts = db.session.query(
                cls.workflow_name,
                func.count(cls.id).label('count')
            ).group_by(cls.workflow_name).all()
            
            return {
                'total_image_requests': total_images,
                'successful_generations': successful_generations,
                'success_rate': round(successful_generations / total_images * 100, 1) if total_images > 0 else 0,
                'failed_generations': total_images - successful_generations,
                'workflow_usage': {workflow: count for workflow, count in workflow_counts}
            }
        except Exception as e:
            print(f"❌ Error getting workflow stats: {e}")
            return {}
    
    @classmethod
    def get_average_execution_time(cls):
        """Get average ComfyUI execution time"""
        try:
            from sqlalchemy import func
            avg_time = db.session.query(func.avg(cls.comfyui_execution_time)).filter(
                cls.comfyui_execution_time.isnot(None)
            ).scalar()
            
            return round(avg_time, 2) if avg_time else None
        except Exception as e:
            print(f"❌ Error getting average execution time: {e}")
            return None
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<ImageLog(id={self.id}, generation_id={self.generation_id}, workflow='{self.workflow_name}', has_image={bool(self.image_path)})>"