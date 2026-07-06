print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from backend.core.workflow_registry import register_workflow
from backend.core.utils.responses import success_response, error_response
from backend.core.utils.validation import require_keys
from typing import Callable, Dict, Any, List

# ===== SHARED BATTLE STARTER =====
# Dialogue outcomes, failed sneaks, and surprise attacks all start battles
# against monsters that ALREADY exist (unlike the monster_battle event,
# which generates its enemies on arrival)

def _start_encounter_battle(monsters: List[Any], opening_note: str = None) -> Dict[str, Any]:
    """Start a battle against existing monsters; returns the battle snapshot"""
    from backend.game.battle import manager as battle_manager
    from backend.game.dungeon import manager
    from backend.models.monster import Monster

    enemy_entries = {
        str(monster.id): {'name': monster.name, 'condition': 'fresh', 'defending': False}
        for monster in monsters
    }

    ally_conditions = {}
    for monster_id, condition in manager.get_party_conditions().items():
        ally = Monster.get_monster_by_id(int(monster_id))
        ally_conditions[monster_id] = {
            'name': ally.name if ally else f'Monster {monster_id}',
            'condition': condition
        }

    battle_state = battle_manager.start_battle(ally_conditions, enemy_entries)

    # Seed the battle's own log so the referee knows how this fight started
    # (an ambush, a failed sneak, an insulted monster...)
    if opening_note:
        battle_manager.append_log(battle_state, opening_note)
        battle_manager.save_battle_state(battle_state)

    return battle_manager.get_battle_snapshot(battle_state)

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
        from backend.game.state.manager import get_party_monster_ids, get_party_summary

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

        party_conditions = {
            str(monster_id): 'fresh' for monster_id in get_party_monster_ids()
        }
        manager.set_party_conditions(party_conditions)

        # The run's story begins
        manager.append_dungeon_log(
            f"The party ({get_party_summary()}) entered the dungeon and arrived at "
            f"{location.get('name', 'an unknown place')}: {location.get('description', '')}"
        )

        return success_response({
            "current_location": location,
            "paths": manager.get_public_paths(),
            "party_conditions": party_conditions
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
            generate_look_around_text,
            generate_exit_text,
            generate_monster_question
        )
        from backend.game.dungeon import manager
        from backend.game.dungeon.events import roll_monsters_present, roll_explore_monster_count
        from backend.game.monster.generator import generate_contextual_monster, generate_ability, generate_card_art
        from backend.game.state.manager import get_party_summary

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
        manager.append_dungeon_log(
            f"The party took the path '{path.get('name', 'unknown')}' and arrived at "
            f"{location.get('name', 'an unknown place')}: {location.get('description', '')}"
        )

        # Step 2 - announce the arrival location to the frontend
        step = "location_generated"
        progress_data.update({ "current_location": location })
        on_update(step, progress_data)

        # === EVENT: LOCATION EXPLORE (the most common arrival) ===
        event = path.get('event')
        if event == 'location_explore':

            # Python decides whether creatures dwell here
            monsters_present = roll_monsters_present()

            # Step 3 - queue streamed look-around text
            step = "queue_look_text"
            on_update(step, progress_data)
            look_text_generation_id = generate_look_around_text(location, monsters_present, workflow_name)
            progress_data.update({ "look_text_generation_id": look_text_generation_id })

            # Step 4 - frontend picks the generation id up from this step
            step = "emit_generation_id"
            on_update(step, progress_data)

            # Steps 5+ - the creatures of this place, revealed live (if any)
            monsters = []
            if monsters_present:
                monster_count = roll_explore_monster_count()
                for i in range(monster_count):
                    step = f"generate_area_monster_{i + 1}"
                    on_update(step, progress_data)
                    monster = generate_contextual_monster(location)
                    generate_ability(monster)
                    generate_ability(monster)
                    generate_card_art(monster)
                    monsters.append(monster)

            # The explore encounter holds what the party found here
            manager.set_active_encounter({
                'event': 'location_explore',
                'monster_ids': [monster.id for monster in monsters],
                'monsters_present': monsters_present,
                'camped': False
            })

            if monsters_present:
                monster_names = ', '.join(f"{m.name} ({m.species})" for m in monsters)
                manager.append_dungeon_log(
                    f"Looking around, the party spotted creatures that have not noticed them yet: {monster_names}."
                )
            else:
                manager.append_dungeon_log("The party looked around and found the area free of other creatures.")

            return success_response({
                "event": "location_explore",
                "current_location": location,
                "monsters_present": monsters_present,
                "monster_ids": [monster.id for monster in monsters],
                "party_conditions": manager.get_party_conditions()
            })

        # === EVENT: MONSTER DIALOGUE (a monster stops the party with a question) ===
        if event == 'monster_dialogue':

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

            # Step 8 - card art, full reveal before it speaks (emits monster.art_ready)
            step = "generate_card_art"
            on_update(step, progress_data)
            generate_card_art(monster)

            # Step 9 - the monster speaks: greeting with its own reason for
            # stopping the party, then its question. What the party answers
            # decides what it does with them (the LLM judges the response)
            step = "generate_monster_question"
            on_update(step, progress_data)
            question_data = generate_monster_question(location, monster, workflow_name)

            manager.set_active_encounter({
                'event': 'monster_dialogue',
                'monster_ids': [monster.id],
                'dialogue': []
            })
            if question_data['greeting']:
                manager.append_encounter_dialogue(monster.name, question_data['greeting'])
            manager.append_encounter_dialogue(monster.name, question_data['question'])

            manager.append_dungeon_log(
                f"At {location.get('name', 'the new location')}, the party was stopped by "
                f"{monster.name} ({monster.species}), who asked them: \"{question_data['question']}\""
            )

            return success_response({
                "event": "monster_dialogue",
                "current_location": location,
                "monster_id": monster.id,
                "greeting": question_data['greeting'],
                "question": question_data['question'],
                "party_conditions": manager.get_party_conditions()
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
            enemy_details = build_side_details({str(e.id): e for e in enemies}, enemy_entries, 'enemies')
            battle_intro = generate_battle_intro(location, enemy_details, get_party_details(), workflow_name)

            # Start the battle - allies carry their run conditions in
            step = "start_battle"
            on_update(step, progress_data)
            battle_snapshot = _start_encounter_battle(enemies)

            enemy_names = ', '.join(f"{e.name} ({e.species})" for e in enemies)
            manager.append_dungeon_log(
                f"Hostile monsters attacked the party on arrival: {enemy_names}. A battle began."
            )

            return success_response({
                "event": "monster_battle",
                "current_location": location,
                "enemy_ids": [enemy.id for enemy in enemies],
                "battle_intro": battle_intro,
                "battle_snapshot": battle_snapshot,
                "party_conditions": manager.get_party_conditions()
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
def respond_to_monster(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """
    The party speaks to the encounter monster(s). The LLM responds in the
    monster's voice and DECIDES the outcome: keep talking, battle, let the
    party pass, reward them, punish them, or join the party.
    Also how the party opens talks with monsters found while exploring.
    """

    workflow_name = 'respond_to_monster'
    # "context" should have the following keys:
    required_keys = ["message"]

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon import manager
        from backend.game.dungeon.generator import build_monsters_details, generate_dialogue_turn
        from backend.game.dungeon.outcomes import apply_dialogue_outcome
        from backend.models.monster import Monster

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        encounter = manager.get_active_encounter()
        if not encounter or not encounter.get('monster_ids'):
            raise Exception("No monsters here to talk to")

        location = manager.get_current_location() or {'name': 'the dungeon', 'description': ''}

        # Talking to monsters found while exploring turns the moment into a dialogue
        if encounter.get('event') == 'location_explore':
            step = "approach_monsters"
            on_update(step, progress_data)
            encounter = {
                'event': 'monster_dialogue',
                'monster_ids': encounter.get('monster_ids', []),
                'dialogue': []
            }
            manager.set_active_encounter(encounter)
            manager.append_dungeon_log("The party approached the creatures and tried to talk with them.")

        if encounter.get('event') != 'monster_dialogue':
            raise Exception("The monsters here are not in a talking mood")

        monsters = [
            m for m in (Monster.get_monster_by_id(int(mid)) for mid in encounter.get('monster_ids', []))
            if m
        ]
        speaker_name = monsters[0].name if len(monsters) == 1 else 'The monsters'

        # Step 1 - record the party's words in the conversation
        step = "record_party_message"
        on_update(step, progress_data)
        message = str(context['message']).strip()
        manager.append_encounter_dialogue('The party', message)

        # Step 2 - the monster responds and decides what happens next
        step = "generate_monster_response"
        on_update(step, progress_data)
        turn = generate_dialogue_turn(
            location,
            build_monsters_details(monsters),
            manager.get_encounter_dialogue_text(),
            workflow_name
        )
        response, outcome = turn['response'], turn['outcome']

        manager.append_encounter_dialogue(speaker_name, response)
        manager.append_dungeon_log(
            f'The party said to {speaker_name}: "{message}" '
            f'{speaker_name} responded: "{response}"'
        )

        # Step 3 - apply the outcome the monster chose
        step = "apply_outcome"
        on_update(step, progress_data)

        if outcome == 'continue_dialogue':
            # The conversation goes on - the encounter stays active
            return success_response({
                "outcome": outcome,
                "response": response
            })

        if outcome == 'begin_battle':
            # Words are over - the monster's last words open the battle
            step = "start_battle"
            on_update(step, progress_data)
            manager.clear_active_encounter()
            battle_snapshot = _start_encounter_battle(
                monsters,
                opening_note=f'{speaker_name} ended the talking: "{response}"'
            )
            manager.append_dungeon_log(f"The conversation turned hostile - {speaker_name} attacked the party!")

            return success_response({
                "outcome": outcome,
                "response": response,
                "battle_intro": response,
                "enemy_ids": [m.id for m in monsters],
                "battle_snapshot": battle_snapshot
            })

        # Every other outcome resolves the encounter peacefully
        applied = apply_dialogue_outcome(outcome, [m.id for m in monsters])
        manager.clear_active_encounter()
        if applied['log_note']:
            manager.append_dungeon_log(applied['log_note'])

        return success_response({
            "outcome": outcome,
            "response": response,
            "joined_names": applied['joined_names']
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

@register_workflow()
def sneak_past(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """
    Try to slip past the monsters spotted while exploring.
    The LLM judges success; failure means the monsters notice - battle.
    """

    workflow_name = 'sneak_past'
    # "context" should have the following keys:
    required_keys = []

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon import manager
        from backend.game.dungeon.generator import build_monsters_details, judge_sneak_attempt
        from backend.models.monster import Monster

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        encounter = manager.get_active_encounter()
        if not encounter or encounter.get('event') != 'location_explore' or not encounter.get('monster_ids'):
            raise Exception("There are no monsters to sneak past")

        location = manager.get_current_location() or {'name': 'the dungeon', 'description': ''}
        monsters = [
            m for m in (Monster.get_monster_by_id(int(mid)) for mid in encounter.get('monster_ids', []))
            if m
        ]
        monster_names = ', '.join(m.name for m in monsters)

        # Step 1 - the referee judges the attempt
        step = "judge_sneak"
        on_update(step, progress_data)
        attempt = judge_sneak_attempt(location, build_monsters_details(monsters), workflow_name)

        step = "resolve_sneak"
        on_update(step, progress_data)
        manager.clear_active_encounter()

        if attempt['success']:
            manager.append_dungeon_log(
                f"The party snuck past {monster_names} without being noticed and pressed on."
            )
            return success_response({
                "success": True,
                "narration": attempt['narration']
            })

        # Noticed! The monsters are on them - battle
        step = "start_battle"
        on_update(step, progress_data)
        battle_snapshot = _start_encounter_battle(
            monsters,
            opening_note=f"The party was caught trying to sneak past: {attempt['narration']}"
        )
        manager.append_dungeon_log(
            f"The party tried to sneak past {monster_names} but was noticed - a battle began!"
        )

        return success_response({
            "success": False,
            "narration": attempt['narration'],
            "battle_intro": attempt['narration'],
            "enemy_ids": [m.id for m in monsters],
            "battle_snapshot": battle_snapshot
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

@register_workflow()
def surprise_attack(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """Strike first at the monsters spotted while exploring - battle on the party's terms"""

    workflow_name = 'surprise_attack'
    # "context" should have the following keys:
    required_keys = []

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon import manager
        from backend.game.dungeon.generator import build_monsters_details, generate_ambush_intro
        from backend.models.monster import Monster

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        encounter = manager.get_active_encounter()
        if not encounter or encounter.get('event') != 'location_explore' or not encounter.get('monster_ids'):
            raise Exception("There are no monsters to ambush")

        location = manager.get_current_location() or {'name': 'the dungeon', 'description': ''}
        monsters = [
            m for m in (Monster.get_monster_by_id(int(mid)) for mid in encounter.get('monster_ids', []))
            if m
        ]
        monster_names = ', '.join(m.name for m in monsters)

        # Step 1 - narrate the ambush being sprung
        step = "generate_ambush_intro"
        on_update(step, progress_data)
        ambush_intro = generate_ambush_intro(location, build_monsters_details(monsters), workflow_name)

        # Step 2 - battle, opened on the party's terms
        step = "start_battle"
        on_update(step, progress_data)
        manager.clear_active_encounter()
        battle_snapshot = _start_encounter_battle(
            monsters,
            opening_note=f"The party sprang a surprise attack - they have the opening moment: {ambush_intro}"
        )
        manager.append_dungeon_log(
            f"The party sprang a surprise attack on {monster_names} - a battle began on their terms!"
        )

        return success_response({
            "battle_intro": ambush_intro,
            "enemy_ids": [m.id for m in monsters],
            "battle_snapshot": battle_snapshot
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

@register_workflow()
def setup_camp(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """
    Set up camp in a monster-free location: streamed vanity dialogue
    between the party's monsters as they rest
    """

    workflow_name = 'setup_camp'
    # "context" should have the following keys:
    required_keys = []

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon import manager
        from backend.game.dungeon.generator import generate_camp_scene
        from backend.models.monster import Monster

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        encounter = manager.get_active_encounter()
        if not encounter or encounter.get('event') != 'location_explore':
            raise Exception("This is no place to camp")
        if encounter.get('monster_ids'):
            raise Exception("Cannot camp with creatures nearby")
        if encounter.get('camped'):
            raise Exception("The party has already camped here")

        location = manager.get_current_location() or {'name': 'the dungeon', 'description': ''}

        # The party's current shape colors the campfire talk
        conditions_lines = []
        for monster_id, condition in manager.get_party_conditions().items():
            monster = Monster.get_monster_by_id(int(monster_id))
            if monster:
                conditions_lines.append(f"- {monster.name}: {condition}")
        party_conditions_text = "\n".join(conditions_lines) or "All fresh"

        # Step 1 - queue the streamed camp scene
        step = "queue_camp_text"
        on_update(step, progress_data)
        camp_text_generation_id = generate_camp_scene(location, party_conditions_text, workflow_name)
        progress_data.update({ "camp_text_generation_id": camp_text_generation_id })

        # Step 2 - frontend picks the generation id up from this step
        step = "emit_generation_id"
        on_update(step, progress_data)

        # Step 3 - one camp per location
        step = "mark_camped"
        on_update(step, progress_data)
        encounter['camped'] = True
        manager.set_active_encounter(encounter)
        manager.append_dungeon_log(
            f"The party set up camp at {location.get('name', 'the area')} and rested, "
            f"talking around the fire."
        )

        return success_response({
            "camped": True
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

@register_workflow()
def use_dungeon_ability(context: dict, on_update: Callable[[str, Dict[str, Any]], None]) -> dict:
    """
    A party monster uses an ability on ANYTHING outside battle - a path,
    a monster, the location, or something the player describes. The LLM
    referee decides whether it does anything at all (heals land, keen
    senses reveal true hints about paths, most odd attempts fizzle).
    """

    workflow_name = 'use_dungeon_ability'
    # "context" should have the following keys:
    required_keys = ["monster_id", "ability_id"]

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon import manager
        from backend.game.dungeon.generator import build_monsters_details, resolve_dungeon_ability
        from backend.game.battle.constants import CONDITION_LADDER, IMPACT_STEPS
        from backend.models.monster import Monster

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        actor = Monster.get_monster_by_id(int(context['monster_id']))
        if not actor:
            raise Exception("Unknown monster")
        ability = next((a for a in (actor.abilities or []) if a.id == context['ability_id']), None)
        if not ability:
            raise Exception(f"{actor.name} does not have that ability")

        location = manager.get_current_location() or {'name': 'the dungeon', 'description': ''}

        # Step 1 - describe the target and gather any secret knowledge
        # (paths know their hidden destination - a perceptive ability can hint at it)
        step = "resolve_target"
        on_update(step, progress_data)

        target_type = str(context.get('target_type') or 'location')
        target_id = context.get('target_id')
        target_text = str(context.get('target_text') or '').strip()
        secret_knowledge = ''
        target_label = ''

        if target_type == 'path' and target_id:
            path = manager.get_path(str(target_id))
            if not path:
                raise Exception(f"Unknown path: {target_id}")
            target_label = f"the path '{path.get('name', 'unknown')}'"
            target_description = (
                f"A path leading onward: {path.get('name', 'unknown')} - {path.get('description', '')}"
            )
            if path.get('type') == 'exit':
                secret_knowledge = "This path truly leads OUT of the dungeon, back to the surface."
            else:
                destination = path.get('destination') or {}
                secret_knowledge = (
                    f"Beyond this path lies: {destination.get('name', 'an unknown place')} - "
                    f"{destination.get('description', '')}"
                )

        elif target_type == 'monster' and target_id:
            target_monster = Monster.get_monster_by_id(int(target_id))
            if not target_monster:
                raise Exception(f"Unknown monster: {target_id}")
            condition = manager.get_party_conditions().get(str(target_monster.id))
            condition_note = f" Its current condition: {condition}." if condition else ""
            target_label = target_monster.name
            target_description = f"A monster.{condition_note}\n{build_monsters_details([target_monster])}"

        elif target_type == 'custom' and target_text:
            target_label = target_text
            target_description = f"The player describes the target as: {target_text}"

        else:
            target_label = f"the location ({location.get('name', 'this place')})"
            target_description = (
                f"The location itself: {location.get('name', 'this place')} - "
                f"{location.get('description', '')}"
            )

        # Step 2 - the dungeon referee judges what actually happens
        step = "resolve_ability"
        on_update(step, progress_data)
        result = resolve_dungeon_ability(
            location,
            build_monsters_details([actor]),
            ability.name,
            ability.description,
            target_description,
            secret_knowledge,
            workflow_name
        )

        # Step 3 - apply any mechanical effect (only party members heal)
        step = "apply_effect"
        on_update(step, progress_data)
        effect = result['effect']

        if effect in ('heal_light', 'heal_major') and target_type == 'monster':
            conditions = manager.get_party_conditions()
            key = str(target_id)
            if key in conditions:
                current_index = CONDITION_LADDER.index(conditions.get(key, 'fresh'))
                new_index = max(0, min(len(CONDITION_LADDER) - 1, current_index + IMPACT_STEPS[effect]))
                conditions[key] = CONDITION_LADDER[new_index]
                manager.set_party_conditions(conditions)
            else:
                effect = 'none'  # healing only sticks to the party

        manager.append_dungeon_log(
            f"{actor.name} used {ability.name} on {target_label}: {result['narration']}"
        )

        return success_response({
            "narration": result['narration'],
            "effect": effect,
            "party_conditions": manager.get_party_conditions()
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

        # A finished battle is over once the party moves on, and a
        # resolved encounter (explored area, ended conversation) is left behind
        battle_manager.end_battle()
        manager.clear_active_encounter()

        location = manager.get_current_location()
        if not location:
            raise Exception("Not currently in a dungeon")

        # Step 1 - new paths from here (hidden events assigned inside)
        step = "generate_paths"
        on_update(step, progress_data)
        paths = generate_paths(location, workflow_name)
        manager.set_available_paths(paths)

        path_names = ', '.join(p.get('name', 'unknown') for p in paths.values())
        manager.append_dungeon_log(
            f"The party looked for ways onward from {location.get('name', 'the area')}. "
            f"Paths ahead: {path_names}."
        )

        return success_response({
            "current_location": location,
            "paths": manager.get_public_paths(),
            "party_conditions": manager.get_party_conditions()
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })
