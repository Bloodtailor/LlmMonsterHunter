# Monster Routes - ACTUALLY THIN
# Just button handlers, minimal validation

from flask import Blueprint, jsonify, request
from backend.services import monster_service

monster_bp = Blueprint('monsters', __name__, url_prefix='/api/monsters')

@monster_bp.route('/generate', methods=['POST'])
def generate_monster():
    """Generate monster - just delegate to service"""
    data = request.get_json() or {}
    prompt_name = data.get('prompt_name', 'basic_monster')
    
    result = monster_service.generate_monster(prompt_name)
    return jsonify(result)

@monster_bp.route('', methods=['GET'])
def get_monsters():
    """Get all monsters - just delegate"""
    result = monster_service.get_all_monsters()
    return jsonify(result)

@monster_bp.route('/<int:monster_id>')
def get_monster(monster_id):
    """Get one monster - just delegate"""
    result = monster_service.get_monster_by_id(monster_id)
    return jsonify(result)

@monster_bp.route('/templates')
def get_templates():
    """Get templates - just delegate"""
    templates = monster_service.get_available_templates()
    return jsonify({'success': True, 'templates': templates})

@monster_bp.route('/stats')
def get_stats():
    """Get stats - just delegate"""
    result = monster_service.get_monster_stats()
    return jsonify(result)