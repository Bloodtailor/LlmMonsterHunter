# ComfyUI Processor - SIMPLIFIED  
# Trusts upstream validation, focuses on image generation
print(f"🔍 Loading {__file__}")
import time
import random
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from backend.core.utils import error_response, success_response, print_success

def process_image_request(generation_id: int, callback: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
    """
    Complete image generation pipeline
    Trusts that queue already validated this is a valid image generation
    
    Args:
        generation_id (int): Database generation_logs.id
        callback (callable): Optional progress callback
        
    Returns:
        dict: Final processing results
    """
    
    try:
        # Load generation log (trust queue validation)
        from backend.models.generation_log import GenerationLog
        
        generation_log = GenerationLog.query.get(generation_id)
        image_log = generation_log.image_log
        
        # Extract parameters (trust service layer validation)
        prompt_text = generation_log.prompt_text
        workflow_name = generation_log.prompt_name
        prompt_type = generation_log.prompt_type
        
        # Mark as started
        generation_log.mark_started()
        generation_log.save()
        
        # Check ComfyUI server availability
        from .client import ComfyUIClient
        from backend.core.config.comfyui_config import get_server_url, get_timeout
        
        client = ComfyUIClient(base_url=get_server_url())
        
        if not client.is_server_running():
            error_msg = "ComfyUI server is not running"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return error_response(
                error_msg,
                generation_id=generation_id,
                help='Start ComfyUI with: python main.py --listen'
            )
        
        # Load workflow
        from .workflow import get_workflow_manager
        
        workflow_manager = get_workflow_manager()
        workflow = workflow_manager.load_workflow(workflow_name)
        
        if not workflow:
            error_msg = f"Workflow '{workflow_name}' not found"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return error_response(error_msg, generation_id=generation_id)
        
        # Build complete positive prompt
        from backend.core.config.comfyui_config import get_base_positive_prompt, get_all_generation_defaults
        
        base_prompt = get_base_positive_prompt()
        complete_positive_prompt = f"{prompt_text}, {base_prompt}"
        
        # Configure workflow
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
            seed=random.randint(1, 1000000)
        )
        
        prompt_id = client.queue_prompt(modified_workflow)
        
        result = client.wait_for_completion(
            prompt_id=prompt_id,
            timeout=config['timeout'],
            callback=callback
        )
        
        if not result.get("images"):
            error_msg = "Generation completed but no images were produced"
            generation_log.mark_failed(error_msg)
            generation_log.save()
            return error_response(error_msg, generation_id=generation_id)
        
        # Download and organize image
        image_info = result["images"][0]
        relative_path = _download_and_organize_image(
            client=client,
            image_info=image_info,
            folder_name=prompt_type
        )
        
        # Update logs with success
        image_log.mark_image_generated(relative_path)
        generation_log.mark_completed()
        
        image_log.save()
        generation_log.save()

        # Clean up ComfyUI memory
        client.unload_models()
        client.free_memory()

        return success_response({
            'image_path': relative_path,
            'execution_time': generation_log.duration_seconds or 0,
            'generation_id': generation_id,
            'workflow_used': workflow_name,
            'prompt_id': prompt_id,
            'image_dimensions': f"{config['width']}x{config['height']}"
        })
        
    except Exception as e:
        # Mark as failed and return error
        try:
            from backend.models.generation_log import GenerationLog
            log = GenerationLog.query.get(generation_id)
            if log:
                log.mark_failed(str(e))
                log.save()
        except:
            pass
        
        return error_response(str(e), generation_id=generation_id)

def _download_and_organize_image(client, image_info: Dict[str, str], folder_name: str) -> str:
    """Download and organize image with sequential numbering"""
    
    # Create output directory
    outputs_dir = Path(__file__).parent / 'outputs' / folder_name
    outputs_dir.mkdir(parents=True, exist_ok=True)
    
    # Find next available number
    existing_files = list(outputs_dir.glob("*.png"))
    if existing_files:
        numbers = []
        for file in existing_files:
            try:
                numbers.append(int(file.stem))
            except ValueError:
                continue
        next_number = max(numbers) + 1 if numbers else 1
    else:
        next_number = 1
    
    # Save image
    filename = f"{next_number:08d}.png"
    save_path = outputs_dir / filename
    
    image_data = client.download_image(
        filename=image_info["filename"],
        subfolder=image_info.get("subfolder", ""),
        img_type=image_info.get("type", "output")
    )
    
    with open(save_path, 'wb') as f:
        f.write(image_data)
    
    relative_path = f"{folder_name}/{filename}"
    print_success(f"Image saved: outputs/{relative_path}")
    return relative_path