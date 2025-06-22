# ComfyUI Model Management
# Handles model loading, unloading, and VRAM optimization
# Ensures efficient VRAM usage for LLM ↔ Image model switching

from typing import Dict, Any, Optional
from .client import ComfyUIClient

class ModelManager:
    """
    Manages ComfyUI model loading and memory optimization
    Handles VRAM switching between LLM and image generation
    """
    
    def __init__(self, client: Optional[ComfyUIClient] = None):
        self.client = client or ComfyUIClient()
        self._last_model_info = None
    
    def free_model_memory(self) -> Dict[str, Any]:
        """
        Free all GPU memory used by ComfyUI models
        Uses the correct /free API endpoint with unload_models=true
        
        Returns:
            dict: Results of memory freeing operation
        """
        try:
            print("🧹 Unloading ComfyUI models...")
            
            # Use the correct API call that matches the "unload models" button
            success = self.client.unload_models()
            
            if success:
                print("✅ ComfyUI models unloaded successfully")
                return {
                    "success": True,
                    "method": "unload_models",
                    "message": "Models unloaded successfully"
                }
            else:
                print("❌ Failed to unload ComfyUI models")
                return {
                    "success": False,
                    "method": "unload_models", 
                    "message": "Failed to unload models"
                }
                
        except Exception as e:
            print(f"❌ Error unloading models: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to unload models"
            }
    
    def ensure_model_loaded(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Ensure specified model is loaded in ComfyUI
        For future use when we want to pre-load specific models
        
        Args:
            model_name (str): Model to ensure is loaded (optional)
            
        Returns:
            dict: Model loading status
        """
        try:
            # For now, ComfyUI automatically loads models when needed
            # This is a placeholder for future model preloading logic
            
            return {
                "success": True,
                "message": "Model loading handled by ComfyUI automatically",
                "model_name": model_name or "default"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Model loading check failed"
            }
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get current GPU memory usage from ComfyUI
        Useful for monitoring VRAM usage
        
        Returns:
            dict: Memory usage information
        """
        try:
            # Try to get system stats from ComfyUI
            stats = self.client.get_system_stats()
            
            if stats:
                return {
                    "success": True,
                    "stats": stats,
                    "message": "Retrieved memory stats from ComfyUI"
                }
            else:
                return {
                    "success": False,
                    "message": "ComfyUI does not provide memory stats",
                    "suggestion": "Check NVIDIA-SMI or Task Manager for VRAM usage"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get memory usage"
            }
    
    def optimize_for_generation(self) -> Dict[str, Any]:
        """
        Optimize ComfyUI for upcoming image generation
        Prepares the system for efficient image generation
        
        Returns:
            dict: Optimization results
        """
        results = []
        
        try:
            # Step 1: Clear any existing generation queue
            print("🔧 Optimizing ComfyUI for generation...")
            
            # Interrupt any running generation
            interrupt_result = self.client.interrupt_generation()
            if interrupt_result:
                results.append("Interrupted existing generation")
            
            # Step 2: Unload models to start fresh  
            unload_result = self.client.unload_models()
            if unload_result:
                results.append("Unloaded models successfully")
            else:
                results.append("Model unload failed (continuing anyway)")
            
            return {
                "success": True,
                "optimizations": results,
                "message": "ComfyUI optimized for generation"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "optimizations": results,
                "message": "Optimization failed"
            }
    
    def post_generation_cleanup(self) -> Dict[str, Any]:
        """
        Clean up after image generation
        Frees memory for LLM model loading
        
        Returns:
            dict: Cleanup results
        """
        try:
            print("🧹 Cleaning up after image generation...")
            
            # Free all model memory to make room for LLM
            cleanup_result = self.free_model_memory()
            
            if cleanup_result["success"]:
                print("✅ Post-generation cleanup completed")
                return {
                    "success": True,
                    "message": "Memory freed for LLM loading",
                    "ready_for_llm": True
                }
            else:
                print("⚠️ Cleanup had issues but continuing...")
                return {
                    "success": False,
                    "message": "Cleanup completed with warnings",
                    "ready_for_llm": False,
                    "warning": cleanup_result.get("error", "Unknown cleanup issue")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Post-generation cleanup failed",
                "ready_for_llm": False
            }

# Convenience functions
def free_comfyui_memory() -> Dict[str, Any]:
    """Convenience function to unload ComfyUI models"""
    manager = ModelManager()
    return manager.free_model_memory()

def optimize_for_image_generation() -> Dict[str, Any]:
    """Convenience function to optimize for image generation"""
    manager = ModelManager()
    return manager.optimize_for_generation()

def cleanup_after_image_generation() -> Dict[str, Any]:
    """Convenience function to cleanup after generation"""
    manager = ModelManager()
    return manager.post_generation_cleanup()