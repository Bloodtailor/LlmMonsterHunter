# Player Service - TRUST BOUNDARY: Validation + Delegation
# The character-creation surface: option sets, the finalize workflow,
# and the portrait stage (paint candidates / select / upload). Async
# pieces queue workflows and answer {workflow_id}; the portrait select
# and upload are synchronous (no AI involved).

from typing import Any

from backend.core.utils import error_response, success_response
from backend.workflow.workflow_gateway import request_workflow


def get_player() -> dict[str, Any]:
    """The player character, or a quiet no when none exists yet"""
    try:
        from backend.game.player.manager import get_player_monster

        player = get_player_monster()
        if player is None:
            return error_response('No player character exists yet', player=None)
        return success_response({'player': player.to_dict()})
    except Exception as e:
        return error_response(str(e))


def generate_options(field: str, choices: dict) -> dict[str, Any]:
    """Queue an option set for one creation field"""
    from backend.game.player.options import OPTION_FIELDS, clean_choices

    if not isinstance(field, str) or field not in OPTION_FIELDS:
        return error_response(f"field must be one of: {', '.join(OPTION_FIELDS)}")

    try:
        success, workflow_id = request_workflow(
            workflow_type='generate_player_options',
            context={'field': field, 'choices': clean_choices(choices)},
        )
        if success:
            return success_response({'workflow_id': workflow_id})
        return error_response('Failed to queue the options workflow')
    except Exception as e:
        return error_response(f'Workflow request failed: {str(e)}')


def create_character(payload: dict) -> dict[str, Any]:
    """Queue the character finalize. Refuses when a complete character
    already lives (New Game is the way to start over)."""
    from backend.game.player.manager import get_player_monster
    from backend.game.player.options import clean_choices

    choices = clean_choices(payload)
    if not choices.get('name'):
        return error_response('The character needs a name')
    if not choices.get('kind'):
        return error_response('The character needs a kind - what are they?')

    existing = get_player_monster()
    if existing is not None and existing.generation_stage == 'complete':
        return error_response(f'A character already exists ({existing.name}) - start a New Game first')

    try:
        success, workflow_id = request_workflow(
            workflow_type='create_player_character', context=choices
        )
        if success:
            return success_response({'workflow_id': workflow_id})
        return error_response('Failed to queue character creation')
    except Exception as e:
        return error_response(f'Workflow request failed: {str(e)}')


def generate_portrait(description: str = None) -> dict[str, Any]:
    """Queue ONE portrait candidate paint"""
    from backend.game.player.manager import player_exists
    from backend.game.utils import IMAGE_GENERATION_ENABLED

    if not player_exists():
        return error_response('No player character exists yet')
    if not IMAGE_GENERATION_ENABLED:
        return error_response('Image generation is disabled - upload an image instead, or skip')

    try:
        success, workflow_id = request_workflow(
            workflow_type='generate_player_portrait',
            context={'description': str(description or '')},
        )
        if success:
            return success_response({'workflow_id': workflow_id})
        return error_response('Failed to queue the portrait workflow')
    except Exception as e:
        return error_response(f'Workflow request failed: {str(e)}')


def select_portrait(image_path: str) -> dict[str, Any]:
    """Make a painted candidate or an upload THE portrait (synchronous)"""
    from backend.game.player.manager import get_player_monster
    from backend.game.player.portrait import candidate_path_error
    from backend.game.player.portrait import select_portrait as apply

    player = get_player_monster()
    if player is None:
        return error_response('No player character exists yet')

    path_error = candidate_path_error(image_path)
    if path_error:
        return error_response(path_error)

    try:
        selected = apply(player, image_path)
        return success_response({'image_path': selected, 'monster': player.to_dict()})
    except Exception as e:
        return error_response(str(e))


def upload_portrait(filename: str, data: bytes) -> dict[str, Any]:
    """Store an uploaded image and make it the portrait (synchronous).
    Uploads auto-select - the player chose this file on purpose."""
    from backend.game.player.manager import get_player_monster
    from backend.game.player.portrait import save_upload, upload_error
    from backend.game.player.portrait import select_portrait as apply

    player = get_player_monster()
    if player is None:
        return error_response('No player character exists yet')

    refusal = upload_error(filename, data)
    if refusal:
        return error_response(refusal)

    try:
        image_path = save_upload(filename, data)
        apply(player, image_path)
        return success_response({'image_path': image_path, 'monster': player.to_dict()})
    except Exception as e:
        return error_response(str(e))
