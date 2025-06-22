# Services Package - Business Logic Layer
# Clean exports with event-driven architecture and abilities support

from . import game_tester_service
from . import llm_service
from . import monster_service
from . import ability_service  # 🔧 NEW: Ability service
from . import comfyui_service  # 🔧 NEW: ComfyUI image generation service
from . import event_service
from . import sse_service

# Simple re-exports
from .game_tester_service import get_test_files, run_test_file
from .llm_service import inference_request
from .monster_service import generate_monster, get_all_monsters, get_monster_by_id
from .ability_service import generate_ability, generate_initial_abilities, get_abilities_for_monster  # 🔧 NEW
from .comfyui_service import generate_monster_image, is_comfyui_available, get_comfyui_status  # 🔧 NEW

# Event system exports
from .event_service import get_event_service, emit_event, subscribe_to_event
from .sse_service import get_sse_service