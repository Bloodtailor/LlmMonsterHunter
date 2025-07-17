# Generation Routes - UNIFIED FOR ALL GENERATION TYPES
# Replaces llm_routes.py with support for both LLM and image generation
# Thin routes for generation monitoring and debugging
print(f"🔍 Loading {__file__}")
from flask import Blueprint, jsonify, request

# Create blueprint for generation routes
generation_bp = Blueprint('generation', __name__, url_prefix='/api/generation')

@generation_bp.route('/status')
def get_status():
    """Get unified generation system status"""
    try:
        from backend.ai.queue import get_ai_queue
        
        # Get unified queue status
        queue = get_ai_queue()
        queue_status = queue.get_queue_status()
        
        # Get model status
        from backend.ai.llm import get_llm_status
        llm_status = get_llm_status()
        
        # Get image generation status
        import os
        image_enabled = os.getenv('ENABLE_IMAGE_GENERATION', 'false').lower() == 'true'
        image_status = {'enabled': image_enabled}
        
        if image_enabled:
            try:
                from backend.ai.comfyui.client import ComfyUIClient
                client = ComfyUIClient()
                image_status['server_running'] = client.is_server_running()
                image_status['available'] = client.is_server_running()
            except Exception as e:
                image_status['error'] = str(e)
                image_status['available'] = False
        else:
            image_status['available'] = False
        
        # Combine status info
        status = {
            'llm_status': llm_status,
            'image_status': image_status,
            'queue_info': {
                'worker_running': queue_status.get('worker_running', False),
                'queue_size': queue_status.get('queue_size', 0),
                'current_item': queue_status.get('current_item'),
                'total_items': queue_status.get('total_items', 0),
                'type_counts': queue_status.get('type_counts', {}),
                'status_counts': queue_status.get('status_counts', {})
            },
            'generation_types_supported': ['llm'] + (['image'] if image_status['available'] else [])
        }
        
        return jsonify({'success': True, 'data': status})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@generation_bp.route('/logs')
def get_logs():
    """Get generation logs - supports filtering by type"""
    try:
        from backend.models.generation_log import GenerationLog
        
        # Simple filtering
        limit = min(int(request.args.get('limit', 20)), 100)
        generation_type = request.args.get('type')  # 'llm', 'image', or None for all
        status_filter = request.args.get('status')
        
        # Build query
        query = GenerationLog.query
        if generation_type:
            query = query.filter(GenerationLog.generation_type == generation_type)
        if status_filter:
            query = query.filter(GenerationLog.status == status_filter)
        
        logs = query.order_by(GenerationLog.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': {
                'logs': [log.to_dict() for log in logs],
                'count': len(logs),
                'filters': {
                    'type': generation_type,
                    'status': status_filter,
                    'limit': limit
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@generation_bp.route('/logs/<int:generation_id>')
def get_log_detail(generation_id):
    """Get generation log detail with child data"""
    try:
        from backend.models.generation_log import GenerationLog
        
        log = GenerationLog.query.get(generation_id)
        if not log:
            return jsonify({'success': False, 'error': 'Generation log not found'}), 404
        
        return jsonify({'success': True, 'data': log.to_dict()})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@generation_bp.route('/stats')
def get_stats():
    """Get comprehensive generation statistics"""
    try:
        from backend.models.generation_log import GenerationLog
        
        # Overall stats
        overall_stats = GenerationLog.get_stats()
        
        # LLM-specific stats
        try:
            from backend.models.llm_log import LLMLog
            llm_stats = LLMLog.get_parsing_stats()
        except Exception as e:
            llm_stats = {'error': str(e)}
        
        # Image-specific stats
        try:
            from backend.models.image_log import ImageLog
            image_stats = ImageLog.get_stats()
        except Exception as e:
            image_stats = {'error': str(e)}
        
        stats = {
            'overall': overall_stats,
            'llm': llm_stats,
            'image': image_stats
        }
        
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@generation_bp.route('/prompts')
def get_prompts():
    """Get available prompts for both LLM and image generation"""
    try:
        from backend.ai.llm.prompt_engine import get_prompt_engine
        
        engine = get_prompt_engine()
        prompts = {}
        
        for name in engine.list_templates():
            template = engine.get_template(name)
            if template:
                prompts[name] = {
                    'description': template.description,
                    'category': template.category,
                    'generation_type': 'llm'  # All current templates are LLM
                }
        
        # Add image generation workflows
        try:
            from backend.ai.comfyui.workflow import get_workflow_manager
            workflow_manager = get_workflow_manager()
            workflows = workflow_manager.list_available_workflows()
            
            for workflow_name in workflows:
                prompts[f"image_{workflow_name}"] = {
                    'description': f'Image generation workflow: {workflow_name}',
                    'category': 'image_generation',
                    'generation_type': 'image'
                }
        except Exception as e:
            print(f"⚠️ Could not load image workflows: {e}")
        
        return jsonify({'success': True, 'data': {'prompts': prompts}})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500