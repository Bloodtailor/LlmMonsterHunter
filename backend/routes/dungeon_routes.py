# Dungeon Routes - SIMPLIFIED: Thin HTTP Layer Only
# Trust boundary established at service layer
# Routes only handle: HTTP parsing → Service call → HTTP response formatting

from flask import Blueprint, jsonify, request
from backend.services import dungeon_service

dungeon_bp = Blueprint('dungeon', __name__, url_prefix='/api/dungeon')

@dungeon_bp.route('/enter', methods=['GET'])
def enter_dungeon():
    """Enter dungeon - thin HTTP wrapper"""
    result = dungeon_service.enter_dungeon()
    return jsonify(result), 200 if result['success'] else 400

@dungeon_bp.route('/choose-path', methods=['POST'])
def choose_path():
    """Choose a path - thin HTTP wrapper"""
    data = request.get_json() or {}

    result = dungeon_service.choose_path(
        path_id=data.get('path_id')
    )

    return jsonify(result), 200 if result['success'] else 400

@dungeon_bp.route('/respond', methods=['POST'])
def respond_to_monster():
    """Speak to the encounter monsters - thin HTTP wrapper"""
    data = request.get_json() or {}

    result = dungeon_service.respond_to_monster(
        message=data.get('message')
    )

    return jsonify(result), 200 if result['success'] else 400

@dungeon_bp.route('/sneak', methods=['POST'])
def sneak_past():
    """Attempt to sneak past the monsters in the area - thin HTTP wrapper"""
    result = dungeon_service.sneak_past()
    return jsonify(result), 200 if result['success'] else 400

@dungeon_bp.route('/surprise-attack', methods=['POST'])
def surprise_attack():
    """Spring a surprise attack on the monsters in the area - thin HTTP wrapper"""
    result = dungeon_service.surprise_attack()
    return jsonify(result), 200 if result['success'] else 400

@dungeon_bp.route('/camp', methods=['POST'])
def setup_camp():
    """Set up camp in a monster-free location - thin HTTP wrapper"""
    result = dungeon_service.setup_camp()
    return jsonify(result), 200 if result['success'] else 400

@dungeon_bp.route('/use-ability', methods=['POST'])
def use_ability():
    """Use a party monster's ability on anything (outside battle) - thin HTTP wrapper"""
    data = request.get_json() or {}

    result = dungeon_service.use_ability(
        monster_id=data.get('monster_id'),
        ability_id=data.get('ability_id'),
        target_type=data.get('target_type'),
        target_id=data.get('target_id'),
        target_text=data.get('target_text')
    )

    return jsonify(result), 200 if result['success'] else 400

@dungeon_bp.route('/use-item', methods=['POST'])
def use_item():
    """Use an inventory item on anything (outside battle) - thin HTTP wrapper"""
    data = request.get_json() or {}

    result = dungeon_service.use_item(
        item_id=data.get('item_id'),
        target_type=data.get('target_type'),
        target_id=data.get('target_id'),
        target_text=data.get('target_text')
    )

    return jsonify(result), 200 if result['success'] else 400

@dungeon_bp.route('/continue', methods=['POST'])
def continue_exploring():
    """Generate fresh paths from the current location - thin HTTP wrapper"""
    result = dungeon_service.continue_exploring()
    return jsonify(result), 200 if result['success'] else 400

@dungeon_bp.route('/state', methods=['GET'])
def get_dungeon_state():
    """Get public dungeon state - thin HTTP wrapper"""
    result = dungeon_service.get_dungeon_state()
    return jsonify(result), 200 if result['success'] else 400

@dungeon_bp.route('/abandon', methods=['POST'])
def abandon_run():
    """Call the party home mid-run (closes the run as abandoned) - thin HTTP wrapper"""
    result = dungeon_service.abandon_run()
    return jsonify(result), 200 if result['success'] else 400

@dungeon_bp.route('/debug-context', methods=['GET'])
def get_debug_context():
    """DEVELOPER ONLY: full LLM context X-ray (includes hidden info) - thin HTTP wrapper"""
    result = dungeon_service.get_debug_context()
    return jsonify(result), 200 if result['success'] else 400
