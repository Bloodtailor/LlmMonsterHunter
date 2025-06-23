# ComfyUI Processor - GENERIC IMAGE GENERATION PIPELINE
# Handles complete image generation pipeline with automatic workflow management
# Takes generation_id, manages the entire process, updates logs automatically
# ARCHITECTURE: Completely generic - knows nothing about monsters or game objects

import time
import random
from pathlib import Path
from typing import Dict, Any, Optional, Callable

def process_request(generation_id: int, callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
    """
    Complete image generation pipeline with automatic workflow management
    
    Philosophy: Given a generation_id, do everything needed to get an image
    - Load parameters from database (generation_log + image_log)
    - Build complete prompt (base + unique text)
    - Load and modify workflow with config
    - Generate image via ComfyUI
    - Save with organized file structure
    - Update logs automatically
    - Return final result
    
    Args:
        generation_id (int): Database generation_logs.id
        callback (callable): Optional progress callback
        
    Returns:
        dict: Final processing results
    """
    
    try:
        # Step 1: Load generation log and verify it's an image generation
        from backend.models.generation_log import GenerationLog
        
        generation_log = GenerationLog.query.get(generation_id)
        if not generation_log:
            return {
                'success': False,
                'error': f'Generation log {generation_id} not found',
                'generation_id': generation_id
            }
        
        if generation_log.generation_type != 'image':
            return {
                'success': False,
                'error': f'Generation {generation_id} is not an image generation (type: {generation_log.generation_type})',
                'generation_id': generation_id
            }
        
        # Step 2: Get image-specific data
        image_log = generation_log.image_log
        if not image_log:
            return {
                'success': False,
                'error': f'Image log not found for generation {generation_id}',
                'generation_id': generation_id
            }
        
        # Step 3: Extract parameters
        prompt_text = generation_log.prompt_text  # The unique part of the prompt
        workflow_name = generation_log.prompt_name  # The workflow to use
        
        if not prompt_text or not workflow_name:
            generation_log.mark_failed("Missing prompt text or workflow name")
            generation_log.save()
            return {
                'success': False,
                'error': 'Missing prompt text or workflow name',
                'generation_id': generation_id
            }
        
        print(f"✅ Loaded image parameters: workflow='{workflow_name}', prompt_length={len(prompt_text)}")
        
        # Step 4: Mark as started
        generation_log.mark_started()
        generation_log.save()
        
        if callback:
            callback("🔧 Initializing image generation...")
        
        # Step 5: Check ComfyUI server availability
        from .client import ComfyUIClient
        from backend.config.comfyui_config import get_server_url, get_timeout
        
        client = ComfyUIClient(base_url=get_server_url())
        
        if not client.is_server_running():
            error_msg = "ComfyUI server is not running"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return {
                'success': False,
                'error': error_msg,
                'generation_id': generation_id,
                'help': 'Start ComfyUI with: python main.py --listen'
            }
        
        if callback:
            callback("✅ ComfyUI server connected")
        
        # Step 6: Load and prepare workflow
        from .workflow import get_workflow_manager
        
        workflow_manager = get_workflow_manager()
        workflow = workflow_manager.load_workflow(workflow_name)
        
        if not workflow:
            error_msg = f"Workflow '{workflow_name}' not found"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return {
                'success': False,
                'error': error_msg,
                'generation_id': generation_id
            }
        
        if callback:
            callback(f"📋 Loaded workflow: {workflow_name}")
        
        # Step 7: Build complete positive prompt
        from backend.config.comfyui_config import get_base_positive_prompt
        
        base_prompt = get_base_positive_prompt()
        complete_positive_prompt = f"{prompt_text}, {base_prompt}"
        
        print(f"✅ Built complete prompt: {len(complete_positive_prompt)} characters")
        
        # Step 8: Modify workflow with config and prompt
        from backend.config.comfyui_config import get_all_generation_defaults
        
        config = get_all_generation_defaults()
        
        modified_workflow = workflow_manager.modify_workflow_prompt(
            workflow=workflow,
            positive_prompt=complete_positive_prompt,
            negative_prompt=config['negative_prompt'],
            steps=config['steps'],
            cfg=config['cfg'],
            denoise=config['denoise'],
            width=config['width'],
            height=config['height'],
            batch_size=config['batch_size'],
            seed=random.randint(1, 1000000)  # Random seed for variety
        )
        
        if callback:
            callback("⚙️ Workflow configured with parameters")
        
        # Step 9: Queue generation
        try:
            if callback:
                callback("📤 Queuing generation request...")
            
            prompt_id = client.queue_prompt(modified_workflow)
            
        except Exception as e:
            error_msg = f"Failed to queue generation: {str(e)}"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return {
                'success': False,
                'error': error_msg,
                'generation_id': generation_id
            }
        
        # Step 10: Wait for completion with progress updates
        if callback:
            callback("⏳ Generation in progress...")
        
        try:
            result = client.wait_for_completion(
                prompt_id=prompt_id,
                timeout=config['timeout']
            )
        except Exception as e:
            error_msg = f"Generation failed: {str(e)}"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return {
                'success': False,
                'error': error_msg,
                'generation_id': generation_id
            }
        
        # Step 11: Check if images were generated
        if not result.get("images"):
            error_msg = "Generation completed but no images were produced"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return {
                'success': False,
                'error': error_msg,
                'generation_id': generation_id
            }
        
        if callback:
            callback("💾 Downloading and organizing image...")
        
        # Step 12: Download and save with organized structure
        image_info = result["images"][0]  # Take first image
        
        try:
            relative_path = _download_and_organize_image(
                client=client,
                image_info=image_info,
                workflow_name=workflow_name
            )
        except Exception as e:
            error_msg = f"Failed to download/save image: {str(e)}"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return {
                'success': False,
                'error': error_msg,
                'generation_id': generation_id
            }
        
        # Step 13: Update logs with success
        image_log.mark_image_generated(str(Path("outputs") / relative_path))  # Full path for database
        generation_log.mark_completed()
        
        image_log.save()
        generation_log.save()
        
        if callback:
            callback("✅ Image generation completed!")

        print("unloading image model and freeing memory")
        client.unload_models()
        client.free_memory()


        # Step 14: Return success
        execution_time = generation_log.duration_seconds or 0
        
        return {
            'success': True,
            'image_path': str(Path("outputs") / relative_path),  # Full path for backwards compatibility
            'relative_path': relative_path,  # Relative path from outputs folder
            'execution_time': execution_time,
            'generation_id': generation_id,
            'workflow_used': workflow_name,
            'prompt_id': prompt_id,
            'image_dimensions': f"{config['width']}x{config['height']}"
        }
        
    except Exception as e:
        print(f"❌ Image processing error for generation {generation_id}: {e}")
        
        # Try to mark as failed in database
        try:
            from backend.models.generation_log import GenerationLog
            log = GenerationLog.query.get(generation_id)
            if log:
                log.mark_failed(str(e))
                log.save()
        except:
            pass  # Don't fail on database update failure
        
        return {
            'success': False,
            'error': str(e),
            'generation_id': generation_id
        }

def _download_and_organize_image(client, image_info: Dict[str, str], workflow_name: str) -> str:
    """
    Download image from ComfyUI and save with organized file structure
    
    Args:
        client: ComfyUI client instance
        image_info (dict): Image info from ComfyUI result
        workflow_name (str): Name of workflow used (for folder organization)
        
    Returns:
        str: Relative path from outputs folder (e.g., "monster_generation/00000001.png")
    """
    
    # Create workflow-specific output directory
    outputs_dir = Path(__file__).parent / 'outputs' / workflow_name
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    # Find next available number
    existing_files = list(outputs_dir.glob("*.png"))
    if existing_files:
        # Extract numbers and find the highest
        numbers = []
        for file in existing_files:
            try:
                number = int(file.stem)
                numbers.append(number)
            except ValueError:
                continue
        next_number = max(numbers) + 1 if numbers else 1
    else:
        next_number = 1
    
    # Format as 8-digit number with leading zeros
    filename = f"{next_number:08d}.png"
    save_path = outputs_dir / filename
    
    # Download image data
    image_data = client.download_image(
        filename=image_info["filename"],
        subfolder=image_info.get("subfolder", ""),
        img_type=image_info.get("type", "output")
    )
    
    # Save image
    with open(save_path, 'wb') as f:
        f.write(image_data)
    
    # Return relative path from outputs folder
    relative_path = f"{workflow_name}/{filename}"
    
    print(f"✅ Image saved: outputs/{relative_path}")
    return relative_path