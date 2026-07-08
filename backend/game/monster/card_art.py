# Card Art - a monster's face, generated through the gateway's image
# pipeline. Art is a BONUS, never a blocker: when image generation is
# not configured (or the paint fails) the monster simply stays art-less
# - the frontend fully supports that - and the workflow that wanted the
# art carries on.

from backend.ai import gateway
from backend.core.events import emit_monster_art_ready
from backend.models.monster import Monster

# The transformation brief for evolution repaints: the old face rides
# along as a reference image (Gemini character consistency) and this
# line tells the model what that reference IS
EVOLUTION_REPAINT_INSTRUCTION = (
    'This creature is evolving into a new form. Repaint it as the SAME '
    'being shown in the reference image, transformed - keep its identity, '
    'colors and silhouette recognizable through the change.'
)


def generate_card_art(monster: Monster):
    """Generate and connect card art (quietly skipped when disabled)"""
    from backend.game.utils import is_image_generation_enabled

    if not is_image_generation_enabled():
        return None

    return _paint_and_attach(monster, _build_card_art_prompt(monster), 'card_art')


def generate_evolved_card_art(monster: Monster, old_art_path: str = None):
    """Card art for a JUST-EVOLVED monster: the old face rides along as
    a reference image so the new form stays recognizably the same being.
    Falls back to a plain paint when there is no old art. Returns the
    new path, or None when nothing was painted."""
    from backend.game.utils import is_image_generation_enabled

    if not is_image_generation_enabled():
        return None

    if not old_art_path:
        return _paint_and_attach(monster, _build_card_art_prompt(monster), 'card_art')

    prompt_text = (
        f"{EVOLUTION_REPAINT_INSTRUCTION} Its evolved appearance: {_build_card_art_prompt(monster)}"
    )
    return _paint_and_attach(
        monster, prompt_text, 'evolution_card_art', reference_images=[old_art_path]
    )


def _paint_and_attach(monster: Monster, prompt_text: str, prompt_name: str, reference_images=None):
    """One paint through the gateway; on success the path is attached
    and announced. Failures return None - the monster stands."""
    try:
        image_result = gateway.image_generation_request(
            prompt_text=prompt_text,
            prompt_type="monster_card_art",
            prompt_name=prompt_name,
            reference_images=reference_images,
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
    """A natural-language subject from the structured appearance block
    (falls back to prose description for monsters that lack one) - the
    Gemini models want sentences, not the old SD tag-soup"""

    taxonomy = monster.taxonomy or {}
    ecology = monster.ecology or {}
    appearance = monster.appearance or {}

    race = taxonomy.get('race_label') or monster.species
    size = ecology.get('size_class')
    creature = f"a {size} {race}" if size else f"a {race}"
    description = str(appearance.get('visual_description') or monster.description or '').strip()

    sentences = [f"A portrait of {monster.name}, {creature}.", description]

    colors = appearance.get('primary_colors') or []
    if colors:
        sentences.append(f"Its main colors are {_join_naturally(colors)}.")

    features = appearance.get('distinguishing_features') or []
    if features:
        sentences.append(f"Distinguishing features: {_join_naturally(features)}.")

    return ' '.join(sentence for sentence in sentences if sentence)


def _join_naturally(items: list) -> str:
    """'a, b and c' - list punctuation for prompt sentences"""
    cleaned = [str(item).strip() for item in items if str(item).strip()]
    if not cleaned:
        return ''
    if len(cleaned) == 1:
        return cleaned[0]
    return ', '.join(cleaned[:-1]) + ' and ' + cleaned[-1]
