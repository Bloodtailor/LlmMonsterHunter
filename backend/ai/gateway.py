# AI gateway - formerly generation_service.py
# THE ONLY WAY to request any AI generation (LLM or Image)
# Creates normalized generation_log entries and delegates to unified queue
import time
from typing import Any, Optional

from backend.core.config.llm_config import get_all_inference_defaults
from backend.core.utils import print_success, print_warning
from backend.models.generation_log import GenerationLog

from .queue import get_ai_queue


def text_generation_request(
    prompt: str,
    prompt_type: str = None,
    prompt_name: str = None,
    parser_config: Optional[dict[str, Any]] = None,
    return_early: bool = False,
    **inference_overrides,
) -> dict[str, Any]:
    """
    THE ONLY WAY to request LLM text generation
    Creates complete generation_log entry and delegates to unified queue

    Args:
        prompt (str): Text to generate from (ONLY REQUIRED parameter)
        prompt_type (str): Type of prompt (optional)
        prompt_name (str): Specific prompt name (optional)
        parser_config (dict): Parser configuration for automatic parsing (optional)
        retrun_early (bool): Return without waiting for completion (optional)
        **inference_overrides: Any inference parameter overrides

    Returns:
        dict: Results from pipeline processing
    """

    # Get inference defaults and apply overrides
    inference_params = get_all_inference_defaults()

    for key, value in inference_overrides.items():
        if key not in inference_params:
            print_warning(f"Unknown override: {key}")
        elif value is not None:
            inference_params[key] = value

    if prompt_type is None:
        prompt_type = inference_params['prompt_type']
    if prompt_name is None:
        prompt_name = inference_params['prompt_name']

    # Which engine speaks - resolved ONCE here and stamped into the log,
    # so a queued request keeps its provider even if settings change
    # before it processes (locked decision, docs/plans/game-settings.md)
    from backend.ai.llm.provider_settings import (
        resolve_llm_settings,
        should_apply_nothink_prefill,
    )

    llm_settings = resolve_llm_settings()

    # Suppress reasoning-model <think> blocks by prefilling an empty one.
    # Applied HERE, before logging, so generation_log.prompt_text is
    # byte-exact with what the model receives (the dev table shows truth).
    # Local raw-completion only: DeepSeek is a chat API and gets thinking
    # disabled as a request parameter instead.
    from backend.core.config.llm_config import NOTHINK_PREFILL

    if should_apply_nothink_prefill(llm_settings['provider']):
        prompt = prompt + NOTHINK_PREFILL

    # Show simplified request info
    truncated_prompt = prompt[:50] + "..." if len(prompt) > 50 else prompt
    print_success(f"Text generation request: {prompt_type}/{prompt_name} - \"{truncated_prompt}\"")

    # Create generation log entry
    generation_log = GenerationLog.create_llm_log(
        prompt_type=prompt_type,
        prompt_name=prompt_name,
        prompt_text=prompt,
        inference_params=inference_params,
        parser_config=parser_config,
        provider=llm_settings['provider'],
        model_name=llm_settings['model_name'],
    )

    if not generation_log or not generation_log.save():
        raise Exception('Failed to create generation log entry')

    # Add to unified queue
    queue = get_ai_queue()

    if not queue.add_request(generation_log.id):
        raise Exception(f'Failed to add request to queue (generation_id={generation_log.id})')

    if return_early:
        return {'generation_id': generation_log.id}
    # Wait for completion
    return _wait_for_completion(queue, generation_log.id, 'llm')


def image_generation_request(
    prompt_text: str,
    prompt_type: str = "image_generation",
    prompt_name: str = "card_art",
    reference_images: Optional[list] = None,
    return_early: bool = False,
    **image_overrides,
) -> dict[str, Any]:
    """
    THE ONLY WAY to request image generation
    Creates complete generation_log entry and delegates to unified queue

    Args:
        prompt_text (str): The image's subject (ONLY REQUIRED parameter)
        prompt_type (str): Filed under outputs/<prompt_type>/ and logged
        prompt_name (str): Log label (the ComfyUI workflow-name concept
            died with the ComfyUI pipeline)
        reference_images (list): Outputs-relative paths whose bytes ride
            along as Gemini reference images (evolution passes the old
            card art so the new form stays recognizably the same being)
        return_early (bool): Return without waiting for completion
        **image_overrides: model / aspect_ratio / resolution overrides

    Returns:
        dict: Results from image generation pipeline
    """
    from backend.ai.image.image_settings import resolve_image_settings
    from backend.core.config.image_config import (
        DEFAULT_ASPECT_RATIO,
        DEFAULT_RESOLUTION,
        compose_image_prompt,
    )

    settings = resolve_image_settings()
    if not settings['enabled']:
        raise Exception('Image generation is not configured - add a Gemini API key in Settings')

    # The house style + avoid-instruction join HERE, before logging, so
    # generation_log.prompt_text is byte-exact with what the model
    # receives (the nothink-prefill precedent: the dev table shows truth)
    complete_prompt = compose_image_prompt(prompt_text)

    # Show simplified request info
    truncated_prompt = prompt_text[:50] + "..." if len(prompt_text) > 50 else prompt_text
    print_success(f"Image generation request: {prompt_name} - \"{truncated_prompt}\"")

    # Model and geometry stamped NOW so a queued paint keeps its setup
    # even if settings change before it processes (the LLM-seam rule)
    image_params = {
        'model': image_overrides.get('model') or settings['model'],
        'aspect_ratio': image_overrides.get('aspect_ratio') or DEFAULT_ASPECT_RATIO,
        'resolution': image_overrides.get('resolution') or DEFAULT_RESOLUTION,
        'reference_images': [str(path) for path in (reference_images or [])],
    }

    # Create generation log entry
    generation_log = GenerationLog.create_image_log(
        prompt_type=prompt_type,
        prompt_name=prompt_name,
        prompt_text=complete_prompt,
        image_params=image_params,
    )

    if not generation_log or not generation_log.save():
        raise Exception('Failed to create image generation log entry')

    # Add to unified queue

    queue = get_ai_queue()

    if not queue.add_request(generation_log.id):
        raise Exception(f'Failed to add image request to queue (generation_id={generation_log.id})')

    if return_early:
        return {'generation_id': generation_log.id}

    # Wait for completion
    return _wait_for_completion(queue, generation_log.id, 'image')


def _wait_for_completion(
    queue, generation_id: int, generation_type: str, timeout: int = 600
) -> dict[str, Any]:
    """
    Wait for generation completion with unified handling

    Args:
        queue: AI generation queue instance
        generation_id (int): Generation ID to wait for
        generation_type (str): 'llm' or 'image'
        timeout (int): Timeout in seconds

    Returns:
        dict: Completion results
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        status = queue.get_request_status(generation_id)

        if not status:
            # Pruning keeps finished items well past this waiter's timeout,
            # so a vanished record is a real anomaly - name it honestly
            # instead of reporting a fake timeout
            raise Exception(
                f'{generation_type.upper()} generation {generation_id} '
                'record vanished while waiting for completion'
            )

        if status['status'] == 'completed':
            result = status['result']

            if generation_type == 'llm':
                return {
                    'generation_id': generation_id,
                    'success': result.get('success', None),
                    'error': result.get('error', None),
                    'text': result.get('text', ''),
                    'parsing_success': result.get('parsing_success', None),
                    'parsing_error': result.get('parsing_error', None),
                    'parsed_data': result.get('parsed_data', None),
                }
            elif generation_type == 'image':
                return {
                    'generation_id': generation_id,
                    'success': result.get('success', None),
                    'error': result.get('error', None),
                    'image_path': result.get('image_path', ''),
                    'model_name': result.get('model_name'),
                }

        if status['status'] == 'failed':
            raise Exception(
                f"{generation_type.upper()} generation {generation_id} failed: "
                f"{status.get('error', 'Processing failed')}"
            )

        time.sleep(0.5)

    raise TimeoutError(
        f'{generation_type.upper()} generation {generation_id} timed out after {timeout} seconds'
    )


# Export main functions
__all__ = ['text_generation_request', 'image_generation_request']
