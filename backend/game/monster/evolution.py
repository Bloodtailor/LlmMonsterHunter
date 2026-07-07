# Monster Evolution - The Big, Earned Leap
# A following monster is transformed at home base: same monster id
# (memories, chat threads, abilities, party status all survive), new
# form. The LLM designs the evolved form from the monster's lived
# history plus optional player guidance; CODE owns every number.
# Evolution sits OUTSIDE the growth/return lifetime caps - its memory
# kind 'evolved' is invisible to MonsterMemory.growth_total_pct.
#
# Shape of a ceremony (the workflow in registered_workflows.py):
#   run_form_design -> apply_evolution_form   (the only abort point)
#   queue_evolution_narration (streamed)      -> saved as lineage narrative
#   run_persona_shift -> apply_persona_shift  (keep-old on failure)
#   run_prose_rewrite -> apply_prose          (keep-old on failure)
#   run_ability_evolution -> apply_ability_evolution
#   finalize_evolution                        (memory + narrative)
# Invariant: a MonsterEvolution row exists <=> the transform happened.

from typing import Any, Optional

# Stat boost per evolution stage: the leap shrinks as stages stack.
# All four stats climb together; numbers are code-owned.
EVOLUTION_STAGE_BOOSTS = [0.25, 0.15]   # stage 1, stage 2
EVOLUTION_BOOST_FLAT = 0.10             # stage 3 and beyond (unlimited)
EVOLVED_STATS = ('max_health', 'attack', 'defense', 'speed')

GUIDANCE_MAX_CHARS = 200
NAME_ROOT_CHARS = 4          # this prefix of the old first name must survive
BACKSTORY_ADDENDUM_MAX_CHARS = 800
ABILITY_REWORD_CAP = 2
MAX_ABILITIES = 6            # mirrors growth.py
REWORD_MAX_RATIO = 1.15      # mirrors growth.py - evolved words, same power
BATTLE_LINE_MAX_RATIO = 1.3  # mirrors returning.py

# Persona fields evolution may rewrite; everything else is preserved.
# core_wish, secret, grudges_and_bonds, and social_bonds are the
# monster's continuity - the body changes, these do not.
EVOLVABLE_PERSONA_FIELDS = ('battle_line', 'speech_style', 'goals', 'motivations')

NO_GUIDANCE_NOTE = "The player offered no guidance - let its history speak."

# ===== ELIGIBILITY =====

def evolution_eligibility_error(monster_id: int) -> Optional[str]:
    """
    Why this monster cannot evolve right now, or None if it can.
    Evolution happens at home base: any fully-generated monster on the
    following list (the active party is drawn from it) qualifies, but
    never during a dungeon run.
    """
    try:
        from backend.game.dungeon import manager as dungeon
        from backend.models.active_party import ActiveParty
        from backend.models.following_monsters import FollowingMonster
        from backend.models.monster import Monster

        if dungeon.is_in_dungeon():
            return "The party is in the dungeon - evolution waits for home base"

        monster = Monster.get_monster_by_id(int(monster_id))
        if not monster:
            return f"Monster {monster_id} not found"
        if monster.generation_stage != 'complete':
            return f"{monster.name} is still taking shape - try again shortly"

        familiar_ids = set(FollowingMonster.get_following_monster_ids())
        familiar_ids.update(ActiveParty.get_party_monster_ids())
        if int(monster_id) not in familiar_ids:
            return f"{monster.name} is not following the party"

        return None
    except Exception as e:
        return f"Could not check evolution eligibility: {e}"

# ===== CODE-OWNED MECHANICS =====

def next_stage_number(monster_id: int) -> int:
    """The stage the NEXT evolution would be (1-based)"""
    from backend.models.monster_evolution import MonsterEvolution
    return MonsterEvolution.count_for_monster(monster_id) + 1

def boost_pct_for_stage(stage: int) -> float:
    """25% -> 15% -> 10% flat: big leaps early, steady steps forever after"""
    stage = max(1, int(stage))
    if stage <= len(EVOLUTION_STAGE_BOOSTS):
        return EVOLUTION_STAGE_BOOSTS[stage - 1]
    return EVOLUTION_BOOST_FLAT

def next_rarity(current) -> str:
    """One step up the ladder; unknown/missing counts as common; legendary stays"""
    from backend.game.monster.cmdts_data import RARITIES
    cleaned = str(current or '').strip().lower()
    if cleaned not in RARITIES:
        cleaned = 'common'
    return RARITIES[min(RARITIES.index(cleaned) + 1, len(RARITIES) - 1)]

def keep_name_root(old_name: str, proposed) -> str:
    """
    An evolved name must still carry the old one: the first
    NAME_ROOT_CHARS of the old first name have to appear somewhere in
    the proposal (Rokk -> Rokkarath). Anything else keeps the old name.
    """
    old = str(old_name or '').strip()
    new = str(proposed or '').strip()
    if not new or len(new) > 100 or not old:
        return old
    root = old.split()[0][:NAME_ROOT_CHARS].lower()
    return new if root and root in new.lower() else old

def clean_guidance(guidance) -> str:
    """The player's whisper, trimmed to size (empty means pure history)"""
    return str(guidance or '').strip()[:GUIDANCE_MAX_CHARS]

def build_transformation_facts(evolution) -> str:
    """Compact code-built lines every post-form stage reads (no numbers)"""
    lines = [
        f"Old form: {evolution.old_name} the {evolution.old_species}",
        f"New form: {evolution.new_name} the {evolution.new_species}",
        f"Evolution stage: {evolution.stage} | "
        f"Rarity: {evolution.old_rarity or 'common'} -> {evolution.new_rarity}"
    ]
    theme = str((evolution.details or {}).get('form_theme') or '').strip()
    if theme:
        lines.append(f"Essence of the change: {theme}")
    return "\n".join(lines)

# ===== STAGE 1: FORM DESIGN (the only abort point) =====

def run_form_design(monster, guidance: str, stage: int, workflow_name: str) -> dict[str, Any]:
    """
    The one call allowed to fail the whole evolution - nothing has been
    mutated yet, so a parse failure here simply aborts. Raises on failure.
    """
    from backend.game.memory.manager import build_memory_block
    from backend.game.monster.context_builder import build_speaker_block
    from backend.game.utils import build_and_generate

    taxonomy = monster.taxonomy or {}
    locked = f"{taxonomy.get('domain') or 'Unknown'} > {taxonomy.get('kingdom') or 'Unknown'}"
    stage_note = (
        f"This is evolution stage {stage} for this monster. " +
        ("It has evolved before - go further, stranger, more fully itself."
         if stage > 1 else
         "Its first evolution - the form its whole journey has been growing toward.")
    )
    return build_and_generate('evolution_form', workflow_name, {
        'monster_details': build_speaker_block(monster),
        'monster_memories': build_memory_block(monster.id),
        'locked_lineage': locked,
        'stage_note': stage_note,
        'player_guidance': guidance or NO_GUIDANCE_NOTE
    })

def apply_evolution_form(monster, form: dict[str, Any], guidance: str, stage: int):
    """
    Snapshot -> lineage row -> identity + taxonomy + stats + rarity +
    heal, every number clamped in code. Emits monster.updated and
    monster.evolved. Returns the MonsterEvolution row.
    Raises if the lineage row cannot be written (nothing mutated then -
    the row IS the record that a transform happened).
    """
    from backend.core.events.monster_events import emit_monster_evolved, emit_monster_updated
    from backend.game.monster.cmdts_data import SIZE_CLASSES, normalize_choice
    from backend.models.monster_evolution import MonsterEvolution

    new_species = str(form.get('species') or '').strip()[:100] or f"Evolved {monster.species}"[:100]
    new_name = keep_name_root(monster.name, form.get('evolved_name'))
    form_theme = str(form.get('form_theme') or '').strip()[:200]
    boost_pct = boost_pct_for_stage(stage)

    ecology = dict(monster.ecology or {})
    old_size = ecology.get('size_class') or 'medium'
    new_size = normalize_choice(form.get('size_class'), SIZE_CLASSES, old_size)

    details = {'form_theme': form_theme or None}
    if new_size != old_size:
        details['size_class'] = {'from': old_size, 'to': new_size}

    evolution = MonsterEvolution.add(
        monster_id=monster.id,
        stage=stage,
        old_name=monster.name,
        old_species=monster.species,
        old_rarity=monster.rarity,
        new_name=new_name,
        new_species=new_species,
        new_rarity=next_rarity(monster.rarity),
        old_stats={stat: getattr(monster, stat) or 0 for stat in EVOLVED_STATS},
        applied_boost_pct=boost_pct,
        old_card_art_path=monster.card_art_path,
        guidance=guidance or None,
        details=details
    )
    if not evolution:
        raise RuntimeError(f"Could not record the evolution of {monster.name} - transform aborted")

    # Identity: name root kept, species mirrored into the taxonomy.
    # Curated domain/kingdom and the derived type_label never move;
    # the invented lineage below them may.
    monster.name = new_name
    monster.species = new_species
    taxonomy = dict(monster.taxonomy or {})
    taxonomy['species'] = new_species
    for field, cap in (('family', 100), ('genus', 100), ('race_label', 50)):
        value = str(form.get(field) or '').strip()[:cap]
        if value:
            taxonomy[field] = value
    monster.taxonomy = taxonomy

    if new_size != old_size:
        ecology['size_class'] = new_size
        monster.ecology = ecology

    # The leap itself: all four stats together, then a fresh body
    for stat in EVOLVED_STATS:
        old_value = getattr(monster, stat) or 0
        setattr(monster, stat, max(old_value + 1, round(old_value * (1 + boost_pct))))
    monster.current_health = monster.max_health
    monster.rarity = evolution.new_rarity
    monster.save()

    emit_monster_updated(monster.to_dict())
    emit_monster_evolved(monster.to_dict(), evolution.to_dict())
    return evolution

# ===== STAGE 2: STREAMED NARRATION (the ceremony text) =====

def queue_evolution_narration(monster, evolution, guidance: str, workflow_name: str) -> int:
    """
    Queue the streamed transformation scene (the monster is already in
    its new form; the facts block carries what it left behind).
    Returns the generation id the frontend streams from.
    """
    from backend.game.memory.manager import build_memory_block
    from backend.game.monster.context_builder import build_speaker_block
    from backend.game.utils import build_and_stream

    return build_and_stream('evolution_narration', workflow_name, {
        'monster_details': build_speaker_block(monster),
        'monster_memories': build_memory_block(monster.id),
        'transformation_facts': build_transformation_facts(evolution),
        'player_guidance': guidance or NO_GUIDANCE_NOTE
    })

# ===== STAGE 3: PERSONA SHIFT =====

def run_persona_shift(monster, evolution, guidance: str, workflow_name: str) -> Optional[dict[str, Any]]:
    """One LLM call: how the inner life shifts with the body. None on failure."""
    from backend.game.monster.context_builder import build_speaker_block
    from backend.game.utils import build_and_generate

    try:
        return build_and_generate('evolution_persona', workflow_name, {
            'monster_details': build_speaker_block(monster),
            'transformation_facts': build_transformation_facts(evolution),
            'player_guidance': guidance or NO_GUIDANCE_NOTE
        })
    except Exception as e:
        print(f"❌ Evolution persona shift failed for {monster.name} - inner life keeps its old shape: {e}")
        return None

def apply_persona_shift(monster, shift: Optional[dict[str, Any]]) -> dict[str, Any]:
    """
    Apply the shift with every rule enforced in code. Only
    EVOLVABLE_PERSONA_FIELDS are ever written - core_wish, secret,
    grudges_and_bonds, and social_bonds are untouchable by design.
    Returns {'memory_note': str, 'changed': {field: new_value}}.
    """
    from backend.core.events.monster_events import emit_monster_updated

    applied = {'memory_note': '', 'changed': {}}
    if not shift:
        return applied

    persona = dict(monster.persona or {})

    new_line = str(shift.get('battle_line') or '').strip()
    old_line = str(persona.get('battle_line') or '')
    if new_line and (not old_line or len(new_line) <= int(max(len(old_line), 60) * BATTLE_LINE_MAX_RATIO)):
        persona['battle_line'] = new_line
        applied['changed']['battle_line'] = new_line

    speech = str(shift.get('speech_style') or '').strip()[:200]
    if speech:
        persona['speech_style'] = speech
        applied['changed']['speech_style'] = speech

    goals = shift.get('goals')
    if isinstance(goals, str):
        goals = [part.strip() for part in goals.split(',') if part.strip()]
    if isinstance(goals, list):
        goals = [str(goal).strip()[:120] for goal in goals if str(goal).strip()][:4]
        if goals:
            persona['goals'] = goals
            applied['changed']['goals'] = goals

    motivations = str(shift.get('motivations') or '').strip()[:300]
    if motivations:
        persona['motivations'] = motivations
        applied['changed']['motivations'] = motivations

    applied['memory_note'] = str(shift.get('memory_note') or '').strip()

    if applied['changed']:
        monster.persona = persona
        monster.save()
        emit_monster_updated(monster.to_dict())
    return applied

def build_persona_shift_facts(applied_shift: dict[str, Any]) -> str:
    """The persona changes as compact lines for the prose stage"""
    labels = {
        'battle_line': 'New battle cry',
        'speech_style': 'New voice',
        'goals': 'New goals',
        'motivations': 'What drives it now'
    }
    lines = []
    for field, value in (applied_shift.get('changed') or {}).items():
        rendered = ", ".join(value) if isinstance(value, list) else str(value)
        lines.append(f"{labels.get(field, field)}: {rendered}")
    return "\n".join(lines) or "Its inner life kept its old shape - the body did all the changing."

# ===== STAGE 4: PROSE + APPEARANCE =====

def run_prose_rewrite(monster, evolution, persona_shift_facts: str, guidance: str,
                      workflow_name: str) -> Optional[dict[str, Any]]:
    """One LLM call: new description, a backstory chapter, the new look. None on failure."""
    from backend.game.monster.context_builder import build_speaker_block
    from backend.game.utils import build_and_generate

    old_visual = str((monster.appearance or {}).get('visual_description') or '').strip() \
        or monster.description
    try:
        return build_and_generate('evolution_prose', workflow_name, {
            'monster_details': build_speaker_block(monster),
            'transformation_facts': build_transformation_facts(evolution),
            'persona_shift_facts': persona_shift_facts,
            'old_visual_description': old_visual,
            'player_guidance': guidance or NO_GUIDANCE_NOTE
        })
    except Exception as e:
        print(f"❌ Evolution prose failed for {monster.name} - old words stand, art stays: {e}")
        return None

def apply_prose(monster, prose: Optional[dict[str, Any]]) -> bool:
    """
    Description is replaced, the backstory gains a chapter (never
    rewritten), the appearance block is rebuilt for the card artist.
    Returns whether the appearance changed - the art-regen gate.
    """
    from backend.core.events.monster_events import emit_monster_updated

    if not prose:
        return False

    changed = False
    description = str(prose.get('description') or '').strip()
    if description:
        monster.description = description
        changed = True

    addendum = str(prose.get('backstory_addendum') or '').strip()[:BACKSTORY_ADDENDUM_MAX_CHARS]
    if addendum:
        old_backstory = str(monster.backstory or '').rstrip()
        monster.backstory = f"{old_backstory}\n\n{addendum}".strip()
        changed = True

    appearance_changed = False
    visual = str(prose.get('visual_description') or '').strip()
    if visual:
        appearance = dict(monster.appearance or {})
        appearance['visual_description'] = visual
        for field, item_cap in (('primary_colors', 40), ('distinguishing_features', 120)):
            value = prose.get(field)
            if isinstance(value, str):
                value = [part.strip() for part in value.split(',') if part.strip()]
            if isinstance(value, list):
                value = [str(item).strip()[:item_cap] for item in value if str(item).strip()][:5]
                if value:
                    appearance[field] = value
        monster.appearance = appearance
        appearance_changed = True
        changed = True

    if changed:
        monster.save()
        emit_monster_updated(monster.to_dict())
    return appearance_changed

# ===== STAGE 5: ABILITY EVOLUTION =====

def run_ability_evolution(monster, evolution, guidance: str, workflow_name: str) -> Optional[dict[str, Any]]:
    """One LLM call: which abilities evolve with the body. None on failure."""
    from backend.game.monster.context_builder import build_speaker_block
    from backend.game.utils import build_and_generate

    abilities_text = "\n".join(
        f"{index + 1}. {ability.name}: {ability.description}"
        for index, ability in enumerate(monster.abilities or [])
    ) or "It has no abilities yet."
    try:
        return build_and_generate('evolution_abilities', workflow_name, {
            'monster_details': build_speaker_block(monster),
            'transformation_facts': build_transformation_facts(evolution),
            'existing_abilities_text': abilities_text,
            'player_guidance': guidance or NO_GUIDANCE_NOTE
        })
    except Exception as e:
        print(f"❌ Evolution ability pass failed for {monster.name} - abilities keep their old words: {e}")
        return None

def apply_ability_evolution(monster, decisions: Optional[dict[str, Any]]) -> dict[str, Any]:
    """
    Up to ABILITY_REWORD_CAP existing abilities may be renamed and
    reworded (same power, evolved expression, length-capped). Whether a
    NEW signature ability is earned is returned for the workflow to act
    on (it owns the generate_ability call and the 6-ability cap).
    Returns {'reworded': [names], 'wants_new': bool, 'theme': str}.
    """
    from backend.core.events.monster_events import emit_monster_updated

    applied = {'reworded': [], 'wants_new': False, 'theme': ''}
    if not decisions:
        return applied

    for slot in range(1, ABILITY_REWORD_CAP + 1):
        target_name = str(decisions.get(f'reword_{slot}') or '').strip().lower()
        new_description = str(decisions.get(f'reword_{slot}_description') or '').strip()
        if not target_name or target_name in ('none', 'null') or not new_description:
            continue
        target = next(
            (a for a in (monster.abilities or []) if a.name.strip().lower() == target_name),
            None
        )
        if not target or target.name in applied['reworded']:
            continue
        if len(new_description) > int(len(target.description or '') * REWORD_MAX_RATIO):
            continue
        new_name = str(decisions.get(f'reword_{slot}_new_name') or '').strip()
        if new_name and new_name.lower() not in ('none', 'null') and len(new_name) <= 100:
            target.name = new_name
        target.description = new_description
        target.save()
        applied['reworded'].append(target.name)

    applied['wants_new'] = str(decisions.get('new_ability', '')).strip().lower() in ('yes', 'true')
    applied['theme'] = str(decisions.get('ability_theme') or '').strip()

    if applied['reworded']:
        emit_monster_updated(monster.to_dict())
    return applied

# ===== FINALE: THE EVOLUTION BECOMES A MEMORY =====

def finalize_evolution(monster, evolution, narrative: str, memory_note: str,
                       applied: dict[str, Any]) -> None:
    """
    Save the ceremony text to the lineage row and make the evolution a
    permanent memory. The memory's details deliberately carry NO 'stat'
    key growth_total_pct could match - and its kind is invisible to the
    caps anyway. Never raises.
    """
    from backend.game.memory.manager import write_memory

    try:
        details = dict(evolution.details or {})
        if applied.get('new_ability'):
            details['new_ability'] = applied['new_ability']
        if applied.get('reworded'):
            details['reworded'] = applied['reworded']
        evolution.details = details or None
        if str(narrative or '').strip():
            evolution.narrative = str(narrative).strip()
        evolution.save()
    except Exception as e:
        print(f"❌ Could not finish the lineage record for {monster.name}: {e}")

    note = str(memory_note or '').strip() or (
        f"Evolved from {evolution.old_name} the {evolution.old_species} "
        f"into {evolution.new_name} the {evolution.new_species}."
    )
    write_memory(monster.id, 'evolved', note, {
        'stage': evolution.stage,
        'old_name': evolution.old_name,
        'old_species': evolution.old_species,
        'amount_pct': evolution.applied_boost_pct,
        'new_ability': applied.get('new_ability'),
        'reworded': applied.get('reworded') or []
    })
