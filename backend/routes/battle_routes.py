# Battle Routes - SIMPLIFIED: Thin HTTP Layer Only
# Trust boundary established at service layer
# Routes only handle: HTTP parsing → Service call → HTTP response formatting

from flask import Blueprint, jsonify, request
from backend.services import battle_service

battle_bp = Blueprint('battle', __name__, url_prefix='/api/battle')

@battle_bp.route('/round', methods=['POST'])
def submit_round():
    """Submit player actions for the round - thin HTTP wrapper"""
    data = request.get_json() or {}

    result = battle_service.submit_round(
        actions=data.get('actions')
    )

    return jsonify(result), 200 if result['success'] else 400

@battle_bp.route('/state', methods=['GET'])
def get_battle_state():
    """Get public battle state - thin HTTP wrapper"""
    result = battle_service.get_battle_state()
    return jsonify(result), 200 if result['success'] else 400
