# Monster Routes - SIMPLIFIED: Thin HTTP Layer Only
# Trust boundary established at service layer
# Routes only handle: HTTP parsing → Service call → HTTP response formatting

from flask import Blueprint, jsonify, request
from backend.services import monster_service, ability_service

monster_bp = Blueprint('monsters', __name__, url_prefix='/api/monsters')

@monster_bp.route('/generate', methods=['POST'])
def generate_monster():
    """Generate monster - thin HTTP wrapper"""
    data = request.get_json() or {}

    prompt_name = data.get('prompt_name', 'detailed_monster')
    
    result = monster_service.generate_monster(prompt_name)
    
    return jsonify(result), 200 if result['success'] else 500

@monster_bp.route('', methods=['GET'])
def get_monsters():
    """Get all monsters - thin HTTP wrapper with parameter extraction"""
    
    result = monster_service.get_all_monsters(
        limit=request.args.get('limit', 50, type=int),
        offset=request.args.get('offset', 0, type=int),
        filter_type=request.args.get('filter', 'all'),
        sort_by=request.args.get('sort', 'newest')
    )
    
    return jsonify(result), 200 if result['success'] else 400

@monster_bp.route('/<int:monster_id>')
def get_monster(monster_id):
    """Get one monster - thin HTTP wrapper"""
    result = monster_service.get_monster_by_id(monster_id)
    return jsonify(result), 200 if result['success'] else 404

@monster_bp.route('/templates')
def get_templates():
    """Get templates - thin HTTP wrapper"""
    result = monster_service.get_available_templates()
    return jsonify({'success': True, 'templates': result})

@monster_bp.route('/stats')
def get_stats():
    """Get monster statistics - thin HTTP wrapper"""
    result = monster_service.get_monster_stats(
        filter_type=request.args.get('filter', 'all')
    )
    return jsonify(result), 200 if result['success'] else 400

# Ability endpoints - thin HTTP wrappers
@monster_bp.route('/<int:monster_id>/abilities', methods=['POST'])
def generate_ability_for_monster(monster_id):
    """Generate ability - thin HTTP wrapper"""
    result = ability_service.generate_ability(monster_id=monster_id)
    return jsonify(result), 200 if result['success'] else 500

@monster_bp.route('/<int:monster_id>/abilities', methods=['GET'])
def get_monster_abilities(monster_id):
    """Get monster abilities - thin HTTP wrapper"""
    result = ability_service.get_abilities_for_monster(monster_id)
    return jsonify(result), 200 if result['success'] else 404

# Card art endpoints - thin HTTP wrappers
@monster_bp.route('/<int:monster_id>/card-art', methods=['POST'])
def generate_card_art_for_monster(monster_id):
    """Generate card art - thin HTTP wrapper"""
    result = monster_service.generate_card_art_for_existing_monster(monster_id=monster_id)
    return jsonify(result), 200 if result['success'] else 500

@monster_bp.route('/<int:monster_id>/card-art', methods=['GET'])
def get_monster_card_art_info(monster_id):
    """Get card art info - thin HTTP wrapper"""
    result = monster_service.get_monster_card_art_info(monster_id)
    return jsonify(result), 200 if result['success'] else 404

@monster_bp.route('/card-art/<path:image_path>')
def serve_card_art(image_path):
    """Serve card art images - direct file serving"""
    try:
        from flask import send_from_directory
        from pathlib import Path
        
        # Simple security check
        if '..' in image_path or image_path.startswith('/'):
            return jsonify({'success': False, 'error': 'Invalid image path'}), 400
        
        # Build path and serve
        outputs_dir = Path(__file__).parent.parent / 'ai' / 'comfyui' / 'outputs'
        return send_from_directory(outputs_dir, image_path)
        
    except FileNotFoundError:
        return jsonify({'success': False, 'error': 'Image not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': f'Failed to serve image: {str(e)}'}), 500