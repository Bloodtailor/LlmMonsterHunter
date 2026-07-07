# Chat Routes - SIMPLIFIED: Thin HTTP Layer Only
# Trust boundary established at service layer
# Routes only handle: HTTP parsing → Service call → HTTP response formatting

from flask import Blueprint, jsonify, request
from backend.services import chat_service

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route('/<int:monster_id>/message', methods=['POST'])
def send_message(monster_id):
    """Speak to a following monster at home base - thin HTTP wrapper"""
    data = request.get_json() or {}

    result = chat_service.send_message(
        monster_id=monster_id,
        message=data.get('message')
    )

    return jsonify(result), 200 if result['success'] else 400

@chat_bp.route('/<int:monster_id>/history', methods=['GET'])
def get_history(monster_id):
    """One page of a monster's chat thread - thin HTTP wrapper"""
    result = chat_service.get_history(
        monster_id=monster_id,
        limit=request.args.get('limit'),
        before_id=request.args.get('before_id')
    )

    return jsonify(result), 200 if result['success'] else 400
