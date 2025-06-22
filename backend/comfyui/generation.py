# ComfyUI Generation Pipeline
# Complete image generation pipeline with VRAM management
# Orchestrates workflow, client, and model management

import time
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from .client import ComfyUIClient
from .workflow import get_workflow_manager
from .models import ModelManager

class MonsterImageGenerator:
    """
    Complete monster image generation pipeline
    Handles the full process from description to saved image
    """
    
    def __init__(self):
        self.client = ComfyUIClient()
        self.workflow_manager = get_workflow_manager()
        self.model_manager = ModelManager(self.client)
        self.outputs_dir = Path(__file__).parent / 'outputs'
        self.outputs_dir.mkdir(exist_ok=True)
    
    def generate_monster_image(self, monster_description: str,
                             monster_name: str = "",
                             monster_species: str = "",
                             callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
        """
        Complete monster image generation pipeline
        
        Args:
            monster_description (str): Monster description for image generation
            monster_name (str): Monster name (optional)
            monster_species (str): Monster species (optional)
            callback (callable): Optional progress callback
            
        Returns:
            dict: Generation results with image path and metadata
        """
        generation_start = time.time()
        
        try:
            # Step 1: Check server availability
            if callback:
                callback("🔍 Checking ComfyUI server...")
            
            if not self.client.is_server_running():
                return {
                    "success": False,
                    "error": "🎨 ComfyUI server is not running",
                    "reason": "SERVER_NOT_RUNNING",
                    "help": "Start ComfyUI with: python main.py --listen"
                }
            
            # Step 2: Optimize for generation (free memory)
            if callback:
                callback("🔧 Optimizing for image generation...")
            
            optimization = self.model_manager.optimize_for_generation()
            if not optimization["success"]:
                print(f"⚠️ Optimization warning: {optimization.get('error')}")
            
            # Step 3: Load and prepare workflow
            if callback:
                callback("📋 Loading workflow...")
            
            workflow = self.workflow_manager.load_workflow("monster_generation")
            if not workflow:
                return {
                    "success": False,
                    "error": "Failed to load monster_generation workflow",
                    "help": "Check that monster_generation.json exists in workflows directory"
                }
            
            # Step 4: Build prompt
            if callback:
                callback("✏️ Building monster prompt...")
            
            full_prompt = self.workflow_manager.build_monster_prompt(
                monster_description=monster_description,
                monster_name=monster_name,
                monster_species=monster_species
            )
            
            # Step 5: Modify workflow with prompt
            if callback:
                callback("🎨 Preparing generation...")
            
            modified_workflow = self.workflow_manager.modify_workflow_prompt(
                workflow=workflow,
                positive_prompt=full_prompt,
                seed=int(time.time()) % 1000000  # Semi-random seed based on time
            )
            
            # Step 6: Queue generation
            if callback:
                callback("📤 Queuing generation...")
            
            try:
                prompt_id = self.client.queue_prompt(modified_workflow)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to queue generation: {str(e)}",
                    "help": "Check ComfyUI server logs for details"
                }
            
            # Step 7: Wait for completion with progress updates
            if callback:
                callback("⏳ Generation in progress...")
            
            def progress_callback(status):
                if callback:
                    if status.get("completed"):
                        callback("✅ Generation completed!")
                    elif status.get("running"):
                        callback("🎨 Generating image...")
                    elif status.get("pending"):
                        callback("⏳ Waiting in queue...")
            
            try:
                result = self.client.wait_for_completion(
                    prompt_id=prompt_id,
                    timeout=300  # 5 minutes
                )
            except TimeoutError:
                return {
                    "success": False,
                    "error": "Image generation timed out after 5 minutes",
                    "help": "Try generating again or check ComfyUI server performance"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Generation monitoring failed: {str(e)}"
                }
            
            # Step 8: Download and save image
            if not result.get("images"):
                return {
                    "success": False,
                    "error": "Generation completed but no images were produced",
                    "help": "Check ComfyUI workflow configuration"
                }
            
            if callback:
                callback("💾 Downloading image...")
            
            # Download the first image
            image_info = result["images"][0]
            image_path = self._download_and_save_image(
                image_info, 
                monster_name or "monster"
            )
            
            if not image_path:
                return {
                    "success": False,
                    "error": "Failed to download generated image"
                }
            
            # Step 9: Post-generation cleanup
            if callback:
                callback("🧹 Cleaning up...")
            
            cleanup_result = self.model_manager.post_generation_cleanup()
            if not cleanup_result["success"]:
                print(f"⚠️ Cleanup warning: {cleanup_result.get('error')}")
            
            # Step 10: Return success
            total_time = time.time() - generation_start
            
            if callback:
                callback(f"✅ Image generated in {total_time:.1f}s!")
            
            return {
                "success": True,
                "image_path": str(image_path),
                "prompt_id": prompt_id,
                "execution_time": total_time,
                "full_prompt": full_prompt,
                "image_info": image_info,
                "cleanup_success": cleanup_result["success"]
            }
            
        except Exception as e:
            # Ensure cleanup even on failure
            try:
                self.model_manager.post_generation_cleanup()
            except:
                pass
            
            return {
                "success": False,
                "error": f"Generation pipeline failed: {str(e)}",
                "execution_time": time.time() - generation_start
            }
    
    def _download_and_save_image(self, image_info: Dict[str, str], 
                               monster_name: str) -> Optional[Path]:
        """
        Download image from ComfyUI and save with monster-specific filename
        
        Args:
            image_info (dict): Image info from ComfyUI result
            monster_name (str): Monster name for filename
            
        Returns:
            Path: Path to saved image or None if failed
        """
        try:
            # Download image data
            image_data = self.client.download_image(
                filename=image_info["filename"],
                subfolder=image_info.get("subfolder", ""),
                img_type=image_info.get("type", "output")
            )
            
            # Generate unique filename
            timestamp = int(time.time())
            safe_name = "".join(c for c in monster_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_').lower()
            
            if not safe_name:
                safe_name = "monster"
            
            filename = f"{safe_name}_{timestamp}.png"
            save_path = self.outputs_dir / filename
            
            # Save image
            with open(save_path, 'wb') as f:
                f.write(image_data)
            
            print(f"✅ Image saved: {save_path}")
            return save_path
            
        except Exception as e:
            print(f"❌ Failed to download/save image: {e}")
            return None
    
    def validate_setup(self) -> Dict[str, Any]:
        """
        Validate complete ComfyUI setup
        
        Returns:
            dict: Validation results with detailed status
        """
        validation_results = {
            "overall_success": False,
            "checks": {}
        }
        
        # Check 1: Server running
        server_running = self.client.is_server_running()
        validation_results["checks"]["server_running"] = {
            "success": server_running,
            "message": "✅ ComfyUI server accessible" if server_running else "❌ ComfyUI server not running"
        }
        
        # Check 2: Workflow available
        workflow = self.workflow_manager.load_workflow("monster_generation")
        workflow_ok = workflow is not None
        validation_results["checks"]["workflow_available"] = {
            "success": workflow_ok,
            "message": "✅ Monster generation workflow loaded" if workflow_ok else "❌ Monster generation workflow not found"
        }
        
        # Check 3: Workflow validation (if loaded)
        if workflow_ok:
            workflow_validation = self.workflow_manager.validate_workflow(workflow)
            validation_results["checks"]["workflow_valid"] = {
                "success": workflow_validation["success"],
                "message": "✅ Workflow structure valid" if workflow_validation["success"] else f"❌ Workflow issues: {', '.join(workflow_validation['issues'])}"
            }
        
        # Check 4: Output directory
        outputs_writable = self.outputs_dir.exists() and self.outputs_dir.is_dir()
        validation_results["checks"]["outputs_directory"] = {
            "success": outputs_writable,
            "message": "✅ Outputs directory ready" if outputs_writable else "❌ Outputs directory not accessible"
        }
        
        # Overall success
        all_checks = [check["success"] for check in validation_results["checks"].values()]
        validation_results["overall_success"] = all(all_checks)
        
        return validation_results

# Convenience functions for external use
def generate_monster_image(monster_description: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for monster image generation"""
    generator = MonsterImageGenerator()
    return generator.generate_monster_image(monster_description, **kwargs)

def validate_comfyui_setup() -> Dict[str, Any]:
    """Convenience function to validate ComfyUI setup"""
    generator = MonsterImageGenerator()
    return generator.validate_setup()