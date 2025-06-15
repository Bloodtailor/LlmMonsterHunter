# Monster Routes - ENHANCED WITH ABILITIES ENDPOINTS
# Now includes ability generation and management endpoints
# Maintains thin route architecture - just delegates to services

from flask import Blueprint, jsonify, request
from backend.services import monster_service, ability_service

monster_bp = Blueprint('monsters', __name__, url_prefix='/api/monsters')

@monster_bp.route('/generate', methods=['POST'])
def generate_monster():
    """Generate monster - now automatically includes 2 abilities"""
    data = request.get_json() or {}
    prompt_name = data.get('prompt_name', 'basic_monster')
    
    result = monster_service.generate_monster(prompt_name)
    return jsonify(result)

@monster_bp.route('', methods=['GET'])
def get_monsters():
    """Get all monsters - now includes abilities in response"""
    result = monster_service.get_all_monsters()
    return jsonify(result)

@monster_bp.route('/<int:monster_id>')
def get_monster(monster_id):
    """Get one monster - now includes abilities"""
    result = monster_service.get_monster_by_id(monster_id)
    return jsonify(result)

@monster_bp.route('/templates')
def get_templates():
    """Get templates - just delegate"""
    templates = monster_service.get_available_templates()
    return jsonify({'success': True, 'templates': templates})

@monster_bp.route('/stats')
def get_stats():
    """Get stats - now includes ability statistics"""
    result = monster_service.get_monster_stats()
    return jsonify(result)

# 🔧 NEW ABILITY ENDPOINTS

@monster_bp.route('/<int:monster_id>/abilities', methods=['POST'])
def generate_ability_for_monster(monster_id):
    """
    Generate a new ability for an existing monster
    For developer testing - creates one new ability
    """
    try:
        # Optional: Get wait preference from request
        data = request.get_json() or {}
        wait_for_completion = data.get('wait_for_completion', True)
        
        result = ability_service.generate_ability(
            monster_id=monster_id,
            wait_for_completion=wait_for_completion
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate ability: {str(e)}',
            'monster_id': monster_id
        }), 500

@monster_bp.route('/<int:monster_id>/abilities', methods=['GET'])
def get_monster_abilities(monster_id):
    """
    Get all abilities for a specific monster
    Useful for detailed ability management
    """
    try:
        result = ability_service.get_abilities_for_monster(monster_id)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get abilities: {str(e)}',
            'monster_id': monster_id,
            'abilities': []
        }), 500