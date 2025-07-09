# ComfyUI Package - SIMPLIFIED
# Exports main functionality with minimal validation
# Just checks what's actually needed

try:
    # Core components
    from .client import ComfyUIClient
    from .workflow import WorkflowManager, get_workflow_manager
    from .processor import process_request

    # Main exports
    __all__ = [
        'ComfyUIClient',
        'WorkflowManager', 
        'process_request',
        'get_workflow_manager',
        'validate_comfyui_setup'
    ]

    def validate_comfyui_setup() -> dict:
        """
        Simple ComfyUI validation - just the essentials
        
        Returns:
            dict: Simple validation results
        """
        try:
            # Check 1: Server running
            client = ComfyUIClient()
            server_running = client.is_server_running()
            
            # Check 2: Checkpoint configured
            from backend.config.comfyui_config import get_checkpoint
            checkpoint = get_checkpoint()
            checkpoint_set = bool(checkpoint)
            
            overall_success = server_running and checkpoint_set
            
            return {
                "overall_success": overall_success,
                "server_running": server_running,
                "checkpoint_set": checkpoint_set,
                "checkpoint": checkpoint if checkpoint_set else "Not configured"
            }
            
        except Exception as e:
            return {
                "overall_success": False,
                "error": str(e)
            }

except ImportError as e:
    from backend.utils import print_warning
    
    print_warning(f"ComfyUI components not available: {e}")
    
    def process_request(*args, **kwargs):
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
    
    __all__ = [
        'process_request',
        'validate_comfyui_setup'
    ]