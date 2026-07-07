# Settings Routes - SIMPLIFIED: Thin HTTP Layer Only
# Trust boundary established at service layer
# Routes only handle: HTTP parsing → Service call → HTTP response formatting

from flask import Blueprint, jsonify, request

from backend.services import settings_service

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')


@settings_bp.route('/llm', methods=['GET'])
def get_llm_settings():
    """Current LLM configuration (API key masked) - thin HTTP wrapper"""
    result = settings_service.get_llm_settings()
    return jsonify(result), 200 if result['success'] else 500


@settings_bp.route('/llm', methods=['PUT'])
def update_llm_settings():
    """Save LLM configuration from the settings panel - thin HTTP wrapper"""
    data = request.get_json() or {}

    result = settings_service.update_llm_settings(payload=data)

    return jsonify(result), 200 if result['success'] else 400


@settings_bp.route('/llm/fetch-models', methods=['POST'])
def fetch_deepseek_models():
    """Live DeepSeek model list (doubles as key validation) - thin HTTP wrapper"""
    data = request.get_json() or {}

    result = settings_service.fetch_deepseek_models(payload=data)

    return jsonify(result), 200 if result['success'] else 400


@settings_bp.route('/llm/test', methods=['POST'])
def test_llm_generation():
    """Fire a tiny generation through the normal gateway - thin HTTP wrapper"""
    result = settings_service.test_llm_generation()
    return jsonify(result), 200 if result['success'] else 400
