print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from typing import Any, Callable

from backend.core.utils.responses import error_response, success_response
from backend.core.utils.validation import require_keys
from backend.core.workflow_registry import register_workflow

# ===== SHARED BATTLE STARTER =====
# Dialogue outcomes, failed sneaks, and surprise attacks all start battles
# against monsters that ALREADY exist (unlike the monster_battle event,
# which generates its enemies on arrival)

def _start_encounter_battle(monsters: list[Any], opening_note: str = None) -> dict[str, Any]:
    """Start a battle against existing monsters; returns the battle snapshot"""
    from backend.game.battle import manager as battle_manager
    from backend.game.dungeon import manager
    from backend.models.monster import Monster

    enemy_entries = {
        str(monster.id): {'name': monster.name, 'condition': 'fresh', 'defending': False}
        for monster in monsters
    }

    ally_conditions = {}
    party_resources = manager.get_party_resources()
    for monster_id, condition in manager.get_party_conditions().items():
        ally = Monster.get_monster_by_id(int(monster_id))
        pools = party_resources.get(str(monster_id), {})
        ally_conditions[monster_id] = {
            'name': ally.name if ally else f'Monster {monster_id}',
            'condition': condition,
            'stamina': pools.get('stamina', 'brimming'),
            'mana': pools.get('mana', 'brimming')
        }

    battle_state = battle_manager.start_battle(ally_conditions, enemy_entries)

    # Seed the battle's own log so the referee knows how this fight started
    # (an ambush, a failed sneak, an insulted monster...)
    if opening_note:
        battle_manager.append_log(battle_state, opening_note)
        battle_manager.save_battle_state(battle_state)

    return battle_manager.get_battle_snapshot(battle_state)

@register_workflow()
def enter_dungeon(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """Enter the dungeon: entry text, starting location, and first paths"""

    workflow_name = 'enter_dungeon'
    # "context" should have the following keys:
    required_keys = []

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.battle import manager as battle_manager
        from backend.game.dungeon import manager
        from backend.game.dungeon.generator import (
            generate_entry_text,
            generate_paths,
            generate_random_location,
        )
        from backend.game.state.manager import get_party_monster_ids, get_party_summary

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        # A fresh run starts clean: any stale battle from a previous run
        # is cleared (start_dungeon below resets the dungeon state and log)
        battle_manager.end_battle()

        # A leftover run (the player walked away mid-run) still deserves
        # its place in the chat context - snapshot its log before begin()
        # closes it and start_dungeon wipes it
        if manager.is_in_dungeon():
            manager.snapshot_last_run_log('abandoned')

        # Open this run's row in the run history (closes any dangling
        # active run as 'abandoned' first)
        from backend.models.dungeon_run import DungeonRun
        run = DungeonRun.begin()

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
        manager.start_dungeon(location, paths, run_id=run.id if run else None)

        party_conditions = {
            str(monster_id): 'fresh' for monster_id in get_party_monster_ids()
        }
        manager.set_party_conditions(party_conditions)

        # Stamina and mana come back full ONLY here - entering the
        # dungeon is the one guaranteed reset of the party's reserves
        from backend.game.battle.constants import full_resources
        party_resources = {
            str(monster_id): full_resources() for monster_id in get_party_monster_ids()
        }
        manager.set_party_resources(party_resources)

        # The run's story begins
        manager.append_dungeon_log(
            f"The party ({get_party_summary()}) entered the dungeon and arrived at "
            f"{location.get('name', 'an unknown place')}: {location.get('description', '')}"
        )

        return success_response({
            "current_location": location,
            "paths": manager.get_public_paths(),
            "party_conditions": party_conditions,
            "party_resources": party_resources
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

@register_workflow()
def choose_path(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
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
        from backend.game.dungeon import manager
        from backend.game.dungeon.events import roll_explore_monster_count, roll_monsters_present
        from backend.game.dungeon.generator import (
            generate_arrival_location,
            generate_encounter_vanity_text,
            generate_exit_text,
            generate_look_around_text,
            generate_monster_question,
        )
        from backend.game.monster.generator import (
            generate_ability,
            generate_card_art,
            generate_contextual_monster,
        )
        from backend.game.state.manager import get_party_summary

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        # Condense old dungeon-log entries if enough have piled up (the
        # queued workflow runs AFTER this one - the player never waits)
        manager.queue_log_condense_if_due()

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

            # The exit ceremony: walking out alive, EVERY member reflects
            # on the whole run and grows from what the journal shows.
            # A failure here never blocks the exit itself.
            step = "exit_ceremony"
            on_update(step, progress_data)
            growth_results = []
            try:
                from backend.game.memory import growth
                from backend.game.memory.manager import write_memory
                from backend.game.state.manager import get_party_monster_ids
                from backend.models.monster import Monster

                for monster_id in get_party_monster_ids():
                    monster = Monster.get_monster_by_id(monster_id)
                    if not monster:
                        continue
                    progress_data.update({ "growing": monster.name })
                    on_update(step, progress_data)
                    reflection = growth.run_growth_reflection(monster, 'exit', workflow_name)
                    if reflection:
                        growth_results.append(growth.apply_growth(monster, reflection))
                    write_memory(
                        monster.id, 'run_complete',
                        "Walked out of the dungeon alive with the party, carrying "
                        "everything the run had made of it."
                    )
            except Exception as ceremony_error:
                print(f"❌ Exit ceremony failed (the exit itself stands): {ceremony_error}")
            progress_data.update({ "growth": growth_results })

            # Close this run's row in the history while the run state
            # still exists (exit_dungeon wipes it), and preserve the run's
            # log for conversations back home
            step = "close_run"
            on_update(step, progress_data)
            from backend.models.dungeon_run import DungeonRun
            log_entries = manager.get_dungeon_log_entries()
            manager.snapshot_last_run_log('victory_exit')
            DungeonRun.close('victory_exit', summary=log_entries[-1] if log_entries else None)

            step = "exit_dungeon"
            on_update(step, progress_data)
            manager.exit_dungeon()

            return success_response({
                "exited": True,
                "exit_text": exit_text,
                "growth": growth_results
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

        event = path.get('event')

        # === EVENT: RETURNING MONSTER (someone here remembers the party) ===
        if event == 'returning_monster':
            from backend.game.memory import returning

            step = "pick_returning_monster"
            on_update(step, progress_data)
            remembered = returning.pick_returning_monster()

            if not remembered:
                # The pool emptied since this path was generated (e.g. the
                # monster joined the party at a sibling path) - degrade
                # invisibly to a plain explore; events are hidden anyway
                event = 'location_explore'
            else:
                # The monster returns CHANGED by what it remembers
                step = "transform_returning_monster"
                on_update(step, progress_data)
                transformed = returning.transform_returning_monster(remembered, workflow_name)
                disposition = transformed['disposition']
                greeting = transformed['greeting']

                step = "reveal_returning_monster"
                on_update(step, progress_data)
                returning.stage_reveal(remembered)
                progress_data.update({ "monster_id": remembered.id, "returning": True })

                # The recognition scene streams while the encounter stages
                step = "queue_reunion_text"
                on_update(step, progress_data)
                from backend.game.dungeon.generator import generate_reunion_scene
                reunion_text_generation_id = generate_reunion_scene(
                    location, remembered, disposition, workflow_name
                )
                progress_data.update({ "reunion_text_generation_id": reunion_text_generation_id })

                step = "emit_generation_id"
                on_update(step, progress_data)

                manager.append_dungeon_log(
                    f"At {location.get('name', 'the new location')}, the party came face to "
                    f"face with {remembered.name} ({remembered.species}) again - it remembers "
                    f"them, and its bearing is {disposition}."
                )

                if disposition == 'hostile':
                    # A reckoning - straight to battle, its greeting as the intro
                    step = "start_battle"
                    on_update(step, progress_data)
                    battle_snapshot = _start_encounter_battle(
                        [remembered],
                        opening_note=(f"{remembered.name} has returned to face the party, "
                                      f"hardened by its memories: \"{greeting}\"")
                    )
                    return success_response({
                        "event": "monster_battle",
                        "returning": True,
                        "current_location": location,
                        "enemy_ids": [remembered.id],
                        "battle_intro": greeting,
                        "battle_snapshot": battle_snapshot,
                        "party_conditions": manager.get_party_conditions()
                    })

                if disposition == 'friendly':
                    # A warm reunion - it opens the conversation itself
                    manager.set_active_encounter({
                        'event': 'monster_dialogue',
                        'monster_ids': [remembered.id],
                        'dialogue': []
                    })
                    manager.append_encounter_dialogue(remembered.name, greeting)
                    return success_response({
                        "event": "monster_dialogue",
                        "returning": True,
                        "current_location": location,
                        "monster_id": remembered.id,
                        "greeting": greeting,
                        "question": "",
                        "party_conditions": manager.get_party_conditions()
                    })

                # wary - a watchful standoff; talk, sneak, or ambush all work
                manager.set_active_encounter({
                    'event': 'location_explore',
                    'monster_ids': [remembered.id],
                    'monsters_present': True,
                    'camped': False
                })
                return success_response({
                    "event": "location_explore",
                    "returning": True,
                    "current_location": location,
                    "monsters_present": True,
                    "monster_ids": [remembered.id],
                    "greeting": greeting,
                    "party_conditions": manager.get_party_conditions()
                })

        # === EVENT: LOCATION EXPLORE (the most common arrival) ===
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

            # Steps 5+ - the creatures of this place, revealed live (if any).
            # Sometimes one of them is a monster the party has met before -
            # it takes a fresh monster's slot, memories and all (no
            # generation needed; it already exists in full).
            monsters = []
            if monsters_present:
                from backend.game.memory import returning

                monster_count = roll_explore_monster_count()
                blended = returning.maybe_blend_in()
                if blended:
                    step = "reveal_returning_monster"
                    on_update(step, progress_data)
                    returning.stage_reveal(blended)
                    monsters.append(blended)
                    monster_count -= 1

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

            from backend.game.memory.journal import append_party_journal
            from backend.game.memory.manager import mark_seen
            mark_seen([monster.id for monster in monsters])

            if monsters_present:
                monster_names = ', '.join(f"{m.name} ({m.species})" for m in monsters)
                manager.append_dungeon_log(
                    f"Looking around, the party spotted creatures that have not noticed them yet: {monster_names}."
                )
                append_party_journal(f"Explored {location.get('name', 'a new area')} and spotted {monster_names}.")
            else:
                manager.append_dungeon_log("The party looked around and found the area free of other creatures.")
                append_party_journal(f"Explored {location.get('name', 'a new area')} - quiet and empty.")

            return success_response({
                "event": "location_explore",
                "current_location": location,
                "monsters_present": monsters_present,
                "monster_ids": [monster.id for monster in monsters],
                "party_conditions": manager.get_party_conditions()
            })

        # === EVENT: TREASURE (a hidden item waits to be discovered) ===
        if event == 'treasure':
            from backend.game.inventory.generator import (
                generate_treasure_discovery_text,
                generate_treasure_item,
            )

            # Step 3 - the item itself (emits inventory.item_added)
            step = "generate_treasure_item"
            on_update(step, progress_data)
            item = generate_treasure_item(location)
            progress_data.update({ "item": item.to_dict() })

            # Step 4 - queue streamed discovery narration referencing the item
            step = "queue_treasure_text"
            on_update(step, progress_data)
            treasure_text_generation_id = generate_treasure_discovery_text(location, item, workflow_name)
            progress_data.update({ "treasure_text_generation_id": treasure_text_generation_id })

            # Step 5 - frontend picks the generation id up from this step
            step = "emit_generation_id"
            on_update(step, progress_data)

            # After the discovery the moment plays like a creature-free
            # explore - the party looks up and decides where to go next
            manager.set_active_encounter({
                'event': 'location_explore',
                'monster_ids': [],
                'monsters_present': False,
                'camped': False
            })

            manager.append_dungeon_log(
                f"At {location.get('name', 'the new location')}, the party discovered "
                f"a hidden treasure: {item.name} ({item.description})"
            )
            from backend.game.memory.journal import append_party_journal
            append_party_journal(f"Found treasure at {location.get('name', 'a new area')}: {item.name}.")

            return success_response({
                "event": "treasure",
                "current_location": location,
                "item": item.to_dict(),
                "monsters_present": False,
                "monster_ids": [],
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

            # Step 5 - the monster that dwells here. Sometimes it is one
            # the party has met before (blend-in: no generation needed).
            from backend.game.memory import returning
            monster = returning.maybe_blend_in()
            if monster:
                step = "reveal_returning_monster"
                on_update(step, progress_data)
                returning.stage_reveal(monster)
                progress_data.update({ "monster_id": monster.id })
            else:
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

            from backend.game.memory.manager import mark_seen
            mark_seen([monster.id])

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
            import random as _random

            from backend.game.battle.constants import ENEMY_COUNT_RANGE
            from backend.game.battle.generator import (
                build_side_details,
                generate_battle_arrival_text,
                generate_battle_intro,
            )
            from backend.game.state.manager import get_party_details

            # Step 3 - queue streamed hostile arrival text
            step = "queue_encounter_text"
            on_update(step, progress_data)
            encounter_text_generation_id = generate_battle_arrival_text(location, workflow_name)
            progress_data.update({ "encounter_text_generation_id": encounter_text_generation_id })

            # Step 4 - frontend picks the generation id up from this step
            step = "emit_generation_id"
            on_update(step, progress_data)

            # Steps 5+ - the hostile monsters, fully revealed (emit domain
            # events). An avoided or bested monster from another day may
            # be running with this pack (blend-in).
            from backend.game.memory import returning
            enemy_count = _random.randint(*ENEMY_COUNT_RANGE)
            enemies = []

            blended = returning.maybe_blend_in()
            if blended:
                step = "reveal_returning_monster"
                on_update(step, progress_data)
                returning.stage_reveal(blended)
                enemies.append(blended)
                enemy_count -= 1

            for i in range(enemy_count):
                step = f"generate_enemy_{i + 1}"
                on_update(step, progress_data)
                enemy = generate_contextual_monster(location)
                generate_ability(enemy)
                generate_ability(enemy)
                generate_card_art(enemy)
                enemies.append(enemy)

            from backend.game.memory.manager import mark_seen
            mark_seen([enemy.id for enemy in enemies])

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
def respond_to_monster(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
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
        from backend.game.dungeon.generator import (
            build_speaking_monsters_details,
            generate_dialogue_turn,
        )
        from backend.game.dungeon.outcomes import apply_dialogue_outcome
        from backend.models.monster import Monster

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        # Long conversations grow the log - condense old entries if due
        manager.queue_log_condense_if_due()

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
            build_speaking_monsters_details(monsters),
            manager.get_encounter_dialogue_text(),
            workflow_name
        )
        response, outcome = turn['response'], turn['outcome']

        manager.append_encounter_dialogue(speaker_name, response)
        manager.append_dungeon_log(
            f'The party said to {speaker_name}: "{message}" '
            f'{speaker_name} responded: "{response}"'
        )
        from backend.game.memory import journal
        journal.append_party_journal(
            f'Talked with {speaker_name}: said "{message[:70]}" - heard "{response[:60]}"'
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
        applied = apply_dialogue_outcome(outcome, [m.id for m in monsters], location)
        manager.clear_active_encounter()
        if applied['log_note']:
            manager.append_dungeon_log(applied['log_note'])

        return success_response({
            "outcome": outcome,
            "response": response,
            "joined_names": applied['joined_names'],
            "item": applied.get('item')
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

@register_workflow()
def sneak_past(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
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

            # The avoided monsters keep only a vague impression - enough
            # for them to resurface in another group someday
            from backend.game.memory.journal import append_party_journal
            from backend.game.memory.manager import write_memory
            location_name = location.get('name', 'the dungeon')
            for avoided in monsters:
                write_memory(
                    avoided.id, 'avoided',
                    f"Sensed someone slip through its territory at {location_name}, "
                    f"but never saw them clearly.",
                    {'location': location_name}
                )
            append_party_journal(f"Slipped past {monster_names} unseen at {location_name}.")

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
def surprise_attack(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
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
def setup_camp(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
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

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        # A quiet moment - condense old dungeon-log entries if due
        manager.queue_log_condense_if_due()

        encounter = manager.get_active_encounter()
        if not encounter or encounter.get('event') != 'location_explore':
            raise Exception("This is no place to camp")
        if encounter.get('monster_ids'):
            raise Exception("Cannot camp with creatures nearby")
        if encounter.get('camped'):
            raise Exception("The party has already camped here")

        location = manager.get_current_location() or {'name': 'the dungeon', 'description': ''}

        # Step 1 - queue the streamed camp scene (party conditions travel
        # inside the full party details block)
        step = "queue_camp_text"
        on_update(step, progress_data)
        camp_text_generation_id = generate_camp_scene(location, workflow_name)
        progress_data.update({ "camp_text_generation_id": camp_text_generation_id })

        # Step 2 - frontend picks the generation id up from this step
        step = "emit_generation_id"
        on_update(step, progress_data)

        # Step 3 - one camp per location (marked BEFORE the rest/growth
        # steps so a failure below can never enable double-camping)
        step = "mark_camped"
        on_update(step, progress_data)
        encounter['camped'] = True
        manager.set_active_encounter(encounter)
        manager.append_dungeon_log(
            f"The party set up camp at {location.get('name', 'the area')} and rested, "
            f"talking around the fire."
        )

        # Step 4 - rest restores the party's reserves (the camp referee
        # judges how much for each monster; failures mean a full rest)
        step = "restore_resources"
        on_update(step, progress_data)
        from backend.game.battle.constants import (
            BRIMMING,
            RESOURCE_DELTAS,
            RESOURCE_LADDER,
            full_resources,
        )
        from backend.game.dungeon.generator import generate_camp_restore

        restores = generate_camp_restore(location, workflow_name)
        party_resources = manager.get_party_resources()
        for monster_id, pools in restores.items():
            current = party_resources.get(str(monster_id)) or full_resources()
            for resource, delta_word in pools.items():
                steps_delta = RESOURCE_DELTAS.get(delta_word, 0)
                if steps_delta == 0:
                    continue
                current_index = RESOURCE_LADDER.index(current.get(resource, BRIMMING))
                new_index = max(0, min(len(RESOURCE_LADDER) - 1, current_index + steps_delta))
                current[resource] = RESOURCE_LADDER[new_index]
            party_resources[str(monster_id)] = current
        manager.set_party_resources(party_resources)
        progress_data.update({ "party_resources": party_resources })

        # Step 5 - growth: the fire spotlights the 1-2 members whose story
        # mattered most this run; the rest keep the memory of the evening.
        # A failure here never breaks the camp itself.
        step = "camp_growth"
        on_update(step, progress_data)
        growth_results = []
        try:
            from backend.game.memory import growth
            from backend.game.memory.manager import write_memory
            from backend.game.state.manager import get_party_monster_ids
            from backend.models.monster import Monster

            party_monsters = [
                m for m in (Monster.get_monster_by_id(mid) for mid in get_party_monster_ids())
                if m
            ]
            spotlight = growth.pick_spotlight(party_monsters, workflow_name)
            for monster in spotlight:
                step = "growth_reflection"
                progress_data.update({ "growing": monster.name })
                on_update(step, progress_data)
                reflection = growth.run_growth_reflection(monster, 'camp', workflow_name)
                if reflection:
                    growth_results.append(growth.apply_growth(monster, reflection))

            spotlight_ids = {m.id for m in spotlight}
            location_name = location.get('name', 'the dungeon')
            for monster in party_monsters:
                if monster.id not in spotlight_ids:
                    write_memory(
                        monster.id, 'camp',
                        f"Rested at a campfire at {location_name} with the party.",
                        {'location': location_name}
                    )
        except Exception as growth_error:
            print(f"❌ Camp growth failed (the camp itself stands): {growth_error}")

        progress_data.update({ "growth": growth_results })

        return success_response({
            "camped": True,
            "party_resources": party_resources,
            "growth": growth_results
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

def _resolve_dungeon_target(context: dict, manager, location: dict):
    """
    Describe an out-of-battle target and gather any secret knowledge
    (paths know their hidden destination - a perceptive use can hint at it).
    Shared by the ability and item dungeon-referee workflows.
    Returns (target_type, target_id, target_label, target_description, secret_knowledge)
    """
    from backend.game.dungeon.generator import build_monsters_details
    from backend.models.monster import Monster

    target_type = str(context.get('target_type') or 'location')
    target_id = context.get('target_id')
    target_text = str(context.get('target_text') or '').strip()
    secret_knowledge = ''

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

    return target_type, target_id, target_label, target_description, secret_knowledge

def _apply_party_heal_effect(effect: str, target_type: str, target_id, manager) -> str:
    """Healing effects stick only to party members; returns the (possibly
    downgraded) effect. Shared by the ability and item workflows."""
    from backend.game.battle.constants import CONDITION_LADDER, IMPACT_STEPS

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
    return effect

def _apply_dungeon_resource_deltas(manager, actor, ability, stamina_delta, mana_delta,
                                   target_type, target_id):
    """
    Out-of-battle resource accounting. The referee's words rule; when it
    stays silent on both pools, the ability's type picks the pool and the
    cost is moderate. Costs tire the ACTOR; restores land on a party-member
    target (else the actor). Pools live in dungeon party_resources.
    """
    from backend.game.battle.constants import (
        ABILITY_POOL_BY_TYPE,
        BRIMMING,
        RESOURCE_DELTAS,
        RESOURCE_LADDER,
        full_resources,
    )
    from backend.game.state.manager import get_party_monster_ids

    if stamina_delta is None and mana_delta is None:
        pool = ABILITY_POOL_BY_TYPE.get(ability.ability_type, 'stamina')
        stamina_delta, mana_delta = ('moderate', None) if pool == 'stamina' else (None, 'moderate')

    resources = manager.get_party_resources()

    def step_pool(monster_id, resource, delta_word):
        pools = resources.get(str(monster_id))
        if pools is None:
            pools = full_resources()
        steps = RESOURCE_DELTAS.get(delta_word, 0)
        current_index = RESOURCE_LADDER.index(pools.get(resource, BRIMMING))
        new_index = max(0, min(len(RESOURCE_LADDER) - 1, current_index + steps))
        pools[resource] = RESOURCE_LADDER[new_index]
        resources[str(monster_id)] = pools

    restore_target_id = actor.id
    if target_type == 'monster' and target_id and int(target_id) in get_party_monster_ids():
        restore_target_id = int(target_id)

    for resource, delta in (('stamina', stamina_delta), ('mana', mana_delta)):
        if not delta or delta == 'none':
            continue
        if RESOURCE_DELTAS.get(delta, 0) > 0:
            step_pool(actor.id, resource, delta)
        else:
            step_pool(restore_target_id, resource, delta)

    manager.set_party_resources(resources)

@register_workflow()
def use_dungeon_ability(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
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
        step = "resolve_target"
        on_update(step, progress_data)
        target_type, target_id, target_label, target_description, secret_knowledge = \
            _resolve_dungeon_target(context, manager, location)

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
        effect = _apply_party_heal_effect(result['effect'], target_type, target_id, manager)

        # Step 4 - the ability drains (or restores) reserves. Costs hit the
        # actor; restores land on a party-member target, else the actor.
        step = "apply_resource_costs"
        on_update(step, progress_data)
        _apply_dungeon_resource_deltas(
            manager, actor, ability,
            result.get('stamina_delta'), result.get('mana_delta'),
            target_type, target_id
        )

        manager.append_dungeon_log(
            f"{actor.name} used {ability.name} on {target_label}: {result['narration']}"
        )
        from backend.game.memory.journal import append_journal
        append_journal(
            actor.id,
            f"Used {ability.name} on {target_label} outside battle: {result['narration'][:100]}"
        )

        return success_response({
            "narration": result['narration'],
            "effect": effect,
            "party_conditions": manager.get_party_conditions(),
            "party_resources": manager.get_party_resources()
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

@register_workflow()
def use_dungeon_item(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    The party uses an inventory ITEM on anything outside battle. The LLM
    referee reads the item's description and decides what actually happens.
    One use is spent regardless of the outcome (during battle, items cost
    a turn instead - see the battle_turn workflow).
    """

    workflow_name = 'use_dungeon_item'
    # "context" should have the following keys:
    required_keys = ["item_id"]

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon import manager
        from backend.game.dungeon.generator import resolve_dungeon_item
        from backend.game.inventory.manager import spend_item_use
        from backend.models.item import Item

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        item = Item.get_item_by_id(int(context['item_id']))
        if not item or item.uses_remaining < 1:
            raise Exception("That item is not in the party's inventory")

        location = manager.get_current_location() or {'name': 'the dungeon', 'description': ''}

        # Step 1 - describe the target and gather any secret knowledge
        step = "resolve_target"
        on_update(step, progress_data)
        target_type, target_id, target_label, target_description, secret_knowledge = \
            _resolve_dungeon_target(context, manager, location)

        # Step 2 - the dungeon referee judges what actually happens
        step = "resolve_item"
        on_update(step, progress_data)
        result = resolve_dungeon_item(
            location,
            item,
            target_description,
            secret_knowledge,
            workflow_name
        )

        # Step 3 - apply any mechanical effect (only party members heal)
        step = "apply_effect"
        on_update(step, progress_data)
        effect = _apply_party_heal_effect(result['effect'], target_type, target_id, manager)

        # Step 4 - one use is spent no matter what came of it
        # (emits inventory.item_updated or inventory.item_consumed)
        step = "spend_item_use"
        on_update(step, progress_data)
        item_name = item.name
        spend_result = spend_item_use(item)
        progress_data.update({ "item_spend": spend_result })

        manager.append_dungeon_log(
            f"The party used {item_name} on {target_label}: {result['narration']}"
        )

        return success_response({
            "narration": result['narration'],
            "effect": effect,
            "item_spend": spend_result,
            "party_conditions": manager.get_party_conditions()
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })

@register_workflow()
def continue_exploring(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """Generate fresh paths onward from the current location"""

    workflow_name = 'continue_exploring'
    # "context" should have the following keys:
    required_keys = []

    # Set the initial conditions
    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.battle import manager as battle_manager
        from backend.game.dungeon import manager
        from backend.game.dungeon.generator import generate_paths

        # Step 0 - validate required keys
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        # Moving on - condense old dungeon-log entries if due
        manager.queue_log_condense_if_due()

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

@register_workflow()
def condense_dungeon_log(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    Housekeeping: condense ONE batch of the oldest un-summarized dungeon
    log entries into a rolling summary. Queued by the heavier dungeon
    workflows when enough entries pile up; the sequential worker runs it
    after the player already has their result. A no-op if the run ended
    or the batch is no longer due.
    """

    workflow_name = 'condense_dungeon_log'

    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.dungeon import manager
        from backend.game.utils.rolling_summary import covered_count, plan_batch, summarize_lines

        step = "plan_batch"
        on_update(step, progress_data)
        entries = manager.get_dungeon_log_entries()
        summaries = manager.get_dungeon_log_summaries()
        batch = plan_batch('dungeon_log', len(entries), covered_count(summaries))
        if not batch:
            return success_response({"condensed": False})

        step = "condense_batch"
        on_update(step, progress_data)
        start, end = batch
        prior = summaries[-1]['text'] if summaries else None
        summary_text = summarize_lines(
            'dungeon_log', entries[start:end], workflow_name, prior_summary=prior
        )
        if not summary_text:
            # The batch stays uncovered and retries at the next trigger
            return success_response({"condensed": False})

        step = "record_summary"
        on_update(step, progress_data)
        manager.record_dungeon_log_summary(end, summary_text)

        return success_response({
            "condensed": True,
            "covers_entries": end
        })

    except Exception as e:
        return error_response({
            'failed_at': step,
            'completed_work': progress_data,
            'error': str(e)
        })
