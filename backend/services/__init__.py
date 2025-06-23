# Services Package - Business Logic Layer
# Updated with unified generation service and abilities support

from . import game_tester_service
from . import generation_service  # 🔧 RENAMED: was llm_service
from . import monster_service
from . import ability_service
from . import event_service
from . import sse_service

# Simple re-exports with new generation service
from .game_tester_service import get_test_files, run_test_file
from .generation_service import text_generation_request, image_generation_request, generate_monster_image, inference_request  # 🔧 NEW: unified generation
from .monster_service import generate_monster, get_all_monsters, get_monster_by_id
from .ability_service import generate_ability, generate_initial_abilities, get_abilities_for_monster

# Event system exports
from .event_service import get_event_service, emit_event, subscribe_to_event
from .sse_service import get_sse_service

# 🔧 REMOVED: comfyui_service (functionality moved to generation_service)