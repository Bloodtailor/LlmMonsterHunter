# Image Processor - one queued image request, end to end
# Loads the stamped log, resolves the player's image settings, reads any
# reference images from the outputs tree, calls the Gemini provider, and
# files the PNG under outputs/<prompt_type>/ with the same sequential
# numbering the ComfyUI pipeline used - serving routes and DB paths
# never notice the swap. Art stays a BONUS: every failure marks the log
# and returns an error envelope; the calling workflow carries on artless.

import contextlib
from typing import Any, Callable, Optional

from backend.core.utils import error_response, print_success, success_response


def process_image_request(
    generation_id: int, callback: Optional[Callable] = None
) -> dict[str, Any]:
    """Complete image generation pipeline (trusts queue validation)"""
    try:
        from backend.models.generation_log import GenerationLog

        generation_log = GenerationLog.query.get(generation_id)
        image_log = generation_log.image_log

        generation_log.mark_started()
        generation_log.save()

        # One elapsed-seconds pulse for the queue's update event - the
        # old ComfyUI poll loop is gone; a single blocking call paints
        if callback:
            with contextlib.suppress(Exception):
                callback(0)

        from backend.ai.image.image_settings import resolve_image_settings

        settings = resolve_image_settings()
        if not settings['enabled']:
            return _fail(
                generation_log,
                generation_id,
                'Image generation is not configured - add a Gemini API key in Settings',
            )

        params = image_log.get_params()
        model = params.get('model') or settings['model']

        from backend.ai.image import gemini
        from backend.core.config.image_config import (
            DEFAULT_ASPECT_RATIO,
            DEFAULT_RESOLUTION,
            get_timeout,
        )

        result = gemini.generate_image(
            prompt=generation_log.prompt_text,
            api_key=settings['api_key'],
            model=model,
            aspect_ratio=params.get('aspect_ratio') or DEFAULT_ASPECT_RATIO,
            resolution=params.get('resolution') or DEFAULT_RESOLUTION,
            reference_images=_load_reference_bytes(params.get('reference_images')),
            timeout=get_timeout(),
        )

        if not result['success']:
            return _fail(generation_log, generation_id, result['error'])

        relative_path = _save_image_bytes(
            result['image_bytes'], generation_log.prompt_type, result.get('mime_type')
        )

        image_log.mark_image_generated(relative_path)
        generation_log.mark_completed()
        image_log.save()
        generation_log.save()

        return success_response(
            {
                'image_path': relative_path,
                'execution_time': generation_log.duration_seconds or 0,
                'generation_id': generation_id,
                'model_name': result['model_name'],
            }
        )

    except Exception as e:
        try:
            from backend.models.generation_log import GenerationLog

            log = GenerationLog.query.get(generation_id)
            if log:
                log.mark_failed(str(e))
                log.save()
        except Exception:
            pass

        return error_response(str(e), generation_id=generation_id)


def _fail(generation_log, generation_id: int, message: str) -> dict[str, Any]:
    generation_log.mark_failed(message)
    generation_log.save()
    return error_response(message, generation_id=generation_id)


def _load_reference_bytes(reference_paths) -> list[bytes]:
    """Reference images by their outputs-relative paths. A missing file
    is skipped with a note - painting WITHOUT the reference beats not
    painting at all (art is a bonus)."""
    from backend.ai.image.paths import outputs_root

    loaded = []
    root = outputs_root()
    for relative_path in reference_paths or []:
        cleaned = str(relative_path or '').strip().replace('\\', '/')
        if not cleaned or '..' in cleaned or cleaned.startswith('/'):
            continue
        try:
            loaded.append((root / cleaned).read_bytes())
        except OSError:
            print(f"⚠️ Reference image missing, painting without it: {cleaned}")
    return loaded


# The file extension for each mime type the provider may declare
# (Gemini answers JPEG today; the ComfyUI era left PNGs behind)
_EXTENSION_BY_MIME = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
}


def _save_image_bytes(image_bytes: bytes, folder_name: str, mime_type: str = None) -> str:
    """File the image with sequential numbering (the ComfyUI-era scheme);
    the extension follows what the provider actually painted"""
    from backend.ai.image.paths import outputs_root

    target_dir = outputs_root() / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)

    numbers = []
    for existing in target_dir.iterdir():
        if not existing.is_file():
            continue
        try:
            numbers.append(int(existing.stem))
        except ValueError:
            continue
    next_number = max(numbers) + 1 if numbers else 1

    extension = _EXTENSION_BY_MIME.get(mime_type, '.png')
    filename = f"{next_number:08d}{extension}"
    (target_dir / filename).write_bytes(image_bytes)

    relative_path = f"{folder_name}/{filename}"
    print_success(f"Image saved: outputs/{relative_path}")
    return relative_path
