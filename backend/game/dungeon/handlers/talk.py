# Talking with encounter monsters - the party speaks, the LLM answers in
# the monster's voice and DECIDES the outcome.

from typing import Any

from backend.core.utils.responses import success_response
from backend.core.utils.validation import require_keys
from backend.core.workflow_steps import WorkflowStep

from .encounter_battle import start_encounter_battle


def run_respond_to_monster(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """One conversational turn: record, respond, apply the chosen outcome"""
    workflow_name = 'respond_to_monster'

    from backend.game.dungeon import manager
    from backend.game.dungeon.generator import (
        build_speaking_monsters_details,
        generate_dialogue_turn,
    )
    from backend.game.dungeon.outcomes import apply_dialogue_outcome
    from backend.models.monster import Monster

    # Step 0 - validate required keys
    step.emit("validate_context")
    require_keys(context, ["message"])

    # Long conversations grow the log - condense old entries if due
    manager.queue_log_condense_if_due()

    encounter = manager.get_active_encounter()
    if not encounter or not encounter.get('monster_ids'):
        raise Exception("No monsters here to talk to")

    location = manager.get_current_location() or {'name': 'the dungeon', 'description': ''}

    # Talking to monsters found while exploring turns the moment into a dialogue
    if encounter.get('event') == 'location_explore':
        step.emit("approach_monsters")
        encounter = {
            'event': 'monster_dialogue',
            'monster_ids': encounter.get('monster_ids', []),
            'dialogue': [],
        }
        manager.set_active_encounter(encounter)
        manager.append_dungeon_log(
            "The party approached the creatures and tried to talk with them."
        )

    if encounter.get('event') != 'monster_dialogue':
        raise Exception("The monsters here are not in a talking mood")

    monsters = [
        m
        for m in (Monster.get_monster_by_id(int(mid)) for mid in encounter.get('monster_ids', []))
        if m
    ]
    speaker_name = monsters[0].name if len(monsters) == 1 else 'The monsters'

    # Step 1 - record the party's words in the conversation
    step.emit("record_party_message")
    message = str(context['message']).strip()
    manager.append_encounter_dialogue('The party', message)

    # Step 2 - the monster responds and decides what happens next
    step.emit("generate_monster_response")
    turn = generate_dialogue_turn(
        location,
        build_speaking_monsters_details(monsters),
        manager.get_encounter_dialogue_text(),
        workflow_name,
    )
    response, outcome = turn['response'], turn['outcome']

    manager.append_encounter_dialogue(speaker_name, response)
    manager.append_dungeon_log(
        f'The party said to {speaker_name}: "{message}" {speaker_name} responded: "{response}"'
    )
    from backend.game.memory import journal

    journal.append_party_journal(
        f'Talked with {speaker_name}: said "{message[:70]}" - heard "{response[:60]}"'
    )

    # Step 3 - apply the outcome the monster chose
    step.emit("apply_outcome")

    if outcome == 'continue_dialogue':
        # The conversation goes on - the encounter stays active
        return success_response({"outcome": outcome, "response": response})

    if outcome == 'begin_battle':
        # Words are over - the monster's last words open the battle
        step.emit("start_battle")
        manager.clear_active_encounter()
        battle_snapshot = start_encounter_battle(
            monsters, opening_note=f'{speaker_name} ended the talking: "{response}"'
        )
        manager.append_dungeon_log(
            f"The conversation turned hostile - {speaker_name} attacked the party!"
        )

        return success_response(
            {
                "outcome": outcome,
                "response": response,
                "battle_intro": response,
                "enemy_ids": [m.id for m in monsters],
                "battle_snapshot": battle_snapshot,
            }
        )

    # Every other outcome resolves the encounter peacefully
    applied = apply_dialogue_outcome(outcome, [m.id for m in monsters], location)
    manager.clear_active_encounter()
    if applied['log_note']:
        manager.append_dungeon_log(applied['log_note'])

    return success_response(
        {
            "outcome": outcome,
            "response": response,
            "joined_names": applied['joined_names'],
            "item": applied.get('item'),
        }
    )
