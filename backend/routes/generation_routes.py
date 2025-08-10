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
        
        # Combine status info
        status = {
            'queue_info': {
                'worker_running': queue_status.get('worker_running', False),
                'queue_size': queue_status.get('queue_size', 0),
                'current_item': queue_status.get('current_item'),
                'total_items': queue_status.get('total_items', 0),
                'type_counts': queue_status.get('type_counts', {}),
                'status_counts': queue_status.get('status_counts', {})
            }
        }
        
        return jsonify({'success': True, 'data': status})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@generation_bp.route('/logs')
def get_logs():
    """Get generation logs - supports filtering by type, status, limit, offset, and sorting"""
    try:
        from backend.models.generation_log import GenerationLog
        from sqlalchemy import func

        # Parse query parameters
        limit_arg = request.args.get('limit')
        offset_arg = request.args.get('offset')
        generation_type = request.args.get('type')  # 'llm', 'image', or None
        status_filter = request.args.get('status')
        prompt_type = request.args.get('prompt_type')
        prompt_name = request.args.get('prompt_name')
        priority = request.args.get('priority')
        sort_by = request.args.get('sort_by')  # Comma-separated list of fields to sort by (e.g., 'generation_type,prompt_type')
        sort_order = request.args.get('sort_order', 'asc')  # 'asc' or 'desc'

        # Convert to ints if present
        limit = int(limit_arg) if limit_arg is not None else None
        offset = int(offset_arg) if offset_arg is not None else None

        # Hard safety cap
        HARD_MAX_LIMIT = 1000

        # Build query
        query = GenerationLog.query

        if generation_type:
            query = query.filter(GenerationLog.generation_type == generation_type)
        if status_filter:
            query = query.filter(GenerationLog.status == status_filter)
        if prompt_type:
            query = query.filter(GenerationLog.prompt_type == prompt_type)
        if prompt_name:
            query = query.filter(GenerationLog.prompt_name.ilike(f"%{prompt_name}%"))
        if priority:
            query = query.filter(GenerationLog.priority == int(priority))

        # Sorting
        if sort_by:
            sort_fields = sort_by.split(',')
            for field in sort_fields:
                if hasattr(GenerationLog, field):
                    column = getattr(GenerationLog, field)
                    if sort_order == 'asc':
                        query = query.order_by(column.asc())
                    else:
                        query = query.order_by(column.desc())

        # Apply offset and limit
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            limit = min(limit, HARD_MAX_LIMIT)
            query = query.limit(limit)
        elif offset is not None:
            # If only offset is provided, still cap the result set
            query = query.limit(HARD_MAX_LIMIT)

        logs = query.all()

        # Optional: Truncate promptText to reduce payload size
        def safe_to_dict(log):
            data = log.to_dict()
            if 'promptText' in data and data['promptText']:
                data['promptText'] = (data['promptText'][:200] + '...') if len(data['promptText']) > 200 else data['promptText']
            return data

        return jsonify({
            'success': True,
            'data': {
                'logs': [safe_to_dict(log) for log in logs],
                'count': len(logs),
                'filters': {
                    'type': generation_type,
                    'status': status_filter,
                    'limit': limit,
                    'offset': offset,
                    'prompt_type': prompt_type,
                    'prompt_name': prompt_name,
                    'priority': priority,
                    'sort_by': sort_by,
                    'sort_order': sort_order
                }
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
@generation_bp.route('/log-options', methods=['GET'])
def get_log_options():
    """Get available filter and sort options for generation logs, dynamically querying the database for prompt_type and prompt_name"""
    try:
        # Available filter options (static)
        filter_options = {
            'generation_type': ['llm', 'image', 'audio'],  # Can be extended if more types are added
            'status': ['pending', 'generating', 'completed', 'failed'],
            'priority': list(range(1, 11)),  # Priority 1-10 (could be adjusted if needed)
        }

        # Query the database for unique prompt_type and prompt_name
        from sqlalchemy import distinct
        from backend.models.generation_log import GenerationLog
        prompt_types = GenerationLog.query.with_entities(distinct(GenerationLog.prompt_type)).all()
        prompt_names = GenerationLog.query.with_entities(distinct(GenerationLog.prompt_name)).all()


        # Convert query results to lists
        prompt_types = [item[0] for item in prompt_types]
        prompt_names = [item[0] for item in prompt_names]

        # Available sort options
        sort_options = {
            'fields': [
                'generation_type',
                'prompt_type',
                'prompt_name',
                'priority',
                'duration_seconds',
                'start_time',
            ],
            'order': ['asc', 'desc']  # Sort order options: 'asc' or 'desc'
        }

        return jsonify({
            'success': True,
            'data': {
                'filters': {
                    **filter_options,
                    'prompt_type': prompt_types,
                    'prompt_name': prompt_names,
                },
                'sort': sort_options
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