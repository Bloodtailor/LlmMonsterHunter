# Battle Routes - SIMPLIFIED: Thin HTTP Layer Only
# Trust boundary established at service layer
# Routes only handle: HTTP parsing → Service call → HTTP response formatting

from flask import Blueprint, jsonify, request

from backend.services import battle_service

battle_bp = Blueprint('battle', __name__, url_prefix='/api/battle')


@battle_bp.route('/turn', methods=['POST'])
def take_turn():
    """Take a battle turn (or run opening initiative) - thin HTTP wrapper"""
    data = request.get_json() or {}

    result = battle_service.take_turn(action=data.get('action'))

    return jsonify(result), 200 if result['success'] else 400


@battle_bp.route('/respond', methods=['POST'])
def respond_to_talk():
    """Reply to an enemy's battlefield talk - thin HTTP wrapper"""
    data = request.get_json() or {}

    result = battle_service.respond_to_talk(response=data.get('response'))

    return jsonify(result), 200 if result['success'] else 400


@battle_bp.route('/state', methods=['GET'])
def get_battle_state():
    """Get public battle state - thin HTTP wrapper"""
    result = battle_service.get_battle_state()
    return jsonify(result), 200 if result['success'] else 400
