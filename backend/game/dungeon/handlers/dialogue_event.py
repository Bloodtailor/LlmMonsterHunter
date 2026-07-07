# Monster dialogue - a monster stops the party with a question.
# What the party answers decides what it does with them.

from typing import Any

from backend.core.utils.responses import success_response
from backend.core.workflow_steps import WorkflowStep


def run_monster_dialogue(step: WorkflowStep, location: dict, workflow_name: str) -> dict[str, Any]:
    """Reveal (or recall) the questioner and open the dialogue"""
    from backend.game.dungeon import manager
    from backend.game.dungeon.generator import (
        generate_encounter_vanity_text,
        generate_monster_question,
    )
    from backend.game.monster.card_art import generate_card_art
    from backend.game.monster.generator import (
        generate_ability,
        generate_contextual_monster,
    )

    # Step 3 - queue streamed vanity text
    step.emit("queue_encounter_text")
    encounter_text_generation_id = generate_encounter_vanity_text(location, workflow_name)
    step.data.update({"encounter_text_generation_id": encounter_text_generation_id})

    # Step 4 - frontend picks the generation id up from this step
    step.emit("emit_generation_id")

    # Step 5 - the monster that dwells here. Sometimes it is one
    # the party has met before (blend-in: no generation needed).
    from backend.game.memory import returning

    monster = returning.maybe_blend_in()
    if monster:
        step.emit("reveal_returning_monster")
        returning.stage_reveal(monster)
        step.data.update({"monster_id": monster.id})
    else:
        step.emit("generate_encounter_monster")
        monster = generate_contextual_monster(location)
        step.data.update({"monster_id": monster.id})

        # Steps 6-7 - abilities (emit monster.ability_added)
        step.emit("generate_first_ability")
        generate_ability(monster)

        step.emit("generate_second_ability")
        generate_ability(monster)

        # Step 8 - card art, full reveal before it speaks (emits monster.art_ready)
        step.emit("generate_card_art")
        generate_card_art(monster)

    # Step 9 - the monster speaks: greeting with its own reason for
    # stopping the party, then its question. What the party answers
    # decides what it does with them (the LLM judges the response)
    step.emit("generate_monster_question")
    question_data = generate_monster_question(location, monster, workflow_name)

    from backend.game.memory.manager import mark_seen

    mark_seen([monster.id])

    manager.set_active_encounter(
        {'event': 'monster_dialogue', 'monster_ids': [monster.id], 'dialogue': []}
    )
    if question_data['greeting']:
        manager.append_encounter_dialogue(monster.name, question_data['greeting'])
    manager.append_encounter_dialogue(monster.name, question_data['question'])

    manager.append_dungeon_log(
        f"At {location.get('name', 'the new location')}, the party was stopped by "
        f"{monster.name} ({monster.species}), who asked them: \"{question_data['question']}\""
    )

    return success_response(
        {
            "event": "monster_dialogue",
            "current_location": location,
            "monster_id": monster.id,
            "greeting": question_data['greeting'],
            "question": question_data['question'],
            "party_conditions": manager.get_party_conditions(),
        }
    )
