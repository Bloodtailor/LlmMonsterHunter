# ComfyUI Service - THIN ENTRY POINT
# Minimal service that delegates to modular ComfyUI components
# Handles optional image generation with graceful degradation

from typing import Dict, Any, Optional, Callable
import os

def is_image_generation_enabled() -> bool:
    """
    Check if image generation is enabled via environment variable
    
    Returns:
        bool: True if image generation should be attempted
    """
    return os.getenv('ENABLE_IMAGE_GENERATION', 'false').lower() == 'true'

def is_comfyui_available() -> bool:
    """
    Check if ComfyUI is available for image generation
    Safe to call even when ComfyUI is not installed
    
    Returns:
        bool: True if ComfyUI is available and running
    """
    if not is_image_generation_enabled():
        return False
    
    try:
        from backend.comfyui.client import ComfyUIClient
        client = ComfyUIClient()
        return client.is_server_running()
    except ImportError:
        return False
    except Exception:
        return False

def generate_monster_image(monster_description: str, 
                         monster_name: str = "",
                         monster_species: str = "",
                         callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
    """
    Generate monster image with graceful degradation
    Returns success=False with helpful message if ComfyUI unavailable
    
    Args:
        monster_description (str): Monster description for image generation
        monster_name (str): Monster name (optional)
        monster_species (str): Monster species (optional)
        callback (callable): Optional progress callback
        
    Returns:
        dict: Generation results or graceful failure
    """
    
    # Check if image generation is enabled
    if not is_image_generation_enabled():
        return {
            "success": False,
            "error": "Image generation is disabled",
            "reason": "DISABLED",
            "help": "Set ENABLE_IMAGE_GENERATION=true in .env to enable image generation"
        }
    
    # Try to import and use ComfyUI components
    try:
        from backend.comfyui.generation import MonsterImageGenerator
        
        generator = MonsterImageGenerator()
        return generator.generate_monster_image(
            monster_description=monster_description,
            monster_name=monster_name,
            monster_species=monster_species,
            callback=callback
        )
        
    except ImportError as e:
        return {
            "success": False,
            "error": "ComfyUI components not available",
            "reason": "IMPORT_ERROR", 
            "help": "Install ComfyUI dependencies or disable image generation",
            "technical_error": str(e)
        }
    except Exception as e:
        # Check if it's a server connection issue
        error_str = str(e).lower()
        if "connection" in error_str or "server" in error_str:
            return {
                "success": False,
                "error": "🎨 ComfyUI server is not running",
                "reason": "SERVER_NOT_RUNNING",
                "help": "Start ComfyUI server with: python main.py --listen",
                "details": [
                    "1. Navigate to your ComfyUI directory",
                    "2. Run: python main.py --listen", 
                    "3. Wait for 'Starting server' message",
                    "4. Try generating monsters again"
                ]
            }
        else:
            return {
                "success": False,
                "error": f"ComfyUI generation failed: {str(e)}",
                "reason": "GENERATION_ERROR",
                "help": "Check ComfyUI server logs for details"
            }

def get_comfyui_status() -> Dict[str, Any]:
    """
    Get comprehensive ComfyUI status for debugging
    
    Returns:
        dict: Complete status information
    """
    status = {
        "enabled": is_image_generation_enabled(),
        "available": False,
        "server_running": False,
        "components_loaded": False,
        "error": None
    }
    
    if not status["enabled"]:
        status["message"] = "Image generation disabled in configuration"
        return status
    
    try:
        # Try importing components
        from backend.comfyui.client import ComfyUIClient
        from backend.comfyui.generation import MonsterImageGenerator
        status["components_loaded"] = True
        
        # Check server
        client = ComfyUIClient()
        status["server_running"] = client.is_server_running()
        status["available"] = status["server_running"]
        
        if status["available"]:
            status["message"] = "✅ ComfyUI ready for image generation"
        else:
            status["message"] = "❌ ComfyUI server not running"
            status["help"] = "Start ComfyUI with: python main.py --listen"
        
    except ImportError as e:
        status["error"] = f"Import error: {str(e)}"
        status["message"] = "❌ ComfyUI components not available"
        status["help"] = "Install ComfyUI or disable image generation"
    except Exception as e:
        status["error"] = str(e)
        status["message"] = f"❌ ComfyUI error: {str(e)}"
    
    return status

# Convenience function for monster service integration
def generate_image_if_available(monster_data: Dict[str, Any], 
                               callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
    """
    Generate image if ComfyUI is available, otherwise return graceful failure
    Perfect for integration with monster generation pipeline
    
    Args:
        monster_data (dict): Monster data including description, name, species
        callback (callable): Optional progress callback
        
    Returns:
        dict: Image generation results or graceful failure
    """
    return generate_monster_image(
        monster_description=monster_data.get('description', ''),
        monster_name=monster_data.get('name', ''),
        monster_species=monster_data.get('species', ''),
        callback=callback
    )