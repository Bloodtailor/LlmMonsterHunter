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

@dungeon_bp.route('/answer-riddle', methods=['POST'])
def answer_riddle():
    """Answer the active riddle - thin HTTP wrapper"""
    data = request.get_json() or {}

    result = dungeon_service.answer_riddle(
        player_answer=data.get('answer')
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
