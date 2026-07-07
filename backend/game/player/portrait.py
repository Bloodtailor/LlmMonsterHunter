# Player Portrait - candidates, selection, and uploads
# The portrait stage is player-controlled: paint as many CANDIDATES as
# they like (each an ordinary gateway image request whose path is only
# ever a candidate), pick one, or upload their own image. Nothing
# touches monster.card_art_path until an explicit selection - and art
# is a bonus, never a blocker: skipping is always allowed.
#
# Uploads land beside generated art in the image outputs tree
# (outputs/player_uploads/) so the existing card-art serving route and
# every cardArt-consuming component work unchanged.

from pathlib import Path
from typing import Optional

from backend.ai import gateway
from backend.core.events import emit_monster_art_ready
from backend.models.monster import Monster

# Where candidate paths may live (anything else is refused on select)
GENERATED_FOLDER = 'player_card_art'
UPLOAD_FOLDER = 'player_uploads'

# Upload guardrails: real image files only, kept small enough to serve
UPLOAD_MAX_BYTES = 8 * 1024 * 1024
# Extension -> the file-signature prefixes that must match (magic bytes;
# a renamed .exe must not become card art)
UPLOAD_SIGNATURES = {
    '.png': (b'\x89PNG\r\n\x1a\n',),
    '.jpg': (b'\xff\xd8\xff',),
    '.jpeg': (b'\xff\xd8\xff',),
    '.webp': (b'RIFF',),  # full check also requires WEBP at offset 8
}


def outputs_dir() -> Path:
    """The image outputs root (same tree the serving route reads)"""
    from backend.ai.image.paths import outputs_root

    return outputs_root()


def compose_portrait_prompt(monster: Monster, description: str) -> str:
    """The image prompt: identity framing + the (possibly re-edited)
    appearance text - the same recipe as monster card art, with the
    player's words as the brief"""
    taxonomy = monster.taxonomy or {}
    ecology = monster.ecology or {}
    parts = [
        monster.name,
        taxonomy.get('race_label') or monster.species,
        ecology.get('size_class') or '',
        description,
    ]
    return ", ".join(part for part in parts if part)


def generate_portrait_candidate(monster: Monster, description: str) -> str:
    """One painted CANDIDATE. Returns its relative path; card_art_path
    is untouched (selection is a separate, explicit act). Raises when
    image generation is disabled or the paint fails."""
    result = gateway.image_generation_request(
        prompt_text=compose_portrait_prompt(monster, description),
        prompt_type=GENERATED_FOLDER,  # the processor files images by prompt_type
        prompt_name='card_art',  # the shared log label for painted art
    )
    image_path = result.get('image_path')
    if not image_path:
        raise Exception('The portrait came back empty')
    return image_path


def candidate_path_error(image_path: str) -> Optional[str]:
    """Why this path cannot become the portrait, or None if it can:
    must be a real file inside one of the portrait folders"""
    if not isinstance(image_path, str) or not image_path.strip():
        return 'An image path is required'
    cleaned = image_path.strip().replace('\\', '/')
    if '..' in cleaned or cleaned.startswith('/'):
        return 'Invalid image path'
    folder = cleaned.split('/', 1)[0]
    if folder not in (GENERATED_FOLDER, UPLOAD_FOLDER):
        return 'Only painted candidates or uploads can become the portrait'
    if not (outputs_dir() / cleaned).is_file():
        return 'That image does not exist'
    return None


def select_portrait(monster: Monster, image_path: str) -> str:
    """Make a validated candidate THE portrait (the one write to
    card_art_path in the whole portrait stage)"""
    cleaned = image_path.strip().replace('\\', '/')
    monster.set_card_art(cleaned)
    emit_monster_art_ready(monster.id, cleaned)
    return cleaned


def upload_error(filename: str, data: bytes) -> Optional[str]:
    """Why this upload is refused, or None if it is a real, small image"""
    extension = Path(filename or '').suffix.lower()
    if extension not in UPLOAD_SIGNATURES:
        allowed = ", ".join(sorted(UPLOAD_SIGNATURES))
        return f'Only image files are accepted ({allowed})'
    if not data:
        return 'The uploaded file is empty'
    if len(data) > UPLOAD_MAX_BYTES:
        return f'Image too large (max {UPLOAD_MAX_BYTES // (1024 * 1024)}MB)'
    if not any(data.startswith(signature) for signature in UPLOAD_SIGNATURES[extension]):
        return 'That file does not look like a real image'
    if extension == '.webp' and data[8:12] != b'WEBP':
        return 'That file does not look like a real image'
    return None


def save_upload(filename: str, data: bytes) -> str:
    """Store a validated upload with the same sequential naming the
    generated art uses. Returns the relative path (a candidate - the
    caller decides whether to select it)."""
    extension = Path(filename).suffix.lower()
    upload_dir = outputs_dir() / UPLOAD_FOLDER
    upload_dir.mkdir(parents=True, exist_ok=True)

    numbers = []
    for existing in upload_dir.iterdir():
        try:
            numbers.append(int(existing.stem))
        except ValueError:
            continue
    next_number = max(numbers) + 1 if numbers else 1

    saved_name = f"{next_number:08d}{extension}"
    with open(upload_dir / saved_name, 'wb') as destination:
        destination.write(data)
    return f"{UPLOAD_FOLDER}/{saved_name}"
