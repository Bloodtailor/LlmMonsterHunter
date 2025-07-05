# Dungeon Routes - Basic Dungeon Flow API
# Provides endpoints for dungeon entry, door choices, and exit

from flask import Blueprint, jsonify, request
from backend.services import dungeon_service

dungeon_bp = Blueprint('dungeon', __name__, url_prefix='/api/dungeon')

@dungeon_bp.route('/enter', methods=['POST'])
def enter_dungeon():
    """
    Enter the dungeon with current active party
    Generates entry text, initial location, and door choices
    """
    try:
        result = dungeon_service.enter_dungeon()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'dungeon_entered': False
        }), 500

@dungeon_bp.route('/choose-door', methods=['POST'])
def choose_door():
    """
    Choose a door in the dungeon
    Handles both location doors and exit door
    """
    try:
        data = request.get_json() or {}
        door_choice = data.get('door_choice')
        
        if not door_choice:
            return jsonify({
                'success': False,
                'error': 'door_choice is required',
                'in_dungeon': False
            }), 400
        
        result = dungeon_service.choose_door(door_choice)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'in_dungeon': False
        }), 500

@dungeon_bp.route('/state', methods=['GET'])
def get_dungeon_state():
    """
    Get current dungeon state
    Returns current location, doors, and party info
    """
    try:
        result = dungeon_service.get_dungeon_state()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'in_dungeon': False
        }), 500

@dungeon_bp.route('/status', methods=['GET'])
def get_dungeon_status():
    """
    Get quick dungeon status check
    Useful for UI to know if player is in dungeon
    """
    try:
        state_result = dungeon_service.get_dungeon_state()
        
        if state_result['success']:
            in_dungeon = state_result['in_dungeon']
            
            if in_dungeon:
                current_state = state_result['state']
                location_name = current_state.get('current_location', {}).get('name', 'Unknown Location')
                party_summary = current_state.get('party_summary', 'Unknown party')
                door_count = len(current_state.get('available_doors', []))
                
                return jsonify({
                    'success': True,
                    'in_dungeon': True,
                    'location_name': location_name,
                    'party_summary': party_summary,
                    'door_count': door_count,
                    'message': f'Currently in {location_name} with {party_summary}'
                })
            else:
                return jsonify({
                    'success': True,
                    'in_dungeon': False,
                    'message': 'Currently at home base'
                })
        else:
            return jsonify({
                'success': False,
                'error': state_result.get('error', 'Unknown error'),
                'in_dungeon': False
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'in_dungeon': False
        }), 500