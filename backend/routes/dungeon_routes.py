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

@dungeon_bp.route('/choose-door', methods=['POST'])
def choose_door():
    """Choose door - thin HTTP wrapper"""
    data = request.get_json() or {}
    
    result = dungeon_service.choose_door(
        door_choice=data.get('door_choice')
    )
    
    return jsonify(result), 200 if result['success'] else 400

@dungeon_bp.route('/state', methods=['GET'])
def get_dungeon_state():
    """Get dungeon state - thin HTTP wrapper"""
    result = dungeon_service.get_dungeon_state()
    return jsonify(result), 200 if result['success'] else 400

@dungeon_bp.route('/status', methods=['GET'])
def get_dungeon_status():
    """Get dungeon status - thin HTTP wrapper"""
    result = dungeon_service.get_dungeon_status()
    return jsonify(result), 200 if result['success'] else 400