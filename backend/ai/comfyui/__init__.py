# ComfyUI Package - UPDATED FOR GENERIC ARCHITECTURE
# Exports main functionality with clean, generic components
# No game-specific logic - pure ComfyUI integration

try:
    # Core components (generic)
    from .client import ComfyUIClient
    from .workflow import WorkflowManager, get_workflow_manager
    from .models import ModelManager, free_comfyui_memory, optimize_for_image_generation, cleanup_after_image_generation
    from .processor import process_request, quick_image_generation

    # Main exports for external use
    __all__ = [
        # Classes
        'ComfyUIClient',
        'WorkflowManager', 
        'ModelManager',
        
        # Core functions (generic)
        'process_request',           # NEW: Generic image processing pipeline
        'quick_image_generation',    # NEW: Simple image generation
        'get_workflow_manager',
        
        # Memory management functions
        'free_comfyui_memory',
        'optimize_for_image_generation', 
        'cleanup_after_image_generation'
    ]

    def validate_comfyui_setup() -> dict:
        """
        Validate ComfyUI setup for generic image generation
        
        Returns:
            dict: Validation results with detailed status
        """
        try:
            validation_results = {
                "overall_success": False,
                "checks": {}
            }
            
            # Check 1: Server running
            client = ComfyUIClient()
            server_running = client.is_server_running()
            validation_results["checks"]["server_running"] = {
                "success": server_running,
                "message": "✅ ComfyUI server accessible" if server_running else "❌ ComfyUI server not running"
            }
            
            # Check 2: Workflow available
            workflow_manager = get_workflow_manager()
            workflows = workflow_manager.list_available_workflows()
            workflow_ok = len(workflows) > 0
            validation_results["checks"]["workflows_available"] = {
                "success": workflow_ok,
                "message": f"✅ {len(workflows)} workflows found" if workflow_ok else "❌ No workflows found",
                "workflows": workflows
            }
            
            # Check 3: Configuration loading
            try:
                from backend.config.comfyui_config import get_all_generation_defaults
                config = get_all_generation_defaults()
                config_ok = bool(config.get('checkpoint'))
                validation_results["checks"]["configuration"] = {
                    "success": config_ok,
                    "message": "✅ Configuration loaded" if config_ok else "❌ Configuration missing",
                    "checkpoint": config.get('checkpoint', 'Not set')
                }
            except Exception as e:
                validation_results["checks"]["configuration"] = {
                    "success": False,
                    "message": f"❌ Configuration error: {str(e)}"
                }
            
            # Check 4: Output directory
            from pathlib import Path
            outputs_dir = Path(__file__).parent / 'outputs'
            outputs_writable = True
            try:
                outputs_dir.mkdir(exist_ok=True)
            except Exception:
                outputs_writable = False
                
            validation_results["checks"]["outputs_directory"] = {
                "success": outputs_writable,
                "message": "✅ Outputs directory ready" if outputs_writable else "❌ Outputs directory not accessible"
            }
            
            # Overall success
            all_checks = [check["success"] for check in validation_results["checks"].values()]
            validation_results["overall_success"] = all(all_checks)
            
            return validation_results
            
        except Exception as e:
            return {
                "overall_success": False,
                "error": str(e),
                "message": "Validation failed with exception"
            }
    
    # Add validation to exports
    __all__.append('validate_comfyui_setup')

except ImportError as e:
    # Graceful handling if ComfyUI dependencies are missing
    print(f"⚠️ ComfyUI components not available: {e}")
    
    # Provide stub functions for graceful degradation
    def process_request(*args, **kwargs):
        return {
            "success": False,
            "error": "ComfyUI components not available",
            "reason": "IMPORT_ERROR"
        }
    
    def quick_image_generation(*args, **kwargs):
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
        'process_request',
        'quick_image_generation',
        'validate_comfyui_setup'
    ]