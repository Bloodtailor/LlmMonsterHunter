# Registers as a callable function for the game orchestration queue to use
print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from typing import Any, Callable

from backend.core.utils.responses import error_response, success_response
from backend.core.utils.validation import require_keys
from backend.core.workflow_registry import register_workflow


@register_workflow()
def generate_detailed_monster(
    context: dict, on_update: Callable[[str, dict[str, Any]], None]
) -> dict:
    """Generate detailed monster using AI with progress updates"""

    step = "initializing"
    progress_data = {}

    try:
        from backend.game.monster.card_art import generate_card_art
        from backend.game.monster.generator import (
            generate_ability,
            generate_monster_blueprint,
            generate_monster_persona,
            generate_monster_story,
        )

        # Step 1 - lineage, ecology, and stats (monster saved + announced here)
        step = "creating_blueprint"
        on_update(step, progress_data)
        monster = generate_monster_blueprint()
        progress_data.update({"monster": monster.to_dict()})

        # Step 2 - inner life and social self
        step = "shaping_persona"
        on_update(step, progress_data)
        monster = generate_monster_persona(monster)
        progress_data.update({"monster": monster.to_dict()})

        # Step 3 - description, backstory, appearance
        step = "writing_story"
        on_update(step, progress_data)
        monster = generate_monster_story(monster)
        progress_data.update({"monster": monster.to_dict()})

        # Step 4
        step = "adding_first_ability"
        on_update(step, progress_data)
        ability_1 = generate_ability(monster)
        progress_data.update({"ability_1": ability_1.to_dict()})

        # Step 5
        step = "adding_second_ability"
        on_update(step, progress_data)
        ability_2 = generate_ability(monster)
        progress_data.update({"ability_2": ability_2.to_dict()})

        # Step 6
        step = "creating_card_art"
        on_update(step, progress_data)
        image_path = generate_card_art(monster)
        progress_data.update({"card_art_path": image_path})

        return success_response(progress_data)

    except Exception as e:
        return error_response({'failed_at': step, 'completed_work': progress_data, 'error': str(e)})


@register_workflow()
def evolve_monster(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """
    The home-base evolution ceremony: design the evolved form (the ONLY
    abort point), transform the monster in place (same id - memories,
    chat threads, abilities, party status all survive), stream the
    narration (the frontend follows evolution_text_generation_id), then
    settle persona/prose/abilities with keep-old fallbacks, record the
    permanent memory, and regenerate the card art for the new body.
    """

    workflow_name = 'evolve_monster'
    # "context" should have the following keys:
    required_keys = ["monster_id"]

    step = "initialize_workflow"
    progress_data = {}

    try:
        from backend.game.chat.generator import wait_for_streamed_text
        from backend.game.monster import evolution
        from backend.game.utils import is_image_generation_enabled
        from backend.models.monster import Monster

        # Step 0 - validate keys and eligibility (re-checked here: the
        # queue may run this long after the service said yes)
        step = "validate_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        monster_id = int(context['monster_id'])
        guidance = evolution.clean_guidance(context.get('guidance'))

        from backend.game.monster.evolution_eligibility import evolution_eligibility_error

        eligibility_error = evolution_eligibility_error(monster_id)
        if eligibility_error:
            raise Exception(eligibility_error)

        monster = Monster.get_monster_by_id(monster_id)
        stage = evolution.next_stage_number(monster_id)

        # Step 1 - design the evolved form (nothing is mutated if this fails)
        step = "designing_form"
        on_update(step, progress_data)
        form = evolution.run_form_design(monster, guidance, stage, workflow_name)

        # Step 2 - the transform: lineage row, identity, stats, rarity, heal.
        # Emits monster.updated + monster.evolved (the ceremony trigger).
        step = "applying_form"
        on_update(step, progress_data)
        evolution_row = evolution.apply_evolution_form(monster, form, guidance, stage)
        progress_data.update({"monster": monster.to_dict(), "evolution": evolution_row.to_dict()})
        step = "form_applied"
        on_update(step, progress_data)

        # Step 3 - queue the streamed ceremony text and hand its id over
        step = "queue_narration"
        on_update(step, progress_data)
        narration_id = evolution.queue_evolution_narration(
            monster, evolution_row, guidance, workflow_name
        )
        progress_data.update(
            {"evolution_text_generation_id": narration_id, "monster_id": monster_id}
        )
        step = "emit_generation_id"
        on_update(step, progress_data)

        step = "await_narration"
        on_update(step, progress_data)
        narrative = ''
        try:
            narrative = wait_for_streamed_text(narration_id)
        except Exception as e:
            print(f"❌ Evolution narration failed for {monster.name} - the ceremony continues: {e}")

        # Step 4 - the inner life settles into the new form
        step = "shifting_persona"
        on_update(step, progress_data)
        shift = evolution.run_persona_shift(monster, evolution_row, guidance, workflow_name)
        persona_applied = evolution.apply_persona_shift(monster, shift)

        # Step 5 - new words and the artist's brief
        step = "rewriting_story"
        on_update(step, progress_data)
        prose = evolution.run_prose_rewrite(
            monster,
            evolution_row,
            evolution.build_persona_shift_facts(persona_applied),
            guidance,
            workflow_name,
        )
        art_worthy = evolution.apply_prose(monster, prose)

        # Step 6 - abilities evolve with the body; maybe one signature is earned
        step = "evolving_abilities"
        on_update(step, progress_data)
        decisions = evolution.run_ability_evolution(monster, evolution_row, guidance, workflow_name)
        ability_applied = evolution.apply_ability_evolution(monster, decisions)

        new_ability = None
        if (
            ability_applied['wants_new']
            and ability_applied['theme']
            and len(monster.abilities or []) < evolution.MAX_ABILITIES
        ):
            step = "adding_signature_ability"
            on_update(step, progress_data)
            try:
                from backend.game.monster.generator import generate_ability as make_ability

                new_ability = make_ability(
                    monster,
                    growth_context=(
                        f"Just evolved into {monster.species}: "
                        f"{ability_applied['theme']}. Only this new form can hold it."
                    ),
                )
            except Exception as e:
                print(f"❌ Signature ability failed for {monster.name}: {e}")

        # Step 7 - the evolution becomes part of its story forever
        step = "recording_memory"
        on_update(step, progress_data)
        evolution.finalize_evolution(
            monster,
            evolution_row,
            narrative,
            persona_applied.get('memory_note'),
            {
                'new_ability': new_ability.name if new_ability else None,
                'reworded': ability_applied['reworded'],
            },
        )

        # The party stood witness to its transformation - the bond deepens
        from backend.game.monster.affinity import step_affinity

        step_affinity(monster.id, 'evolved_together')

        # Step 8 - a new face for the new form (old art stays on disk,
        # its path lives in the lineage row). Prose failure skips this so
        # the art never mismatches the appearance block.
        art_regenerated = False
        if art_worthy and is_image_generation_enabled():
            step = "regenerating_art"
            on_update(step, progress_data)
            try:
                from backend.game.monster.card_art import generate_card_art

                generate_card_art(monster)
                art_regenerated = True
            except Exception as e:
                print(f"❌ Card art regen failed for {monster.name} - the old face stands: {e}")

        return success_response(
            {
                "monster_id": monster_id,
                "monster_name": monster.name,
                "monster": monster.to_dict(),
                "evolution": evolution_row.to_dict(),
                "narrative": narrative,
                "new_ability": new_ability.to_dict() if new_ability else None,
                "reworded_abilities": ability_applied['reworded'],
                "art_regenerated": art_regenerated,
            }
        )

    except Exception as e:
        return error_response({'failed_at': step, 'completed_work': progress_data, 'error': str(e)})


@register_workflow()
def generate_ability(context: dict, on_update: Callable[[str, dict[str, Any]], None]) -> dict:
    """Generate detailed monster using AI with progress updates"""

    # "context" should have the following keys:
    required_keys = ["monster_id"]

    # Set the initial conditions
    step = "initializing"
    progress_data = {}

    try:
        from backend.game.monster.generator import generate_ability_by_id

        # Step 0 - validate required keys
        step = "validating_context"
        on_update(step, progress_data)
        require_keys(context, required_keys)

        # Step 1
        step = "generating_ability"
        on_update(step, progress_data)
        ability = generate_ability_by_id(context["monster_id"])
        progress_data.update({"ability": ability.to_dict()})

        return success_response(progress_data)

    except Exception as e:
        return error_response({'failed_at': step, 'completed_work': progress_data, 'error': str(e)})
