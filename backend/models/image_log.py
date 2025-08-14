# Image Log Child Table - Generic Image Generation Results
# Contains only the essential image generation results
# Linked to GenerationLog parent table

from backend.models.base import BaseModel
from backend.core.config.database import db
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from typing import Dict, Any
from pathlib import Path

class ImageLog(BaseModel):
    """
    Image-specific generation results - child table of GenerationLog
    Contains only the final image generation results (paths to generated files)
    All generation parameters are stored in parent GenerationLog or implied by workflow
    """
    
    __tablename__ = 'image_logs'
    
    # === Foreign Key to Parent ===
    generation_id = Column(Integer, ForeignKey('generation_logs.id'), nullable=False, unique=True)
    generation_log = relationship("GenerationLog", back_populates="image_log")
    
    # === Image Results (Only Essential Fields) ===
    image_path = Column(String(500), nullable=True)        # Full path to generated image
    image_filename = Column(String(200), nullable=True)    # Just the filename
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        result = super().to_dict()
        
        # Add essential fields
        result.update({
            'generation_id': self.generation_id,
            'image_path': self.image_path,
            'image_filename': self.image_filename,
            'has_image': bool(self.image_path),
            'image_exists': self._check_image_exists()
        })
        
        return result
    
    def _check_image_exists(self) -> bool:
        """Check if the image file actually exists on disk"""
        if not self.image_path:
            return False
        
        try:
            return Path(self.image_path).exists()
        except Exception:
            return False
    
    def mark_image_generated(self, image_path: str):
        """Mark image generation as completed with results"""
        self.image_path = image_path
        
        # Extract filename from path
        if image_path:
            self.image_filename = Path(image_path).name
    
    @classmethod
    def create_from_params(cls, image_params: Dict[str, Any]):
        """
        Create Image log from image parameters
        
        Args:
            image_params (dict): Image generation parameters (can be empty)
            
        Returns:
            ImageLog: New image log instance (not yet saved)
        """
        return cls(
            # Initialize as not yet generated
            image_path=None,
            image_filename=None
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
    def get_successful_generations(cls):
        """Get count of successful image generations"""
        try:
            return cls.query.filter(cls.image_path.isnot(None)).count()
        except Exception as e:
            print(f"❌ Error counting successful generations: {e}")
            return 0
    
    @classmethod
    def get_stats(cls):
        """Get simple image generation statistics"""
        try:
            total_requests = cls.query.count()
            successful_generations = cls.get_successful_generations()
            
            return {
                'total_image_requests': total_requests,
                'successful_generations': successful_generations,
                'success_rate': round(successful_generations / total_requests * 100, 1) if total_requests > 0 else 0,
                'failed_generations': total_requests - successful_generations
            }
        except Exception as e:
            print(f"❌ Error getting image stats: {e}")
            return {}
    
    def __repr__(self):
        """String representation for debugging"""
        return f"<ImageLog(id={self.id}, generation_id={self.generation_id}, has_image={bool(self.image_path)})>"