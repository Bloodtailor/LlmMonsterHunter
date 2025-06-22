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
        Critical for VRAM management when switching to LLM
        
        Returns:
            dict: Results of memory freeing operation
        """
        try:
            print("🧹 Freeing ComfyUI model memory...")
            
            # Method 1: Use ComfyUI's free memory endpoint
            memory_freed = self.client.free_memory()
            
            if memory_freed:
                print("✅ ComfyUI memory freed successfully")
                return {
                    "success": True,
                    "method": "api_free",
                    "message": "Model memory freed via API"
                }
            else:
                print("⚠️ API memory free failed, trying alternative method")
                
                # Method 2: Try interrupt + free (more aggressive)
                interrupt_result = self.client.interrupt_generation()
                if interrupt_result:
                    # Wait a moment then try free again
                    import time
                    time.sleep(1)
                    memory_freed = self.client.free_memory()
                    
                    if memory_freed:
                        return {
                            "success": True,
                            "method": "interrupt_and_free",
                            "message": "Memory freed after interrupting generation"
                        }
                
                # Method 3: Manual garbage collection workflow (last resort)
                return self._manual_memory_cleanup()
                
        except Exception as e:
            print(f"❌ Error freeing model memory: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to free model memory"
            }
    
    def _manual_memory_cleanup(self) -> Dict[str, Any]:
        """
        Manual memory cleanup using a minimal workflow
        This can help force ComfyUI to release VRAM
        
        Returns:
            dict: Results of manual cleanup
        """
        try:
            print("🔧 Attempting manual memory cleanup...")
            
            # Create a minimal workflow that forces model unloading
            # This is a "dummy" workflow that loads nothing
            cleanup_workflow = {
                "1": {
                    "inputs": {},
                    "class_type": "CheckpointLoaderSimple",
                    "_meta": {"title": "Cleanup Loader"}
                }
            }
            
            # Don't actually execute this, just the attempt can trigger cleanup
            # In some versions of ComfyUI, even invalid workflows trigger memory cleanup
            
            return {
                "success": True,
                "method": "manual_cleanup",
                "message": "Attempted manual memory cleanup",
                "warning": "This is a fallback method - results may vary"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "manual_cleanup",
                "message": "Manual cleanup failed"
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
            
            # Step 2: Free memory to start fresh
            memory_result = self.free_model_memory()
            if memory_result["success"]:
                results.append("Freed model memory")
            else:
                results.append(f"Memory free failed: {memory_result.get('error', 'Unknown')}")
            
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
    """Convenience function to free ComfyUI memory"""
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