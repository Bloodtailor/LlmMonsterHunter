# Game State Routes - SIMPLIFIED: Thin HTTP Layer Only
# Trust boundary established at service layer
# Routes only handle: HTTP parsing → Service call → HTTP response formatting

from flask import Blueprint, jsonify, request
from backend.services import game_state_service

game_state_bp = Blueprint('game_state', __name__, url_prefix='/api/game-state')

@game_state_bp.route('', methods=['GET'])
def get_game_state():
    """Get complete current game state - thin HTTP wrapper"""
    result = game_state_service.get_game_state()
    return jsonify(result), 200 if result['success'] else 500

@game_state_bp.route('/reset', methods=['POST'])
def reset_game_state():
    """Reset game state (for testing) - thin HTTP wrapper"""
    result = game_state_service.reset_game_state()
    return jsonify(result), 200 if result['success'] else 500

# === Following Monsters Management ===

@game_state_bp.route('/following/add', methods=['POST'])
def add_following_monster():
    """Add monster to following list - thin HTTP wrapper"""
    data = request.get_json() or {}
    
    result = game_state_service.add_following_monster(
        monster_id=data.get('monster_id')
    )
    
    return jsonify(result), 200 if result['success'] else 400

@game_state_bp.route('/following/remove', methods=['POST'])
def remove_following_monster():
    """Remove monster from following list - thin HTTP wrapper"""
    data = request.get_json() or {}
    
    result = game_state_service.remove_following_monster(
        monster_id=data.get('monster_id')
    )
    
    return jsonify(result), 200 if result['success'] else 400

@game_state_bp.route('/following', methods=['GET'])
def get_following_monsters():
    """Get all monsters currently following - thin HTTP wrapper"""
    result = game_state_service.get_following_monsters()
    return jsonify(result), 200 if result['success'] else 500

# === Active Party Management ===

@game_state_bp.route('/party/set', methods=['POST'])
def set_active_party():
    """Set active party from following monsters - thin HTTP wrapper"""
    data = request.get_json() or {}
    
    result = game_state_service.set_active_party(
        monster_ids=data.get('monster_ids', [])
    )
    
    return jsonify(result), 200 if result['success'] else 400

@game_state_bp.route('/party', methods=['GET'])
def get_active_party():
    """Get current active party - thin HTTP wrapper"""
    result = game_state_service.get_active_party()
    return jsonify(result), 200 if result['success'] else 500
