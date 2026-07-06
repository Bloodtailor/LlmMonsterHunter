print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from backend.core.workflow_registry import register_workflow
from backend.core.utils.responses import success_response, error_response
from backend.core.utils.validation import require_keys
from typing import Callable, Dict, Any

@register_workflow()
def enter_dungeon(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """Enter the dungeon: entry text, starting location, and first paths"""

    workflow_name = 'enter_dungeon'
    # "context" should have the following keys:
    required_keys = []

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon.generator import generate_random_location, generate_paths, generate_entry_text
        from backend.game.dungeon import manager

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        # Step 1
        step = "queue_entry_text"
        on_update(step, progress_data)
        entry_text_generation_id = generate_entry_text(workflow_name)
        progress_data.update({ "entry_text_generation_id": entry_text_generation_id })

        # Step 2
        step = "emit_generation_id"
        on_update(step, progress_data)

        # Step 3
        step = "generate_starting_location"
        on_update(step, progress_data)
        location = generate_random_location(workflow_name)
        progress_data.update({ "current_location": location })

        # Step 4 - generate paths (hidden events assigned inside, never emitted)
        step = "generate_paths"
        on_update(step, progress_data)
        paths = generate_paths(location, workflow_name)

        # Step 5 - persist the dungeon run, party starts the run fresh
        step = "save_dungeon_state"
        on_update(step, progress_data)
        manager.start_dungeon(location, paths)

        from backend.game.state.manager import get_party_monster_ids
        manager.set_party_conditions({
            str(monster_id): 'fresh' for monster_id in get_party_monster_ids()
        })

        return success_response({
            "current_location": location,
            "paths": manager.get_public_paths()
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

@register_workflow()
def choose_path(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """
    Take a chosen path: generate the arrival location, then play out the
    path's hidden event (or exit the dungeon)
    """

    workflow_name = 'choose_path'
    # "context" should have the following keys:
    required_keys = ["path_id"]

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon.generator import (
            generate_arrival_location,
            generate_encounter_vanity_text,
            generate_exit_text
        )
        from backend.game.dungeon import manager
        from backend.game.monster.generator import generate_contextual_monster, generate_ability, generate_card_art
        from backend.game.state.manager import get_party_summary, get_party_details
        from backend.game.utils import build_and_generate

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        # Look up the chosen path WITH its hidden event (backend only)
        path = manager.get_path(context["path_id"])
        if not path:
            raise Exception(f"Unknown path: {context['path_id']}")

        previous_location = manager.get_current_location()

        # === EXIT BRANCH ===
        if path.get('type') == 'exit':
            step = "generate_exit_text"
            on_update(step, progress_data)
            exit_text = generate_exit_text(get_party_summary(), workflow_name)

            step = "exit_dungeon"
            on_update(step, progress_data)
            manager.exit_dungeon()

            return success_response({
                "exited": True,
                "exit_text": exit_text
            })

        # === PATH BRANCH ===
        # Step 1 - the destination was pre-generated with the path, so
        # arrival is instant (fall back to generating for old saved paths)
        step = "resolve_arrival_location"
        on_update(step, progress_data)
        location = path.get('destination') or generate_arrival_location(previous_location, path, workflow_name)
        manager.set_current_location(location)

        # Step 2 - announce the arrival location to the frontend
        step = "location_generated"
        progress_data.update({ "current_location": location })
        on_update(step, progress_data)

        # === EVENT: MONSTER RIDDLE ===
        event = path.get('event')
        if event == 'monster_riddle':

            # Step 3 - queue streamed vanity text
            step = "queue_encounter_text"
            on_update(step, progress_data)
            encounter_text_generation_id = generate_encounter_vanity_text(location, workflow_name)
            progress_data.update({ "encounter_text_generation_id": encounter_text_generation_id })

            # Step 4 - frontend picks the generation id up from this step
            step = "emit_generation_id"
            on_update(step, progress_data)

            # Step 5 - the monster that dwells here (emits monster.created)
            step = "generate_encounter_monster"
            on_update(step, progress_data)
            monster = generate_contextual_monster(location)
            progress_data.update({ "monster_id": monster.id })

            # Steps 6-7 - abilities (emit monster.ability_added)
            step = "generate_first_ability"
            on_update(step, progress_data)
            generate_ability(monster)

            step = "generate_second_ability"
            on_update(step, progress_data)
            generate_ability(monster)

            # Step 8 - card art, full reveal before the riddle (emits monster.art_ready)
            step = "generate_card_art"
            on_update(step, progress_data)
            generate_card_art(monster)

            # Step 9 - the monster speaks: greeting with its own reason for
            # the challenge, then the riddle (answer NEVER leaves the backend)
            step = "generate_riddle"
            on_update(step, progress_data)
            riddle_data = build_and_generate('riddle', workflow_name, {
                'location_name': location.get('name', 'Unknown Location'),
                'location_description': location.get('description', ''),
                'monster_name': monster.name,
                'monster_species': monster.species,
                'monster_description': monster.description,
                'party_details': get_party_details()
            })

            manager.set_active_encounter({
                'event': 'monster_riddle',
                'monster_id': monster.id,
                'riddle': riddle_data['riddle'],
                'answer': riddle_data['answer']
            })

            return success_response({
                "event": "monster_riddle",
                "current_location": location,
                "monster_id": monster.id,
                "greeting": riddle_data['greeting'],
                "riddle": riddle_data['riddle']
            })

        # === EVENT: MONSTER BATTLE ===
        if event == 'monster_battle':
            from backend.game.battle import manager as battle_manager
            from backend.game.battle.generator import (
                generate_battle_arrival_text,
                generate_battle_intro,
                build_side_details
            )
            from backend.game.battle.constants import ENEMY_COUNT_RANGE
            from backend.game.state.manager import get_party_details
            from backend.models.monster import Monster
            import random as _random

            # Step 3 - queue streamed hostile arrival text
            step = "queue_encounter_text"
            on_update(step, progress_data)
            encounter_text_generation_id = generate_battle_arrival_text(location, workflow_name)
            progress_data.update({ "encounter_text_generation_id": encounter_text_generation_id })

            # Step 4 - frontend picks the generation id up from this step
            step = "emit_generation_id"
            on_update(step, progress_data)

            # Steps 5+ - the hostile monsters, fully revealed (emit domain events)
            enemy_count = _random.randint(*ENEMY_COUNT_RANGE)
            enemies = []
            for i in range(enemy_count):
                step = f"generate_enemy_{i + 1}"
                on_update(step, progress_data)
                enemy = generate_contextual_monster(location)
                generate_ability(enemy)
                generate_ability(enemy)
                generate_card_art(enemy)
                enemies.append(enemy)

            # Battle intro - the enemies' in-character challenge
            step = "generate_battle_intro"
            on_update(step, progress_data)
            enemy_entries = {
                str(enemy.id): {'name': enemy.name, 'condition': 'fresh', 'defending': False}
                for enemy in enemies
            }
            enemy_details = build_side_details({str(e.id): e for e in enemies}, enemy_entries)
            battle_intro = generate_battle_intro(location, enemy_details, get_party_details(), workflow_name)

            # Start the battle - allies carry their run conditions in
            step = "start_battle"
            on_update(step, progress_data)
            ally_conditions = {}
            for monster_id, condition in manager.get_party_conditions().items():
                ally = Monster.get_monster_by_id(int(monster_id))
                ally_conditions[monster_id] = {
                    'name': ally.name if ally else f'Monster {monster_id}',
                    'condition': condition
                }
            battle_state = battle_manager.start_battle(ally_conditions, enemy_entries)

            return success_response({
                "event": "monster_battle",
                "current_location": location,
                "enemy_ids": [enemy.id for enemy in enemies],
                "battle_intro": battle_intro,
                "battle_snapshot": battle_manager.get_battle_snapshot(battle_state)
            })

        # Unknown event - shouldn't happen, but don't strand the player
        raise Exception(f"Unknown path event: {event}")

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

@register_workflow()
def answer_riddle(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """Judge the player's riddle answer semantically via the LLM"""

    workflow_name = 'answer_riddle'
    # "context" should have the following keys:
    required_keys = ["player_answer"]

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon import manager
        from backend.game.state.manager import get_party_details
        from backend.game.utils import build_and_generate
        from backend.models.monster import Monster

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        encounter = manager.get_active_encounter()
        if not encounter:
            raise Exception("No active encounter to answer")

        # The monster who asked - it responds to the party in character
        monster = Monster.get_monster_by_id(encounter.get('monster_id'))

        # Step 1 - LLM judges the answer strictly, then speaks as the monster
        step = "judge_answer"
        on_update(step, progress_data)
        judgement = build_and_generate('riddle_judgement', workflow_name, {
            'riddle': encounter['riddle'],
            'correct_answer': encounter['answer'],
            'player_answer': context['player_answer'],
            'monster_name': monster.name if monster else 'The monster',
            'monster_species': monster.species if monster else 'Unknown',
            'monster_description': monster.description if monster else '',
            'party_details': get_party_details()
        })

        # Step 2 - the encounter is resolved either way
        step = "resolve_encounter"
        on_update(step, progress_data)
        manager.clear_active_encounter()

        return success_response({
            "correct": bool(judgement.get('correct')),
            "response": judgement.get('response', '')
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

@register_workflow()
def continue_exploring(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """Generate fresh paths onward from the current location"""

    workflow_name = 'continue_exploring'
    # "context" should have the following keys:
    required_keys = []

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon.generator import generate_paths
        from backend.game.dungeon import manager
        from backend.game.battle import manager as battle_manager

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        # A finished battle is over once the party moves on
        battle_manager.end_battle()

        location = manager.get_current_location()
        if not location:
            raise Exception("Not currently in a dungeon")

        # Step 1 - new paths from here (hidden events assigned inside)
        step = "generate_paths"
        on_update(step, progress_data)
        paths = generate_paths(location, workflow_name)
        manager.set_available_paths(paths)

        return success_response({
            "current_location": location,
            "paths": manager.get_public_paths()
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })
