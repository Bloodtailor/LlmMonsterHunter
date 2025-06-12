# Monster Routes - API endpoints for monster generation and management
# 🔧 SIMPLIFIED: All generation goes through queue system only
# Single entry point, comprehensive logging, real-time streaming

from flask import Blueprint, jsonify, request
from backend.models.monster import Monster
from backend.models.llm_log import LLMLog
from backend.llm.monster_generation import generate_monster, get_available_prompts

# Create blueprint for monster routes
monster_bp = Blueprint('monsters', __name__, url_prefix='/api/monsters')

@monster_bp.route('/generate', methods=['POST'])
def generate_new_monster():
    """
    🔧 SIMPLIFIED: Generate a new monster using queue system ONLY
    All requests are queued, logged, and streamed automatically
    
    POST Body (JSON):
        prompt_name (str, optional): Prompt to use ('basic_monster', 'detailed_monster', 'story_driven_monster')
        priority (int, optional): Queue priority (1=highest, 10=lowest, default=3)
    
    Returns:
        JSON with generation results
    """
    try:
        # Get request data
        data = request.get_json() or {}
        prompt_name = data.get('prompt_name', 'basic_monster')
        priority = data.get('priority', 3)  # High priority for UI requests
        
        print(f"🎲 Monster generation requested: {prompt_name} (priority: {priority})")
        
        # 🔧 CRITICAL: Use ONLY the queue system - no direct generation
        result = generate_monster(
            prompt_name=prompt_name,
            use_queue=True  # ALWAYS use queue
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Monster generated successfully!',
                'monster': result['monster'],
                'request_id': result.get('request_id'),
                'log_id': result['log_id'],
                'generation_stats': result.get('generation_stats', {}),
                'prompt_used': prompt_name
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'request_id': result.get('request_id'),
                'log_id': result.get('log_id'),
                'raw_response': result.get('raw_response'),  # For debugging
                'prompt_used': prompt_name
            }), 500
            
    except Exception as e:
        print(f"❌ Monster generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@monster_bp.route('/generate-async', methods=['POST'])
def generate_monster_async():
    """
    🔧 NEW: Start monster generation and return immediately
    Use this for long generations where you want to show streaming progress
    
    POST Body (JSON):
        prompt_name (str, optional): Prompt to use
        priority (int, optional): Queue priority
    
    Returns:
        JSON with request_id to track progress via streaming
    """
    try:
        from backend.llm.queue import get_llm_queue
        from backend.llm.monster_generation import load_prompts
        
        # Get request data  
        data = request.get_json() or {}
        prompt_name = data.get('prompt_name', 'basic_monster')
        priority = data.get('priority', 3)
        
        # Load prompt configuration
        prompts = load_prompts()
        if prompt_name not in prompts:
            return jsonify({
                'success': False,
                'error': f'Unknown prompt: {prompt_name}'
            }), 400
        
        prompt_config = prompts[prompt_name]
        
        # Create LLM log entry
        log = LLMLog.create_log(
            prompt_type='monster_generation_async',
            prompt_name=prompt_name,
            prompt_text=prompt_config['prompt_template'],
            max_tokens=prompt_config['max_tokens'],
            temperature=prompt_config['temperature']
        )
        
        if not log.save():
            return jsonify({
                'success': False,
                'error': 'Could not create log entry'
            }), 500
        
        # Add to queue
        queue = get_llm_queue()
        request_id = queue.add_request(
            prompt=prompt_config['prompt_template'],
            max_tokens=prompt_config['max_tokens'],
            temperature=prompt_config['temperature'],
            prompt_type=f'monster_generation_{prompt_name}',
            priority=priority,
            log_id=log.id
        )
        
        # Associate log with queue request
        log.entity_type = 'async_generation'
        log.entity_id = request_id
        log.save()
        
        return jsonify({
            'success': True,
            'message': 'Monster generation started',
            'request_id': request_id,
            'log_id': log.id,
            'prompt_used': prompt_name,
            'queue_position': queue.get_queue_status()['queue_size'],
            'streaming_instructions': 'Connect to /api/streaming/llm-events to watch progress'
        })
        
    except Exception as e:
        print(f"❌ Async monster generation error: {e}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@monster_bp.route('', methods=['GET'])
def get_all_monsters():
    """
    Get all monsters from database
    
    Query Parameters:
        limit (int): Number of monsters to return (default: 50)
        offset (int): Offset for pagination (default: 0)
    
    Returns:
        JSON with list of monsters
    """
    try:
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100
        offset = int(request.args.get('offset', 0))
        
        # Get monsters with pagination
        monsters = Monster.query.order_by(Monster.created_at.desc()).offset(offset).limit(limit).all()
        total_count = Monster.query.count()
        
        return jsonify({
            'success': True,
            'data': {
                'monsters': [monster.to_dict() for monster in monsters],
                'count': len(monsters),
                'total': total_count,
                'pagination': {
                    'limit': limit,
                    'offset': offset,
                    'has_more': offset + len(monsters) < total_count
                }
            }
        })
        
    except Exception as e:
        print(f"❌ Error fetching monsters: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monster_bp.route('/<int:monster_id>', methods=['GET'])
def get_monster_by_id(monster_id):
    """
    Get specific monster by ID
    
    Returns:
        JSON with monster details
    """
    try:
        monster = Monster.query.get(monster_id)
        
        if not monster:
            return jsonify({
                'success': False,
                'error': 'Monster not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': monster.to_dict()
        })
        
    except Exception as e:
        print(f"❌ Error fetching monster {monster_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monster_bp.route('/prompts', methods=['GET'])
def get_generation_prompts():
    """
    Get available monster generation prompts
    
    Returns:
        JSON with available prompts and descriptions
    """
    try:
        prompts = get_available_prompts()
        
        return jsonify({
            'success': True,
            'data': {
                'prompts': prompts,
                'count': len(prompts),
                'recommended': 'basic_monster'  # Default recommendation
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monster_bp.route('/stats', methods=['GET'])
def get_monster_stats():
    """
    Get monster generation statistics
    
    Returns:
        JSON with generation and database statistics
    """
    try:
        # Database stats
        total_monsters = Monster.query.count()
        
        # Recent generation stats (link to LLM logs)
        from datetime import datetime, timedelta
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_logs = LLMLog.query.filter(
            LLMLog.prompt_type.like('monster_generation%'),
            LLMLog.created_at >= recent_cutoff
        ).all()
        
        recent_stats = {
            'last_24h_attempts': len(recent_logs),
            'last_24h_successful': len([log for log in recent_logs if log.status == 'completed' and log.parse_success]),
            'last_24h_failed': len([log for log in recent_logs if log.status == 'failed' or not log.parse_success])
        }
        
        return jsonify({
            'success': True,
            'data': {
                'database': {
                    'total_monsters': total_monsters,
                    'newest_monster': Monster.query.order_by(Monster.created_at.desc()).first().to_dict() if total_monsters > 0 else None
                },
                'generation': recent_stats,
                'prompts_available': len(get_available_prompts())
            }
        })
        
    except Exception as e:
        print(f"❌ Error getting monster stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 🔧 DEBUG: Test endpoint for quick monster generation
@monster_bp.route('/debug/quick-generate', methods=['POST'])
def debug_quick_generate():
    """Debug endpoint for quick monster generation testing"""
    try:
        data = request.get_json() or {}
        prompt_name = data.get('prompt_name', 'basic_monster')
        
        print(f"🧪 Debug: Quick monster generation with {prompt_name}")
        
        result = generate_monster(prompt_name=prompt_name, use_queue=True)
        
        return jsonify({
            'success': result['success'],
            'debug_info': {
                'prompt_used': prompt_name,
                'queue_used': True,
                'log_id': result.get('log_id'),
                'request_id': result.get('request_id'),
                'generation_time': result.get('generation_stats', {}).get('duration'),
                'tokens': result.get('generation_stats', {}).get('tokens')
            },
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'debug_info': {'error_type': type(e).__name__}
        }), 500