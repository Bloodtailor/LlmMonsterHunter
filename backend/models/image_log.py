# Image Log Child Table - Generic Image Generation Results
# Contains only the essential image generation results
# Linked to GenerationLog parent table

from pathlib import Path
from typing import Any

from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


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
    image_path = Column(String(500), nullable=True)  # Full path to generated image
    image_filename = Column(String(200), nullable=True)  # Just the filename

    # === Generation Parameters (stamped at request time) ===
    # The dev table shows truth: the model that painted, the geometry,
    # and any reference-image paths the paint was asked with (evolution
    # regen). NULL = a row from before the Gemini seam existed.
    params = Column(JSON, nullable=True)
    model_name = Column(String(200), nullable=True)  # Gemini model id

    def to_dict(self):
        """Convert to dictionary for API responses"""
        result = super().to_dict()

        # Add essential fields
        result.update(
            {
                'generation_id': self.generation_id,
                'image_path': self.image_path,
                'image_filename': self.image_filename,
                'has_image': bool(self.image_path),
                'image_exists': self._check_image_exists(),
                'model_name': self.model_name,
                'params': self.get_params(),
            }
        )

        return result

    def _check_image_exists(self) -> bool:
        """Check if the image file actually exists on disk (image_path is
        relative to THE outputs root - never resolve it against the CWD)"""
        if not self.image_path:
            return False

        try:
            from backend.ai.image.paths import outputs_root

            return (outputs_root() / self.image_path).exists()
        except Exception:
            return False

    def mark_image_generated(self, image_path: str):
        """Mark image generation as completed with results"""
        self.image_path = image_path

        # Extract filename from path
        if image_path:
            self.image_filename = Path(image_path).name

    def get_params(self) -> dict[str, Any]:
        """Generation parameters as a dictionary (empty for pre-seam rows)"""
        return self.params or {}

    @classmethod
    def create_from_params(cls, image_params: dict[str, Any]):
        """
        Create Image log from image parameters (model, aspect_ratio,
        resolution, reference_images) - stamped at request time so a
        queued paint keeps its setup even if settings change

        Args:
            image_params (dict): Image generation parameters (can be empty)

        Returns:
            ImageLog: New image log instance (not yet saved)
        """
        return cls(
            # Initialize as not yet generated
            image_path=None,
            image_filename=None,
            params=image_params or {},
            model_name=(image_params or {}).get('model'),
        )

    def __repr__(self):
        """String representation for debugging"""
        return f"<ImageLog(id={self.id}, generation_id={self.generation_id}, has_image={bool(self.image_path)})>"
