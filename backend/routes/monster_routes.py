# Monster Routes - ENHANCED WITH ADVANCED PAGINATION
# Now includes server-side filtering, sorting, and improved statistics
# Maintains thin route architecture - just delegates to services

from flask import Blueprint, jsonify, request
from backend.services import monster_service, ability_service

monster_bp = Blueprint('monsters', __name__, url_prefix='/api/monsters')

@monster_bp.route('/generate', methods=['POST'])
def generate_monster():
    """Generate monster - now automatically includes 2 abilities and card art"""
    data = request.get_json() or {}
    prompt_name = data.get('prompt_name', 'basic_monster')
    generate_card_art = data.get('generate_card_art', True)  # NEW: Optional card art
    
    result = monster_service.generate_monster(
        prompt_name=prompt_name,
        generate_card_art=generate_card_art
    )
    return jsonify(result)

@monster_bp.route('', methods=['GET'])
def get_monsters():
    """Get all monsters - ENHANCED with server-side filtering, sorting, and pagination"""
    
    # Parse query parameters with validation
    try:
        limit = min(int(request.args.get('limit', 50)), 1000)  # Max 1000 monsters per request
        offset = max(int(request.args.get('offset', 0)), 0)
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Invalid limit or offset parameter - must be integers'
        }), 400
    
    # Parse filtering options
    filter_type = request.args.get('filter', 'all')  # all, with_art, without_art
    if filter_type not in ['all', 'with_art', 'without_art']:
        return jsonify({
            'success': False,
            'error': 'Invalid filter parameter - must be: all, with_art, or without_art'
        }), 400
    
    # Parse sorting options  
    sort_by = request.args.get('sort', 'newest')  # newest, oldest, name, species
    if sort_by not in ['newest', 'oldest', 'name', 'species']:
        return jsonify({
            'success': False,
            'error': 'Invalid sort parameter - must be: newest, oldest, name, or species'
        }), 400
    
    # Call enhanced service method
    result = monster_service.get_all_monsters_enhanced(
        limit=limit,
        offset=offset,
        filter_type=filter_type,
        sort_by=sort_by
    )
    
    return jsonify(result)

@monster_bp.route('/<int:monster_id>')
def get_monster(monster_id):
    """Get one monster - now includes abilities and card art"""
    result = monster_service.get_monster_by_id(monster_id)
    return jsonify(result)

@monster_bp.route('/templates')
def get_templates():
    """Get templates - just delegate"""
    templates = monster_service.get_available_templates()
    return jsonify({'success': True, 'templates': templates})

@monster_bp.route('/stats')
def get_stats():
    """Get enhanced monster statistics with optional filtering"""
    
    # Parse optional filter parameter
    filter_type = request.args.get('filter', 'all')  # all, with_art, without_art
    if filter_type not in ['all', 'with_art', 'without_art']:
        return jsonify({
            'success': False,
            'error': 'Invalid filter parameter - must be: all, with_art, or without_art'
        }), 400
    
    result = monster_service.get_enhanced_monster_stats(filter_type=filter_type)
    return jsonify(result)

# 🔧 ABILITY ENDPOINTS (existing)

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

# 🔧 CARD ART ENDPOINTS (existing)

@monster_bp.route('/<int:monster_id>/card-art', methods=['POST'])
def generate_card_art_for_monster(monster_id):
    """
    Generate card art for an existing monster
    Useful for adding card art to monsters created before this feature
    """
    try:
        data = request.get_json() or {}
        wait_for_completion = data.get('wait_for_completion', True)
        
        result = monster_service.generate_card_art_for_existing_monster(
            monster_id=monster_id,
            wait_for_completion=wait_for_completion
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to generate card art: {str(e)}',
            'monster_id': monster_id
        }), 500

@monster_bp.route('/<int:monster_id>/card-art', methods=['GET'])
def get_monster_card_art_info(monster_id):
    """
    Get card art information for a specific monster
    Returns card art path and existence status
    """
    try:
        from backend.models.monster import Monster
        
        monster = Monster.get_monster_by_id(monster_id)
        if not monster:
            return jsonify({
                'success': False,
                'error': 'Monster not found',
                'monster_id': monster_id
            }), 404
        
        card_art_info = monster.get_card_art_info()
        
        return jsonify({
            'success': True,
            'monster_id': monster_id,
            'card_art': card_art_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get card art info: {str(e)}',
            'monster_id': monster_id
        }), 500

# 🔧 CARD ART FILE SERVING
@monster_bp.route('/card-art/<path:image_path>')
def serve_card_art(image_path):
    """
    Serve card art images
    Direct file serving from the API
    """
    try:
        from flask import send_from_directory
        from pathlib import Path
        
        # Build path to outputs folder
        outputs_dir = Path(__file__).parent.parent / 'ai' / 'comfyui' / 'outputs'
        
        # Validate that the path is safe (no directory traversal)
        if '..' in image_path or image_path.startswith('/'):
            return jsonify({
                'success': False,
                'error': 'Invalid image path'
            }), 400
        
        # Send the file
        return send_from_directory(outputs_dir, image_path)
        
    except FileNotFoundError:
        return jsonify({
            'success': False,
            'error': 'Image not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to serve image: {str(e)}'
        }), 500