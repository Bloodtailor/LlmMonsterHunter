# ComfyUI Package - Clean Modular Architecture
# Exports main functionality with organized imports

try:
    # Core components
    from .client import ComfyUIClient
    from .workflow import WorkflowManager, get_workflow_manager
    from .models import ModelManager, free_comfyui_memory, optimize_for_image_generation, cleanup_after_image_generation
    from .generation import MonsterImageGenerator, generate_monster_image, validate_comfyui_setup

    # Main exports for external use
    __all__ = [
        # Classes
        'ComfyUIClient',
        'WorkflowManager', 
        'ModelManager',
        'MonsterImageGenerator',
        
        # Convenience functions
        'generate_monster_image',
        'validate_comfyui_setup',
        'get_workflow_manager',
        'free_comfyui_memory',
        'optimize_for_image_generation', 
        'cleanup_after_image_generation'
    ]

except ImportError as e:
    # Graceful handling if ComfyUI dependencies are missing
    print(f"⚠️ ComfyUI components not available: {e}")
    
    # Provide stub functions for graceful degradation
    def generate_monster_image(*args, **kwargs):
        return {
            "success": False,
            "error": "ComfyUI components not available",
            "reason": "IMPORT_ERROR"
        }
    
    def validate_comfyui_setup():
        return {
            "overall_success": False,
            "error": "ComfyUI components not available"
        }
    
    # Minimal exports for graceful degradation
    __all__ = [
        'generate_monster_image',
        'validate_comfyui_setup'
    ]