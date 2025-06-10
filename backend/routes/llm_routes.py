# LLM Routes - API endpoints for LLM monitoring and debugging
# Provides access to LLM logs, status, and generation history

from flask import Blueprint, jsonify, request
from backend.models.llm_log import LLMLog
from backend.llm import get_llm_status, get_available_prompts

# Create blueprint for LLM routes
llm_bp = Blueprint('llm', __name__, url_prefix='/api/llm')

@llm_bp.route('/status', methods=['GET'])
def get_status():
    """
    Get current LLM status including model state and generation info
    
    Returns:
        JSON with model loaded status, current generation, etc.
    """
    try:
        status = get_llm_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/logs', methods=['GET'])
def get_logs():
    """
    Get recent LLM logs for debugging and monitoring
    
    Query parameters:
        limit (int): Number of logs to return (default: 50, max: 200)
        status (str): Filter by status ('pending', 'generating', 'completed', 'failed')
        prompt_type (str): Filter by prompt type ('monster_generation', etc.)
    
    Returns:
        JSON with list of LLM logs
    """
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 50)), 200)  # Max 200 logs
        status_filter = request.args.get('status')
        prompt_type_filter = request.args.get('prompt_type')
        
        # Build query
        query = LLMLog.query
        
        if status_filter:
            query = query.filter(LLMLog.status == status_filter)
        
        if prompt_type_filter:
            query = query.filter(LLMLog.prompt_type == prompt_type_filter)
        
        # Execute query
        logs = query.order_by(LLMLog.created_at.desc()).limit(limit).all()
        
        # Convert to JSON
        logs_data = [log.to_dict() for log in logs]
        
        return jsonify({
            'success': True,
            'data': {
                'logs': logs_data,
                'count': len(logs_data),
                'filters': {
                    'limit': limit,
                    'status': status_filter,
                    'prompt_type': prompt_type_filter
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/logs/<int:log_id>', methods=['GET'])
def get_log_detail(log_id):
    """
    Get detailed information about a specific LLM log
    
    Args:
        log_id (int): ID of the log to retrieve
    
    Returns:
        JSON with detailed log information including full prompt and response
    """
    try:
        log = LLMLog.query.get(log_id)
        
        if not log:
            return jsonify({
                'success': False,
                'error': 'Log not found'
            }), 404
        
        # Get detailed data including full text
        log_data = log.to_dict()
        
        return jsonify({
            'success': True,
            'data': log_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Get LLM generation statistics
    
    Returns:
        JSON with generation statistics and performance metrics
    """
    try:
        stats = LLMLog.get_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/prompts', methods=['GET'])
def get_prompts():
    """
    Get available prompts for LLM generation
    
    Returns:
        JSON with available prompt types and descriptions
    """
    try:
        prompts = get_available_prompts()
        
        return jsonify({
            'success': True,
            'data': {
                'prompts': prompts,
                'count': len(prompts)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/current-generation', methods=['GET'])
def get_current_generation():
    """
    Get information about the currently running generation, if any
    
    Returns:
        JSON with current generation info or null if none active
    """
    try:
        current_log = LLMLog.get_current_generation()
        
        if current_log:
            data = current_log.to_dict()
        else:
            data = None
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500