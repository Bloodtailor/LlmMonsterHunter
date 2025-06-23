# ComfyUI Processor - Image Generation Pipeline for Queue System
# Handles complete image generation pipeline with GenerationLog integration
# Similar to LLM processor but for ComfyUI image generation

from typing import Dict, Any, Optional, Callable
from .client import ComfyUIClient
from .workflow import get_workflow_manager
from .models import ModelManager
import time
from pathlib import Path

def process_image_request(generation_id: int, callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
    """
    Complete image generation pipeline for queue system
    
    Philosophy: Given a generation_id, do everything needed to generate an image
    - Load parameters from GenerationLog/ImageLog
    - Generate image using ComfyUI
    - Update logs automatically
    - Return final result
    
    Args:
        generation_id (int): GenerationLog ID containing image parameters
        callback (callable): Optional progress callback
        
    Returns:
        dict: Final image generation results
    """
    
    generation_start = time.time()
    
    try:
        # Step 1: Load generation log and image parameters
        from backend.models.generation_log import GenerationLog
        from backend.models.image_log import ImageLog
        
        generation_log = GenerationLog.query.get(generation_id)
        if not generation_log:
            return {
                'success': False,
                'error': f'GenerationLog {generation_id} not found',
                'generation_id': generation_id
            }
        
        if generation_log.generation_type != 'image':
            return {
                'success': False,
                'error': f'GenerationLog {generation_id} is not an image generation type',
                'generation_id': generation_id
            }
        
        image_log = generation_log.image_log
        if not image_log:
            return {
                'success': False,
                'error': f'ImageLog not found for GenerationLog {generation_id}',
                'generation_id': generation_id
            }
        
        # Extract image parameters from the prompt_text and any stored metadata
        # For now, we'll parse from the prompt_text format: "Monster: name (species) - description"
        prompt_text = generation_log.prompt_text
        
        # Simple parsing of the prompt text
        if prompt_text.startswith("Monster: "):
            try:
                parts = prompt_text[9:].split(" - ", 1)  # Remove "Monster: " prefix
                name_species_part = parts[0]
                description = parts[1] if len(parts) > 1 else ""
                
                if " (" in name_species_part and name_species_part.endswith(")"):
                    name = name_species_part.split(" (")[0]
                    species = name_species_part.split(" (")[1][:-1]  # Remove closing )
                else:
                    name = name_species_part
                    species = ""
            except:
                name = "Unknown Monster"
                species = "Unknown Species"
                description = prompt_text
        else:
            name = "Monster"
            species = "Creature"
            description = prompt_text
        
        workflow_name = generation_log.prompt_name or "monster_generation"
        
        print(f"✅ Loaded image parameters: {name} ({species}) - {description[:100]}...")
        
        # Step 2: Mark as started
        generation_log.mark_started()
        generation_log.save()
        
        # Step 3: Initialize ComfyUI components
        if callback:
            callback("🔍 Checking ComfyUI server...")
        
        client = ComfyUIClient()
        workflow_manager = get_workflow_manager()
        model_manager = ModelManager(client)
        
        # Check server availability
        if not client.is_server_running():
            generation_log.mark_failed("ComfyUI server is not running")
            generation_log.save()
            return {
                'success': False,
                'error': '🎨 ComfyUI server is not running',
                'reason': 'SERVER_NOT_RUNNING',
                'help': 'Start ComfyUI with: python main.py --listen',
                'generation_id': generation_id
            }
        
        # Step 4: Optimize for generation (free memory)
        if callback:
            callback("🔧 Optimizing for image generation...")
        
        optimization = model_manager.optimize_for_generation()
        if not optimization["success"]:
            print(f"⚠️ Optimization warning: {optimization.get('error')}")
        
        # Step 5: Load and prepare workflow
        if callback:
            callback("📋 Loading workflow...")
        
        workflow = workflow_manager.load_workflow(workflow_name)
        if not workflow:
            error_msg = f"Failed to load {workflow_name} workflow"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return {
                'success': False,
                'error': error_msg,
                'help': f"Check that {workflow_name}.json exists in workflows directory",
                'generation_id': generation_id
            }
        
        # Step 6: Build prompt
        if callback:
            callback("✏️ Building monster prompt...")
        
        full_prompt = workflow_manager.build_monster_prompt(
            monster_description=description,
            monster_name=name,
            monster_species=species
        )
        
        # Step 7: Modify workflow with prompt
        if callback:
            callback("🎨 Preparing generation...")
        
        modified_workflow = workflow_manager.modify_workflow_prompt(
            workflow=workflow,
            positive_prompt=full_prompt,
            seed=int(time.time()) % 1000000  # Semi-random seed based on time
        )
        
        # Step 8: Queue generation
        if callback:
            callback("📤 Queuing generation...")
        
        try:
            prompt_id = client.queue_prompt(modified_workflow)
        except Exception as e:
            error_msg = f"Failed to queue generation: {str(e)}"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return {
                'success': False,
                'error': error_msg,
                'help': "Check ComfyUI server logs for details",
                'generation_id': generation_id
            }
        
        # Step 9: Wait for completion with progress updates
        if callback:
            callback("⏳ Generation in progress...")
        
        try:
            result = client.wait_for_completion(
                prompt_id=prompt_id,
                timeout=300  # 5 minutes
            )
        except TimeoutError:
            error_msg = "Image generation timed out after 5 minutes"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return {
                'success': False,
                'error': error_msg,
                'help': "Try generating again or check ComfyUI server performance",
                'generation_id': generation_id
            }
        except Exception as e:
            error_msg = f"Generation monitoring failed: {str(e)}"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return {
                'success': False,
                'error': error_msg,
                'generation_id': generation_id
            }
        
        # Step 10: Download and save image
        if not result.get("images"):
            error_msg = "Generation completed but no images were produced"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return {
                'success': False,
                'error': error_msg,
                'help': "Check ComfyUI workflow configuration",
                'generation_id': generation_id
            }
        
        if callback:
            callback("💾 Downloading image...")
        
        # Download the first image
        image_info = result["images"][0]
        image_path = _download_and_save_image(
            client, 
            image_info, 
            name or "monster"
        )
        
        if not image_path:
            error_msg = "Failed to download generated image"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return {
                'success': False,
                'error': error_msg,
                'generation_id': generation_id
            }
        
        # Step 11: Update image log with results
        image_log.mark_image_generated(str(image_path))
        image_log.save()
        
        # Step 12: Post-generation cleanup
        if callback:
            callback("🧹 Cleaning up...")
        
        cleanup_result = model_manager.post_generation_cleanup()
        if not cleanup_result["success"]:
            print(f"⚠️ Cleanup warning: {cleanup_result.get('error')}")
        
        # Step 13: Mark as completed
        generation_log.mark_completed()
        generation_log.save()
        
        # Step 14: Return success
        total_time = time.time() - generation_start
        
        if callback:
            callback(f"✅ Image generated in {total_time:.1f}s!")
        
        return {
            'success': True,
            'image_path': str(image_path),
            'prompt_id': prompt_id,
            'execution_time': total_time,
            'full_prompt': full_prompt,
            'workflow_used': workflow_name,
            'image_info': image_info,
            'cleanup_success': cleanup_result["success"],
            'generation_id': generation_id
        }
        
    except Exception as e:
        # Ensure cleanup even on failure
        try:
            model_manager = ModelManager()
            model_manager.post_generation_cleanup()
        except:
            pass
        
        # Mark as failed in database
        try:
            from backend.models.generation_log import GenerationLog
            generation_log = GenerationLog.query.get(generation_id)
            if generation_log:
                generation_log.mark_failed(str(e))
                generation_log.save()
        except:
            pass
        
        return {
            'success': False,
            'error': f"Image generation pipeline failed: {str(e)}",
            'execution_time': time.time() - generation_start,
            'generation_id': generation_id
        }

def _download_and_save_image(client: ComfyUIClient, image_info: Dict[str, str], 
                           monster_name: str) -> Optional[Path]:
    """
    Download image from ComfyUI and save with monster-specific filename
    
    Args:
        client (ComfyUIClient): ComfyUI client instance
        image_info (dict): Image info from ComfyUI result
        monster_name (str): Monster name for filename
        
    Returns:
        Path: Path to saved image or None if failed
    """
    try:
        # Download image data
        image_data = client.download_image(
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
        
        # Save to ComfyUI outputs directory
        outputs_dir = Path(__file__).parent / 'outputs'
        outputs_dir.mkdir(exist_ok=True)
        save_path = outputs_dir / filename
        
        # Save image
        with open(save_path, 'wb') as f:
            f.write(image_data)
        
        print(f"✅ Image saved: {save_path}")
        return save_path
        
    except Exception as e:
        print(f"❌ Failed to download/save image: {e}")
        return None