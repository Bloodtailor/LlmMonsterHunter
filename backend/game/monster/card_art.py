# Card Art - a monster's face, generated through the gateway's image
# pipeline. Art is a BONUS, never a blocker: when image generation is
# disabled (or ComfyUI fails) the monster simply stays art-less - the
# frontend fully supports that - and the workflow that wanted the art
# carries on.

from backend.ai import gateway
from backend.core.events import emit_monster_art_ready
from backend.models.monster import Monster


def generate_card_art(monster: Monster):
    """Generate and connect card art (quietly skipped when disabled)"""
    from backend.game.utils import IMAGE_GENERATION_ENABLED

    if not IMAGE_GENERATION_ENABLED:
        return None

    try:
        prompt_text = _build_card_art_prompt(monster)

        image_result = gateway.image_generation_request(
            prompt_text=prompt_text,
            prompt_type="monster_card_art",
            prompt_name="monster_generation",
        )

        image_path = image_result.get('image_path')
        if not image_path:
            return None

        monster.set_card_art(image_path)

        # The monster's card art is now attached
        emit_monster_art_ready(monster.id, image_path)

        return image_path
    except Exception as art_error:
        print(f"❌ Card art failed for {monster.name} (the monster stands): {art_error}")
        return None


def _build_card_art_prompt(monster: Monster):
    """Image prompt from the structured appearance block (falls back to
    prose description for monsters that lack one)"""

    taxonomy = monster.taxonomy or {}
    ecology = monster.ecology or {}
    appearance = monster.appearance or {}

    prompt_parts = [
        monster.name,
        taxonomy.get('race_label') or monster.species,
        ecology.get('size_class') or '',
        appearance.get('visual_description') or monster.description,
    ]

    colors = appearance.get('primary_colors') or []
    if colors:
        prompt_parts.append("colors: " + ", ".join(colors))

    features = appearance.get('distinguishing_features') or []
    if features:
        prompt_parts.append(", ".join(features))

    return ", ".join(part for part in prompt_parts if part)
