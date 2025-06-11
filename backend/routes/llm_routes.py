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
        
        # 🔧 NEW: Add queue information to status
        from backend.llm.queue import get_llm_queue
        queue = get_llm_queue()
        queue_status = queue.get_queue_status()
        
        # Merge LLM status with queue status
        enhanced_status = {
            **status,
            'queue_info': {
                'worker_running': queue_status.get('worker_running', False),
                'queue_size': queue_status.get('queue_size', 0),
                'current_generation': queue_status.get('current_item'),
                'total_processed': queue_status.get('total_items', 0)
            }
        }
        
        return jsonify({
            'success': True,
            'data': enhanced_status
        })
    except Exception as e:
        print(f"❌ Error getting LLM status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@llm_bp.route('/logs', methods=['GET'])
def get_logs():
    """
    🔧 ENHANCED: Get recent LLM logs for debugging and monitoring
    
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
        
        print(f"📋 Fetching LLM logs: limit={limit}, status={status_filter}, type={prompt_type_filter}")
        
        # Build query
        query = LLMLog.query
        
        if status_filter:
            query = query.filter(LLMLog.status == status_filter)
        
        if prompt_type_filter:
            query = query.filter(LLMLog.prompt_type == prompt_type_filter)
        
        # Execute query
        logs = query.order_by(LLMLog.created_at.desc()).limit(limit).all()
        
        print(f"📋 Found {len(logs)} LLM logs")
        
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
                },
                'total_in_db': LLMLog.query.count()  # 🔧 NEW: Total count for debugging
            }
        })
        
    except Exception as e:
        print(f"❌ Error fetching LLM logs: {e}")
        import traceback
        traceback.print_exc()
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
        print(f"❌ Error fetching log detail: {e}")
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
        
        # 🔧 NEW: Add recent activity stats
        from datetime import datetime, timedelta
        recent_cutoff = datetime.utcnow() - timedelta(hours=1)  # Last hour
        
        recent_logs = LLMLog.query.filter(LLMLog.created_at >= recent_cutoff).all()
        recent_stats = {
            'last_hour_total': len(recent_logs),
            'last_hour_completed': len([log for log in recent_logs if log.status == 'completed']),
            'last_hour_failed': len([log for log in recent_logs if log.status == 'failed'])
        }
        
        enhanced_stats = {
            **stats,
            'recent_activity': recent_stats,
            'database_health': {
                'total_logs': LLMLog.query.count(),
                'oldest_log': LLMLog.query.order_by(LLMLog.created_at.asc()).first().created_at.isoformat() if LLMLog.query.first() else None,
                'newest_log': LLMLog.query.order_by(LLMLog.created_at.desc()).first().created_at.isoformat() if LLMLog.query.first() else None
            }
        }
        
        return jsonify({
            'success': True,
            'data': enhanced_stats
        })
        
    except Exception as e:
        print(f"❌ Error getting LLM stats: {e}")
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
        # Check queue for current generation
        from backend.llm.queue import get_llm_queue
        queue = get_llm_queue()
        queue_status = queue.get_queue_status()
        
        current_item = queue_status.get('current_item')
        
        # Also check for active log entry
        current_log = LLMLog.get_current_generation()
        
        data = {
            'queue_item': current_item,
            'log_entry': current_log.to_dict() if current_log else None,
            'queue_status': queue_status
        }
        
        return jsonify({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        print(f"❌ Error getting current generation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 🔧 NEW: Debug endpoint to test log creation
@llm_bp.route('/debug/create-test-log', methods=['POST'])
def create_test_log():
    """Create a test log entry for debugging"""
    try:
        log = LLMLog.create_log(
            prompt_type='debug_test',
            prompt_name='test_log_creation',
            prompt_text='This is a test log entry created for debugging purposes.',
            max_tokens=50,
            temperature=0.8
        )
        
        if log.save():
            return jsonify({
                'success': True,
                'message': 'Test log created successfully',
                'log_id': log.id,
                'log_data': log.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save test log'
            }), 500
            
    except Exception as e:
        print(f"❌ Error creating test log: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 🔧 NEW: Debug endpoint to check database connection
@llm_bp.route('/debug/db-test', methods=['GET'])
def test_database():
    """Test database connection and LLM log table"""
    try:
        from backend.config.database import db
        
        # Test basic query
        total_logs = LLMLog.query.count()
        
        # Test recent logs
        recent_logs = LLMLog.query.order_by(LLMLog.created_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'data': {
                'database_connected': True,
                'total_logs': total_logs,
                'recent_logs_count': len(recent_logs),
                'recent_logs': [log.to_dict() for log in recent_logs],
                'table_exists': True
            }
        })
        
    except Exception as e:
        print(f"❌ Database test error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'database_connected': False
        }), 500