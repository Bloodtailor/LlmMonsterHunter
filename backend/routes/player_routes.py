# Player Routes - SIMPLIFIED: Thin HTTP Layer Only
# Trust boundary established at service layer
# Routes only handle: HTTP parsing → Service call → HTTP response formatting

from flask import Blueprint, jsonify, request

from backend.services import player_service

player_bp = Blueprint('player', __name__, url_prefix='/api/player')


@player_bp.route('', methods=['GET'])
def get_player():
    """Get the player character - thin HTTP wrapper"""
    result = player_service.get_player()
    return jsonify(result), 200 if result['success'] else 404


@player_bp.route('/options', methods=['POST'])
def generate_options():
    """Queue option generation for one creation field - thin HTTP wrapper"""
    data = request.get_json(silent=True) or {}
    result = player_service.generate_options(
        field=data.get('field'), choices=data.get('choices') or {}
    )
    return jsonify(result), 200 if result['success'] else 400


@player_bp.route('/create', methods=['POST'])
def create_character():
    """Queue the character finalize workflow - thin HTTP wrapper"""
    data = request.get_json(silent=True) or {}
    result = player_service.create_character(data)
    return jsonify(result), 200 if result['success'] else 400


@player_bp.route('/portrait/generate', methods=['POST'])
def generate_portrait():
    """Queue one portrait candidate paint - thin HTTP wrapper"""
    data = request.get_json(silent=True) or {}
    result = player_service.generate_portrait(description=data.get('description'))
    return jsonify(result), 200 if result['success'] else 400


@player_bp.route('/portrait/select', methods=['POST'])
def select_portrait():
    """Make a candidate the portrait - thin HTTP wrapper"""
    data = request.get_json(silent=True) or {}
    result = player_service.select_portrait(image_path=data.get('image_path'))
    return jsonify(result), 200 if result['success'] else 400


@player_bp.route('/portrait/upload', methods=['POST'])
def upload_portrait():
    """Store an uploaded portrait image - thin HTTP wrapper (multipart)"""
    uploaded = request.files.get('image')
    if uploaded is None:
        return jsonify({'success': False, 'error': "An 'image' file field is required"}), 400

    result = player_service.upload_portrait(
        filename=uploaded.filename or '', data=uploaded.read()
    )
    return jsonify(result), 200 if result['success'] else 400
