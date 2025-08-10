# Generation Routes - UNIFIED FOR ALL GENERATION TYPES
# Replaces llm_routes.py with support for both LLM and image generation
# Thin routes for generation monitoring and debugging
print(f"🔍 Loading {__file__}")
from flask import Blueprint, jsonify, request

# Create blueprint for generation routes
generation_bp = Blueprint('generation', __name__, url_prefix='/api/generation')

@generation_bp.route('/logs')
def get_logs():
    """Get generation logs - supports filtering by type, status, limit, offset, and sorting"""
    try:
        from backend.models.generation_log import GenerationLog
        from sqlalchemy import func

        # Parse query parameters
        limit_arg = request.args.get('limit')
        offset_arg = request.args.get('offset')
        generation_type = request.args.get('generation_type')  # 'llm', 'image', or None
        status_filter = request.args.get('status')
        prompt_type = request.args.get('prompt_type')
        prompt_name = request.args.get('prompt_name')
        priority = request.args.get('priority')
        sort_by = request.args.get('sort_by', 'id')  # Default to 'id' 
        sort_order = request.args.get('sort_order', 'desc')  # Default to 'desc'

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

        # Sorting - handle both single field and comma-separated fields
        if sort_by:
            sort_fields = sort_by.split(',')
            for field in sort_fields:
                field = field.strip()  # Remove any whitespace
                if hasattr(GenerationLog, field):
                    column = getattr(GenerationLog, field)
                    if sort_order == 'asc':
                        query = query.order_by(column.asc())
                    else:
                        query = query.order_by(column.desc())

        # Get total count before applying limit/offset for pagination
        total_count = query.count()

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
                'count': total_count,  # Total count for pagination
                'returned_count': len(logs),  # Actual returned count
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
            'generation_type': ['llm', 'image'],  # Can be extended if more types are added
            'status': ['pending', 'generating', 'completed', 'failed'],
            'priority': list(range(1, 11)),  # Priority 1-10 (could be adjusted if needed)
        }

        # Query the database for unique prompt_type and prompt_name
        from sqlalchemy import distinct
        from backend.models.generation_log import GenerationLog
        prompt_types = GenerationLog.query.with_entities(distinct(GenerationLog.prompt_type)).all()
        prompt_names = GenerationLog.query.with_entities(distinct(GenerationLog.prompt_name)).all()

        # Convert query results to lists and filter out None values
        prompt_types = [item[0] for item in prompt_types if item[0] is not None]
        prompt_names = [item[0] for item in prompt_names if item[0] is not None]

        # Available sort options - UPDATED to include 'id' and better field names
        sort_options = {
            'fields': [
                'id',                # ADDED: Sort by ID
                'generation_type',
                'prompt_type', 
                'prompt_name',
                'status',           # ADDED: Sort by status
                'priority',
                'duration_seconds',
                'start_time',
            ],
            'orders': ['asc', 'desc']  # Changed from 'order' to 'orders' for clarity
        }

        return jsonify({
            'success': True,
            'data': {
                'filter_options': {
                    **filter_options,
                    'prompt_type': prompt_types,
                    'prompt_name': prompt_names,
                },
                'sort_options': sort_options
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500