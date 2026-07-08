# Gemini Image Provider - the cloud painter behind the image seam
# Speaks the Gemini Interactions API over plain requests (no SDK - the
# deepseek.py precedent): one blocking POST per image, text + optional
# base64 reference images in, base64 image out (JPEG - the only output
# mime the API accepts today). Reference images are the
# headline capability: identity-preserving edits, which is how Monster
# Evolution keeps a creature recognizable across its new form. The API
# key arrives from the resolved settings at call time; the model id was
# stamped into the log at request time.

import base64
from typing import Any, Optional

import requests

GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta'
CONNECT_TIMEOUT_SECONDS = 10
MODELS_READ_TIMEOUT_SECONDS = 30

# Magic bytes -> the mime type Gemini is told for a reference image
# (the same signatures portrait.py trusts for uploads)
_MIME_SIGNATURES = (
    (b'\x89PNG\r\n\x1a\n', 'image/png'),
    (b'\xff\xd8\xff', 'image/jpeg'),
    (b'RIFF', 'image/webp'),
)


def generate_image(
    prompt: str,
    api_key: str,
    model: str,
    aspect_ratio: str,
    resolution: str,
    reference_images: Optional[list[bytes]] = None,
    timeout: int = 120,
) -> dict[str, Any]:
    """
    The image provider contract.

    Returns:
        dict: {'success', 'error', 'image_bytes', 'mime_type', 'model_name'}
    """
    input_blocks: list[dict[str, Any]] = [{'type': 'text', 'text': prompt}]
    for reference_bytes in reference_images or []:
        input_blocks.append(
            {
                'type': 'image',
                'mime_type': _sniff_mime(reference_bytes),
                'data': base64.b64encode(reference_bytes).decode('ascii'),
            }
        )

    body = {
        'model': model,
        'input': input_blocks,
        'response_format': {
            # image/jpeg is the ONLY output mime the interactions API
            # accepts (soak-verified 2026-07-07: png is refused with a
            # 400); the processor files by the mime the response declares
            'type': 'image',
            'mime_type': 'image/jpeg',
            'aspect_ratio': aspect_ratio,
            'image_size': resolution,
        },
    }

    try:
        response = requests.post(
            f'{GEMINI_BASE_URL}/interactions',
            headers={'x-goog-api-key': api_key, 'Content-Type': 'application/json'},
            json=body,
            timeout=(CONNECT_TIMEOUT_SECONDS, timeout),
        )
    except requests.exceptions.RequestException as request_error:
        return _failure(f'Could not reach Gemini: {request_error}')

    if response.status_code != 200:
        return _failure(map_http_error(response))

    try:
        payload = response.json()
    except ValueError:
        return _failure('Gemini returned an unreadable response')

    encoded, mime_type = _extract_image(payload)
    if not encoded:
        return _failure('Gemini returned no image data')

    try:
        image_bytes = base64.b64decode(encoded)
    except (ValueError, TypeError):
        return _failure('Gemini returned undecodable image data')

    return {
        'success': True,
        'error': None,
        'image_bytes': image_bytes,
        'mime_type': mime_type or 'image/jpeg',
        'model_name': model,
    }


def list_models(api_key: str) -> dict[str, Any]:
    """
    Image-capable model ids from GET /models - live discovery, the
    DeepSeek precedent: new Nano Banana models work the day they ship,
    and a successful authed fetch IS key validation.
    """
    try:
        response = requests.get(
            f'{GEMINI_BASE_URL}/models',
            headers={'x-goog-api-key': api_key},
            params={'pageSize': 1000},
            timeout=(CONNECT_TIMEOUT_SECONDS, MODELS_READ_TIMEOUT_SECONDS),
        )
    except requests.exceptions.RequestException as request_error:
        return {'success': False, 'error': f'Could not reach Gemini: {request_error}', 'models': []}

    if response.status_code != 200:
        return {'success': False, 'error': map_http_error(response), 'models': []}

    try:
        entries = response.json().get('models') or []
    except ValueError:
        return {'success': False, 'error': 'Gemini returned an unreadable model list', 'models': []}

    # The id is the tail of "models/<id>"; the image models all carry
    # 'image' in the id (nano banana family) - text models stay out of
    # the picker
    models = []
    for entry in entries:
        model_id = str(entry.get('name') or '').split('/')[-1]
        if model_id and 'image' in model_id:
            models.append(model_id)

    return {'success': True, 'error': None, 'models': models}


def map_http_error(response) -> str:
    """HTTP status -> a message the settings panel can show a player"""
    try:
        detail = (response.json().get('error') or {}).get('message') or ''
    except Exception:
        detail = ''

    status = response.status_code
    if status in (401, 403):
        base = f'Gemini rejected the API key ({status}) - check it in Settings'
    elif status == 429:
        base = 'Gemini rate limit hit (429) - give it a moment and try again'
    elif status == 400:
        base = 'Gemini rejected the request (400)'
    elif status >= 500:
        base = f'Gemini server error ({status}) - try again shortly'
    else:
        base = f'Gemini returned HTTP {status}'

    return f'{base}: {detail}' if detail else base


def _extract_image(payload: dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
    """Base64 data + mime type from an interactions response: the
    output_image convenience field first, then a scan of the steps'
    model_output content blocks (interleaved outputs)"""
    convenience = payload.get('output_image') or {}
    if convenience.get('data'):
        return convenience['data'], convenience.get('mime_type')

    for step in payload.get('steps') or []:
        if step.get('type') != 'model_output':
            continue
        for block in step.get('content') or []:
            if block.get('type') == 'image' and block.get('data'):
                return block['data'], block.get('mime_type')

    return None, None


def _sniff_mime(image_bytes: bytes) -> str:
    for signature, mime_type in _MIME_SIGNATURES:
        if image_bytes.startswith(signature):
            return mime_type
    return 'image/png'


def _failure(error_message: str) -> dict[str, Any]:
    return {
        'success': False,
        'error': error_message,
        'image_bytes': None,
        'mime_type': None,
        'model_name': None,
    }
