# Monster Service - GREATLY SIMPLIFIED: Minimal Trust Boundary
# Only validates what routes absolutely cannot handle
# Eliminates all redundant error checking

from typing import Any

from backend.core.utils import error_response, success_response, validate_and_continue
from backend.game import monster
from backend.workflow.workflow_gateway import request_workflow

from .validators import validate_monster_list_params


def generate_monster() -> dict[str, Any]:
    """Generate monster using workflow system - queued processing"""

    try:
        # Request workflow execution
        success, workflow_id = request_workflow(workflow_type="generate_detailed_monster")

        if success:
            return success_response({'workflow_id': workflow_id})
        else:
            return error_response('Failed to queue monster generation workflow')

    except Exception as e:
        return error_response(f'Workflow request failed: {str(e)}')


def get_all_monsters(
    limit: int = None, offset: int = 0, filter_type: str = 'all', sort_by: str = 'newest'
) -> dict[str, Any]:
    """Get monsters - validate complex parameters"""

    params_validation = validate_monster_list_params(limit, offset, filter_type, sort_by)
    error_check = validate_and_continue(params_validation)
    if error_check:
        return error_check

    return monster.manager.get_all_monsters(limit, offset, filter_type, sort_by)


def get_monster_stats(filter_type: str = 'all') -> dict[str, Any]:
    """Get stats - validate filter parameter"""

    valid_filters = ['all', 'with_art', 'without_art']
    if filter_type not in valid_filters:
        return error_response(f'Invalid filter parameter - must be: {", ".join(valid_filters)}')

    return monster.manager.get_monster_stats(filter_type)


def get_monster_by_id(monster_id: int) -> dict[str, Any]:
    """Get monster - delegate directly (routes handle integer validation)"""
    return monster.manager.get_monster_by_id(monster_id)


def get_monster_memories(monster_id: int) -> dict[str, Any]:
    """A monster's permanent memories, oldest first (its life in order)"""
    from backend.models.monster import Monster
    from backend.models.monster_memory import MonsterMemory

    if not Monster.get_monster_by_id(monster_id):
        return error_response('Monster not found')

    memories = MonsterMemory.for_monster(monster_id)
    return success_response(
        {'monster_id': monster_id, 'memories': [memory.to_dict() for memory in memories]}
    )


def evolve_monster(monster_id, guidance=None) -> dict[str, Any]:
    """
    Evolve a following monster at home base - queues the ceremony
    workflow; the transform and narration arrive over SSE.
    """
    from backend.game.monster.evolution import GUIDANCE_MAX_CHARS, clean_guidance
    from backend.game.monster.evolution_eligibility import evolution_eligibility_error

    try:
        monster_id = int(monster_id)
    except (TypeError, ValueError):
        return error_response("A valid monster_id is required")

    eligibility_error = evolution_eligibility_error(monster_id)
    if eligibility_error:
        return error_response(eligibility_error)

    if guidance and len(str(guidance).strip()) > GUIDANCE_MAX_CHARS:
        return error_response(f"Guidance too long (max {GUIDANCE_MAX_CHARS} characters)")

    try:
        success, workflow_id = request_workflow(
            workflow_type="evolve_monster",
            context={"monster_id": monster_id, "guidance": clean_guidance(guidance)},
        )
        if success:
            return success_response({'workflow_id': workflow_id})
        return error_response('Failed to queue evolution workflow')
    except Exception as e:
        return error_response(f'Workflow request failed: {str(e)}')


def get_monster_evolutions(monster_id: int) -> dict[str, Any]:
    """A monster's evolution lineage, oldest first (its forms in order)"""
    from backend.models.monster import Monster
    from backend.models.monster_evolution import MonsterEvolution

    if not Monster.get_monster_by_id(monster_id):
        return error_response('Monster not found')

    evolutions = MonsterEvolution.for_monster(monster_id)
    return success_response(
        {'monster_id': monster_id, 'evolutions': [evolution.to_dict() for evolution in evolutions]}
    )


def generate_ability(monster_id: int) -> dict[str, Any]:
    """Generate ability - only validate monster exists"""

    try:
        # Request workflow execution
        success, workflow_id = request_workflow(
            workflow_type="generate_ability", context={"monster_id": monster_id}
        )

        if success:
            return success_response({'workflow_id': workflow_id})
        else:
            return error_response('Failed to queue ability generation workflow')

    except Exception as e:
        return error_response(f'Workflow request failed: {str(e)}')
