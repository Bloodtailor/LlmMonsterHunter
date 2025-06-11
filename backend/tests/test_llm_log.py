#!/usr/bin/env python3
"""
Debug LLM Log Script
Inspects the raw database fields of LLM logs to see what's actually stored
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.getcwd())

from backend.app import create_app
from backend.models.llm_log import LLMLog

def inspect_recent_llm_logs(limit=5):
    """Inspect recent LLM logs and show all database fields"""
    
    app = create_app()
    with app.app_context():
        try:
            # Get recent logs
            logs = LLMLog.query.order_by(LLMLog.created_at.desc()).limit(limit).all()
            
            if not logs:
                print("❌ No LLM logs found in database")
                return
            
            print(f"🔍 Found {len(logs)} recent LLM log(s)")
            print("=" * 80)
            
            for i, log in enumerate(logs):
                print(f"\n📋 LOG {i+1} - ID: {log.id}")
                print("-" * 40)
                
                # Request Information
                print(f"📝 PROMPT INFO:")
                print(f"   prompt_type: {repr(log.prompt_type)}")
                print(f"   prompt_name: {repr(log.prompt_name)}")
                print(f"   prompt_text: {repr(log.prompt_text[:100] + '...' if log.prompt_text and len(log.prompt_text) > 100 else log.prompt_text)}")
                
                # Model Configuration
                print(f"\n🤖 MODEL CONFIG:")
                print(f"   model_name: {repr(log.model_name)}")
                print(f"   max_tokens: {log.max_tokens}")
                print(f"   temperature: {log.temperature}")
                
                # Response Data - THIS IS THE KEY SECTION
                print(f"\n🔥 RESPONSE DATA:")
                print(f"   response_text: {repr(log.response_text)}")
                print(f"   response_text (length): {len(log.response_text) if log.response_text else 'None'}")
                print(f"   response_text (type): {type(log.response_text)}")
                print(f"   response_tokens: {log.response_tokens}")
                
                # Timing Metrics
                print(f"\n⏱️  TIMING:")
                print(f"   start_time: {log.start_time}")
                print(f"   end_time: {log.end_time}")
                print(f"   duration_seconds: {log.duration_seconds}")
                
                # Parsing Results
                print(f"\n🔍 PARSING:")
                print(f"   parse_success: {log.parse_success}")
                print(f"   parsed_data: {repr(log.parsed_data)}")
                print(f"   parse_error: {repr(log.parse_error)}")
                print(f"   parser_used: {repr(log.parser_used)}")
                
                # Status and Error Handling
                print(f"\n📊 STATUS:")
                print(f"   status: {repr(log.status)}")
                print(f"   error_message: {repr(log.error_message)}")
                
                # Game Entity Associations
                print(f"\n🎮 GAME DATA:")
                print(f"   entity_type: {repr(log.entity_type)}")
                print(f"   entity_id: {log.entity_id}")
                
                # Standard Fields
                print(f"\n📅 METADATA:")
                print(f"   id: {log.id}")
                print(f"   created_at: {log.created_at}")
                print(f"   updated_at: {log.updated_at}")
                
                print("\n" + "=" * 80)
            
        except Exception as e:
            print(f"❌ Error inspecting logs: {e}")
            import traceback
            traceback.print_exc()

def inspect_specific_log(log_id):
    """Inspect a specific log by ID"""
    
    app = create_app()
    with app.app_context():
        try:
            log = LLMLog.query.get(log_id)
            
            if not log:
                print(f"❌ Log ID {log_id} not found")
                return
            
            print(f"🔍 DETAILED INSPECTION - LOG ID: {log_id}")
            print("=" * 80)
            
            # Show the response_text in detail
            print(f"🔥 CRITICAL: response_text field:")
            print(f"   Value: {repr(log.response_text)}")
            print(f"   Type: {type(log.response_text)}")
            print(f"   Length: {len(log.response_text) if log.response_text else 'None'}")
            print(f"   Is None: {log.response_text is None}")
            print(f"   Is Empty String: {log.response_text == ''}")
            
            if log.response_text:
                print(f"   First 500 chars: {repr(log.response_text[:500])}")
            
            print(f"\n📋 Generation status: {log.status}")
            print(f"📋 Parse status: {log.parse_success}")
            print(f"📋 Parse error: {repr(log.parse_error)}")
            
        except Exception as e:
            print(f"❌ Error inspecting specific log: {e}")
            import traceback
            traceback.print_exc()

def show_all_log_ids():
    """Show all available log IDs"""
    
    app = create_app()
    with app.app_context():
        try:
            logs = LLMLog.query.order_by(LLMLog.created_at.desc()).all()
            
            print(f"📋 All LLM Log IDs (newest first):")
            for log in logs:
                print(f"   ID: {log.id} | {log.created_at} | {log.prompt_name} | {log.status}")
            
        except Exception as e:
            print(f"❌ Error getting log IDs: {e}")

def main():
    """Main function with options"""
    
    print("🔍 LLM Log Database Inspector")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "ids":
            show_all_log_ids()
        elif sys.argv[1] == "specific" and len(sys.argv) > 2:
            log_id = int(sys.argv[2])
            inspect_specific_log(log_id)
        else:
            print("Usage:")
            print("  python debug_llm_log.py              # Show recent logs")
            print("  python debug_llm_log.py ids          # Show all log IDs")
            print("  python debug_llm_log.py specific 4   # Inspect specific log ID")
    else:
        inspect_recent_llm_logs()

if __name__ == "__main__":
    main()