# Game State Routes - Testing and Party Management
# Provides API endpoints for managing game state and party

from flask import Blueprint, jsonify, request
from backend.services import game_state_service

game_state_bp = Blueprint('game_state', __name__, url_prefix='/api/game-state')

@game_state_bp.route('', methods=['GET'])
def get_game_state():
    """Get complete current game state"""
    try:
        result = game_state_service.get_game_state()
        return jsonify({'success': True, 'game_state': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@game_state_bp.route('/reset', methods=['POST'])
def reset_game_state():
    """Reset game state (for testing)"""
    try:
        result = game_state_service.reset_game_state()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Following Monsters Management
@game_state_bp.route('/following/add', methods=['POST'])
def add_following_monster():
    """Add monster to following list (for testing)"""
    try:
        data = request.get_json() or {}
        monster_id = data.get('monster_id')
        
        if not monster_id:
            return jsonify({
                'success': False,
                'error': 'monster_id is required'
            }), 400
        
        result = game_state_service.add_following_monster(monster_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@game_state_bp.route('/following/remove', methods=['POST'])
def remove_following_monster():
    """Remove monster from following list"""
    try:
        data = request.get_json() or {}
        monster_id = data.get('monster_id')
        
        if not monster_id:
            return jsonify({
                'success': False,
                'error': 'monster_id is required'
            }), 400
        
        result = game_state_service.remove_following_monster(monster_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@game_state_bp.route('/following', methods=['GET'])
def get_following_monsters():
    """Get all monsters currently following"""
    try:
        result = game_state_service.get_following_monsters()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Active Party Management
@game_state_bp.route('/party/set', methods=['POST'])
def set_active_party():
    """Set active party from following monsters"""
    try:
        data = request.get_json() or {}
        monster_ids = data.get('monster_ids', [])
        
        if not isinstance(monster_ids, list):
            return jsonify({
                'success': False,
                'error': 'monster_ids must be a list'
            }), 400
        
        result = game_state_service.set_active_party(monster_ids)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@game_state_bp.route('/party', methods=['GET'])
def get_active_party():
    """Get current active party"""
    try:
        result = game_state_service.get_active_party()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@game_state_bp.route('/party/ready', methods=['GET'])
def check_party_ready():
    """Check if party is ready for dungeon"""
    try:
        ready = game_state_service.is_party_ready_for_dungeon()
        summary = game_state_service.get_party_summary()
        
        return jsonify({
            'success': True,
            'ready_for_dungeon': ready,
            'party_summary': summary,
            'message': 'Party is ready for adventure!' if ready else 'Add monsters to your party before entering the dungeon'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500