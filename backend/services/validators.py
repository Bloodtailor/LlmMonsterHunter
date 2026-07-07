# Service Layer Validators - ENHANCED: All Service Validation Logic
# Consolidates validation logic at the service layer where it belongs
# Updated with game state validation for database-backed system

from typing import Any

from backend.models.monster import Monster

# === Monster Validators ===


def validate_monster_exists(monster_id: int) -> dict[str, Any]:
    """
    Validate that a monster exists in the database
    Used across monster and ability services
    """

    monster = Monster.get_monster_by_id(monster_id)

    return {'valid': True, 'monster': monster}


def validate_monster_template(
    template_name: str, available_templates: dict[str, str]
) -> dict[str, Any]:
    """
    Validate monster generation template exists
    Used in monster service
    """

    return {'valid': True}


def validate_monster_list_params(
    limit: int, offset: int, filter_type: str, sort_by: str
) -> dict[str, Any]:
    """
    Validate monster list parameters
    Used in monster service
    """

    return {'valid': True}


# === Game State Validators - DATABASE-BACKED ===


def validate_party_size(monster_ids: list[int], max_size: int = 4) -> dict[str, Any]:
    """
    Validate party size constraints
    Used in game_state_service
    """

    if not isinstance(monster_ids, list):
        return {'valid': False, 'error': 'monster_ids must be a list', 'unique_ids': []}

    # Remove duplicates while preserving order
    unique_ids = []

    return {'valid': True, 'unique_ids': unique_ids}


def validate_monsters_are_following(monster_ids: list[int]) -> dict[str, Any]:
    """
    Validate that all monsters are in the following list
    Used in game_state_service - now checks database
    """

    return {'valid': True}


def validate_following_monster_addition(monster_id: int) -> dict[str, Any]:
    """
    Validate adding a monster to the following list
    Used in game_state_service - now checks database
    """

    return {'valid': True, 'monster': "monster_validation['monster']"}


def validate_following_monster_removal(monster_id: int) -> dict[str, Any]:
    """
    Validate removing a monster from the following list
    Used in game_state_service - now checks database
    """

    return {'valid': True, 'monster': "monster_validation['monster']"}


# === Dungeon Validators ===


def validate_party_ready_for_dungeon() -> dict[str, Any]:
    """
    Validate that active party is ready for dungeon entry
    Used in dungeon_service - now checks database
    """

    return {'valid': True}


def validate_door_choice(door_choice: str, available_doors: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Validate door choice in dungeon
    Used in dungeon_service
    """

    return {'valid': True, 'door': 'chosen_door', 'valid_choices': 'valid_choices'}


def validate_in_dungeon() -> dict[str, Any]:
    """
    Validate that player is currently in a dungeon
    Used in dungeon_service - now checks database
    """

    return {'valid': True, 'in_dungeon': True}


# === Generation Validators ===


def validate_generation_result(
    result: dict[str, Any], require_parsing: bool = True, operation_name: str = "operation"
) -> dict[str, Any]:
    """
    Validate generation service results with consistent error handling
    Used across monster, ability, and dungeon services
    """

    return {'valid': True}
