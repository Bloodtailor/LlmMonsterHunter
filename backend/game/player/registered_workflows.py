# Registers as a callable function for the game orchestration queue to use
print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from typing import Any, Callable

from backend.core.utils.responses import error_response, success_response
from backend.core.utils.validation import require_keys
from backend.core.workflow_registry import register_workflow


@register_workflow()
def generate_player_options(
    context: dict, on_update: Callable[[str, dict[str, Any]], None]
) -> dict:
    """One small LLM call: distinct options for ONE character-creation
    field, conditioned on the choices made so far"""

    required_keys = ["field"]

    step = "initializing"
    progress_data = {}

    try:
        from backend.game.player.options import OPTION_FIELDS, clean_choices, generate_options

        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        field = str(context['field'])
        if field not in OPTION_FIELDS:
            raise Exception(
                f"Unknown creation field '{field}' - one of: {', '.join(OPTION_FIELDS)}"
            )
        choices = clean_choices(context.get('choices'))

        step = "generating_options"
        on_update(step, progress_data)
        options = generate_options(field, choices)
        progress_data.update({"field": field, "options": options})

        return success_response(progress_data)

    except Exception as e:
        return error_response({'failed_at': step, 'completed_work': progress_data, 'error': str(e)})


@register_workflow()
def create_player_character(
    context: dict, on_update: Callable[[str, dict[str, Any]], None]
) -> dict:
    """
    The player's answers become their character: staged like monster
    generation (identity -> persona -> story -> two abilities), each
    stage conditioned on the player's own words. Emits the standard
    monster.* events, so the frontend card reveal works unchanged. A
    half-built character from an earlier failed attempt is discarded
    first; a COMPLETE one refuses (New Game is the way to start over).
    """

    step = "initializing"
    progress_data = {}

    try:
        from backend.game.monster.generator import generate_ability
        from backend.game.player.creation import (
            create_player_blueprint,
            create_player_persona,
            create_player_story,
            discard_partial_player,
        )
        from backend.game.player.manager import get_player_monster
        from backend.game.player.options import clean_choices

        # Step 0 - validate (re-checked here: the queue may run this
        # long after the service said yes)
        step = "validate_context"
        on_update(step, progress_data)
        choices = clean_choices(context)
        if not choices.get('name'):
            raise Exception('The character needs a name')
        if not choices.get('kind'):
            raise Exception('The character needs a kind - what are they?')

        existing = get_player_monster()
        if existing is not None and existing.generation_stage == 'complete':
            raise Exception(
                f'A character already exists ({existing.name}) - start a New Game first'
            )
        discard_partial_player()

        # Step 1 - taxonomy placement + code-derived stats (row saved
        # and the player pointer set here)
        step = "building_identity"
        on_update(step, progress_data)
        monster = create_player_blueprint(choices)
        progress_data.update({"monster": monster.to_dict()})

        # Step 2 - the player's answers expand into the persona
        step = "shaping_persona"
        on_update(step, progress_data)
        monster = create_player_persona(monster, choices)
        progress_data.update({"monster": monster.to_dict()})

        # Step 3 - prose; the appearance text is kept verbatim
        step = "writing_story"
        on_update(step, progress_data)
        monster = create_player_story(monster, choices)
        progress_data.update({"monster": monster.to_dict()})

        # Steps 4-5 - the adventurer's own talents
        step = "adding_first_ability"
        on_update(step, progress_data)
        ability_1 = generate_ability(monster)
        progress_data.update({"ability_1": ability_1.to_dict()})

        step = "adding_second_ability"
        on_update(step, progress_data)
        ability_2 = generate_ability(monster)
        progress_data.update({"ability_2": ability_2.to_dict()})

        # No card art here - the portrait stage is its own, player-paced
        # step (candidates, uploads, or skip; art never blocks)
        return success_response(progress_data)

    except Exception as e:
        return error_response({'failed_at': step, 'completed_work': progress_data, 'error': str(e)})


@register_workflow()
def generate_player_portrait(
    context: dict, on_update: Callable[[str, dict[str, Any]], None]
) -> dict:
    """Paint ONE portrait candidate from the given description (default:
    the character's own appearance text). The result carries the image
    path; card_art_path is untouched until the player selects."""

    step = "initializing"
    progress_data = {}

    try:
        from backend.game.player.manager import get_player_monster
        from backend.game.player.options import FIELD_MAX_CHARS
        from backend.game.player.portrait import generate_portrait_candidate

        step = "validate_context"
        on_update(step, progress_data)
        monster = get_player_monster()
        if monster is None:
            raise Exception('No player character exists yet')

        description = str(context.get('description') or '').strip()
        if not description:
            appearance = monster.appearance or {}
            description = appearance.get('visual_description') or monster.description
        description = description[: FIELD_MAX_CHARS['appearance']]

        step = "painting_portrait"
        on_update(step, progress_data)
        image_path = generate_portrait_candidate(monster, description)
        progress_data.update(
            {"image_path": image_path, "description": description, "monster_id": monster.id}
        )

        return success_response(progress_data)

    except Exception as e:
        return error_response({'failed_at': step, 'completed_work': progress_data, 'error': str(e)})
