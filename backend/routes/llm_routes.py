# LLM Routes - THIN routes for LLM monitoring and debugging
# Just delegates to services, minimal validation

from flask import Blueprint, jsonify, request
from backend.services import llm_service

# Create blueprint for LLM routes
llm_bp = Blueprint('llm', __name__, url_prefix='/api/llm')

@llm_bp.route('/status')
def get_status():
    """Get LLM system status - thin route"""
    try:
        from backend.llm import get_llm_status
        from backend.llm.queue import get_llm_queue
        
        # Get basic LLM status
        llm_status = get_llm_status()
        
        # Get queue status
        queue = get_llm_queue()
        queue_status = queue.get_queue_status()
        
        # Combine status info
        status = {
            **llm_status,
            'queue_info': {
                'worker_running': queue_status.get('worker_running', False),
                'queue_size': queue_status.get('queue_size', 0),
                'current_generation': queue_status.get('current_item'),
                'total_processed': queue_status.get('total_items', 0)
            }
        }
        
        return jsonify({'success': True, 'data': status})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@llm_bp.route('/logs')
def get_logs():
    """Get LLM logs - thin route with basic filtering"""
    try:
        from backend.models.llm_log import LLMLog
        
        # Simple filtering
        limit = min(int(request.args.get('limit', 20)), 100)
        status_filter = request.args.get('status')
        
        # Build query
        query = LLMLog.query
        if status_filter:
            query = query.filter(LLMLog.status == status_filter)
        
        logs = query.order_by(LLMLog.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': {
                'logs': [log.to_dict() for log in logs],
                'count': len(logs)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@llm_bp.route('/logs/<int:log_id>')
def get_log_detail(log_id):
    """Get log detail - thin route"""
    try:
        from backend.models.llm_log import LLMLog
        
        log = LLMLog.query.get(log_id)
        if not log:
            return jsonify({'success': False, 'error': 'Log not found'}), 404
        
        return jsonify({'success': True, 'data': log.to_dict()})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@llm_bp.route('/stats')
def get_stats():
    """Get LLM stats - thin route"""
    try:
        from backend.models.llm_log import LLMLog
        
        # Simple stats
        total = LLMLog.query.count()
        completed = LLMLog.query.filter_by(status='completed').count()
        failed = LLMLog.query.filter_by(status='failed').count()
        
        stats = {
            'total_generations': total,
            'completed': completed,
            'failed': failed,
            'success_rate': round(completed / total * 100, 1) if total > 0 else 0
        }
        
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@llm_bp.route('/prompts')
def get_prompts():
    """Get available prompts - thin route"""
    try:
        from backend.llm.prompt_engine import get_prompt_engine
        
        engine = get_prompt_engine()
        prompts = {}
        
        for name in engine.list_templates():
            template = engine.get_template(name)
            if template:
                prompts[name] = template.description
        
        return jsonify({'success': True, 'data': {'prompts': prompts}})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@llm_bp.route('/test', methods=['POST'])
def test_inference():
    """Test LLM inference - thin route"""
    data = request.get_json() or {}
    prompt = data.get('prompt', 'Hello! Please respond with just the word "hi".')
    
    result = llm_service.inference_request(prompt, prompt_type='api_test', wait_for_completion=True)
    return jsonify(result)