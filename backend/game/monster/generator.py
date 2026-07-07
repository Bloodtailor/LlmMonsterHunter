# Monster Generator - STAGED: facts -> persona -> prose
# Each stage is a small LLM call conditioned on the stages before it, so the
# backstory can never contradict the taxonomy. The monster row is saved after
# the blueprint stage and progressively filled in (generation_stage:
# blueprint -> persona -> complete), emitting events the frontend streams.
# Normalization here guards LLM output, not our own code.

import random

from backend.core.events import (
    emit_monster_ability_added,
    emit_monster_created,
    emit_monster_updated,
)
from backend.game.monster import cmdts_data
from backend.game.utils import build_and_generate
from backend.models.ability import Ability
from backend.models.monster import Monster

WILDS_LOCATION_CONTEXT = "The untamed wilds of the realm, far from any charted place"

# ===== PUBLIC ENTRY POINTS (signatures stable for workflows) =====


def generate_base_monster():
    """Generate a complete monster of the open wilds (all stages)"""
    return _generate_monster_chain(WILDS_LOCATION_CONTEXT)


def generate_contextual_monster(location: dict):
    """Generate a complete monster that belongs to a specific dungeon
    location (and to the active expedition's theme, when a run is on)"""
    from backend.game.dungeon.run_context import themed_location_context

    return _generate_monster_chain(themed_location_context(location))


def _generate_monster_chain(location_context: str):
    monster = generate_monster_blueprint(location_context)
    monster = generate_monster_persona(monster)
    monster = generate_monster_story(monster, location_context)
    return monster


# ===== STAGE 1: BLUEPRINT (identity + ecology facts, code-derived stats) =====


def generate_monster_blueprint(location_context: str = WILDS_LOCATION_CONTEXT) -> Monster:
    """Stages A1+A2: lineage, role, and way of life. Saves the monster
    (generation_stage='blueprint') and announces it to the game world."""

    rarity = cmdts_data.roll_rarity()

    identity_raw = build_and_generate(
        'monster_blueprint_identity',
        'monster_generation',
        {
            'location_context': location_context,
            'rarity': rarity,
            'taxonomy_options': cmdts_data.taxonomy_options_text(),
            'role_options': cmdts_data.options_line(cmdts_data.PARTY_ROLES),
            'size_options': cmdts_data.options_line(cmdts_data.SIZE_CLASSES),
            'lifecycle_options': cmdts_data.options_line(cmdts_data.LIFECYCLE_STAGES),
            'creation_options': cmdts_data.options_line(cmdts_data.CREATION_MECHANISMS),
        },
    )
    identity = _normalize_identity(identity_raw)

    ecology_raw = build_and_generate(
        'monster_blueprint_ecology',
        'monster_generation',
        {
            'location_context': location_context,
            'identity_facts': _identity_facts_text(identity, rarity),
            'habitat_options': cmdts_data.options_line(cmdts_data.HABITAT_DOMAINS),
            'biome_options': cmdts_data.options_line(cmdts_data.BIOMES),
            'social_options': cmdts_data.options_line(cmdts_data.SOCIAL_STRUCTURES),
            'sustenance_options': cmdts_data.options_line(cmdts_data.SUSTENANCE_SOURCES),
            'feeding_options': cmdts_data.options_line(cmdts_data.FEEDING_STYLES),
            'sapience_options': cmdts_data.options_line(cmdts_data.SAPIENCE_LEVELS),
            'communication_options': cmdts_data.options_line(cmdts_data.COMMUNICATION_MODES),
            'element_options': cmdts_data.options_line(cmdts_data.ELEMENTS),
            'activity_options': cmdts_data.options_line(cmdts_data.ACTIVITY_CYCLES),
            'class_domain_options_line': cmdts_data.options_line(list(cmdts_data.CLASS_DOMAINS)),
            'class_domain_options': cmdts_data.class_domain_options_text(),
        },
    )
    ecology, class_taxonomy = _normalize_ecology(ecology_raw, identity)

    stats = cmdts_data.derive_stats(identity['party_role'], rarity, identity['size_class'])

    monster = Monster(
        name=identity['name'],
        species=identity['species'],
        # Stub prose until the story stage fills it in
        description=f"A {identity['size_class']} {identity['kingdom'].lower()} creature, newly encountered.",
        backstory=None,
        max_health=stats['health'],
        current_health=stats['health'],
        attack=stats['attack'],
        defense=stats['defense'],
        speed=stats['speed'],
        personality_traits=[],
        rarity=rarity,
        party_role=identity['party_role'],
        generation_stage='blueprint',
        taxonomy=identity['taxonomy'],
        class_taxonomy=class_taxonomy,
        ecology=ecology,
        persona=None,
        appearance=None,
        card_art_path=None,
    )
    monster.save()

    # Reload with relationships, then announce
    monster = Monster.get_monster_by_id(monster.id)
    emit_monster_created(monster.to_dict())

    return monster


# ===== STAGE 2: PERSONA (inner life + social self) =====


def generate_monster_persona(monster: Monster) -> Monster:
    """Stages B+C: wish/fears/secret, then traits/tastes/voice.
    Advances generation_stage to 'persona'."""

    facts = _monster_facts_text(monster)

    inner = build_and_generate('monster_inner_life', 'monster_generation', {'monster_facts': facts})

    social = build_and_generate(
        'monster_social_self',
        'monster_generation',
        {'monster_facts': facts, 'inner_life_facts': _inner_life_facts_text(inner)},
    )

    monster.persona = _assemble_persona(inner, social)
    monster.personality_traits = _clean_list(social.get('personality_traits'), ['mysterious'])[:5]
    monster.generation_stage = 'persona'
    monster.save()

    emit_monster_updated(monster.to_dict())
    return monster


# ===== STAGE 3: STORY (description, backstory, structured appearance) =====


def generate_monster_story(
    monster: Monster, location_context: str = WILDS_LOCATION_CONTEXT
) -> Monster:
    """Stage D: the finished prose, conditioned on every fact so far.
    Advances generation_stage to 'complete'."""

    creative = build_and_generate(
        'monster_creative_text',
        'monster_generation',
        {
            'location_context': location_context,
            'monster_facts': _monster_facts_text(monster),
            'persona_facts': _persona_facts_text(monster.persona or {}),
        },
    )

    monster.description = _clean_str(creative.get('description'), monster.description)
    monster.backstory = _clean_str(creative.get('backstory'), '') or None
    monster.appearance = {
        'visual_description': _clean_str(creative.get('visual_description'), monster.description),
        'primary_colors': _clean_list(creative.get('primary_colors'), []),
        'distinguishing_features': _clean_list(creative.get('distinguishing_features'), []),
    }
    monster.generation_stage = 'complete'
    monster.save()

    emit_monster_updated(monster.to_dict())
    return monster


# ===== ABILITIES AND CARD ART (signatures unchanged) =====


# Card art (generation + prompt composition) lives in card_art.py -
# art is a bonus, never a blocker


def generate_ability(monster: Monster, growth_context: str = ''):

    variables = _build_ability_variables(monster, growth_context)
    parsed_data = build_and_generate('generate_ability', 'ability_generation', variables)

    ability = Ability.create_from_llm_data(monster.id, parsed_data)
    ability.save()

    # The monster has a new ability
    emit_monster_ability_added(monster.id, ability.to_dict())

    return ability


def generate_ability_by_id(monster_id):
    monster = Monster.query.get(monster_id)
    return generate_ability(monster)


def _build_ability_variables(monster: Monster, growth_context: str = ''):

    # Format existing abilities
    existing_abilities = monster.abilities
    abilities_text = (
        "\n".join(
            [
                f"- {ability.name} ({ability.ability_type}): {ability.description}"
                for ability in existing_abilities
            ]
        )
        if existing_abilities
        else "None (this will be their first ability)"
    )

    persona = monster.persona or {}
    ecology = monster.ecology or {}

    # Growth/return abilities carry the WHY into the prompt; ordinary
    # generation leaves this block empty
    growth_block = (
        f"\n--- Why this ability is being learned NOW ---\n{growth_context}\n"
        if growth_context
        else ''
    )

    return {
        'growth_context': growth_block,
        'monster_name': monster.name,
        'monster_species': monster.species,
        'monster_description': monster.description,
        'monster_backstory': monster.backstory,
        'monster_health': monster.max_health,
        'monster_attack': monster.attack,
        'monster_defense': monster.defense,
        'monster_speed': monster.speed,
        'monster_personality': ', '.join(monster.personality_traits or []),
        'monster_role': monster.party_role or 'unknown',
        'monster_class': _class_text(monster.class_taxonomy),
        'monster_elements': ', '.join(ecology.get('elemental_affinities') or []) or 'none',
        'monster_wish': persona.get('core_wish', 'unknown'),
        'existing_abilities_text': abilities_text,
        'ability_count': len(monster.abilities),
    }


# ===== NORMALIZATION (snap LLM output onto curated data) =====


def _clean_str(value, default, max_length=None):
    if isinstance(value, str) and value.strip():
        cleaned = value.strip()
        return cleaned[:max_length] if max_length else cleaned
    return default


def _clean_list(value, default):
    if isinstance(value, str) and value.strip():
        value = [part.strip() for part in value.split(',')]
    if isinstance(value, list):
        cleaned = [item.strip() for item in value if isinstance(item, str) and item.strip()]
        if cleaned:
            return cleaned
    return default


def _normalize_identity(data: dict) -> dict:
    domain, kingdom = cmdts_data.normalize_taxonomy_pick(data.get('domain'), data.get('kingdom'))
    species = _clean_str(data.get('species'), f"{kingdom} of {domain}", 100)

    return {
        'name': _clean_str(data.get('name'), 'Unnamed Monster', 100),
        'species': species,
        'kingdom': kingdom,
        'party_role': cmdts_data.normalize_choice(
            data.get('party_role'), cmdts_data.PARTY_ROLES, random.choice(cmdts_data.PARTY_ROLES)
        ),
        'size_class': cmdts_data.normalize_choice(
            data.get('size_class'), cmdts_data.SIZE_CLASSES, 'medium'
        ),
        'lifecycle_stage': cmdts_data.normalize_choice(
            data.get('lifecycle_stage'), cmdts_data.LIFECYCLE_STAGES, 'adult'
        ),
        'creation_mechanism': cmdts_data.normalize_choice(
            data.get('creation_mechanism'), cmdts_data.CREATION_MECHANISMS, 'born'
        ),
        'taxonomy': {
            'domain': domain,
            'kingdom': kingdom,
            'family': _clean_str(data.get('family'), 'Uncharted Lineage', 100),
            'genus': _clean_str(data.get('genus'), 'Unnamed Breed', 100),
            'species': species,
            'type_label': kingdom,  # display label derived, never LLM-invented
            'race_label': _clean_str(data.get('race_label'), kingdom, 50),
        },
    }


def _normalize_ecology(data: dict, identity: dict) -> tuple:
    """Returns (ecology_json, class_taxonomy_json)"""

    sustenance = cmdts_data.normalize_multi(
        data.get('sustenance'), cmdts_data.SUSTENANCE_SOURCES, ['matter']
    )
    sapience = cmdts_data.normalize_choice(
        data.get('sapience'), cmdts_data.SAPIENCE_LEVELS, 'sapient'
    )
    default_communication = ['speech'] if sapience in ('sapient', 'erudite') else ['none']

    ecology = {
        'size_class': identity['size_class'],
        'lifecycle_stage': identity['lifecycle_stage'],
        'creation_mechanism': identity['creation_mechanism'],
        'habitat': {
            'primary': cmdts_data.normalize_choice(
                data.get('habitat_primary'), cmdts_data.HABITAT_DOMAINS, 'land'
            ),
            'secondary': cmdts_data.normalize_multi(
                data.get('habitat_secondary'), cmdts_data.HABITAT_DOMAINS, []
            ),
            'biomes': cmdts_data.normalize_multi(data.get('biomes'), cmdts_data.BIOMES, []),
        },
        'social_structure': {
            'primary': cmdts_data.normalize_choice(
                data.get('social_structure'), cmdts_data.SOCIAL_STRUCTURES, 'solitary'
            ),
            'notes': _clean_str(data.get('social_notes'), ''),
        },
        'diet': {
            'feeds': sustenance != ['none'],
            'sustenance': sustenance,
            'feeding_style': cmdts_data.normalize_choice(
                data.get('feeding_style'),
                cmdts_data.FEEDING_STYLES,
                'omnivore' if 'matter' in sustenance else 'none',
            ),
            'notes': _clean_str(data.get('diet_notes'), ''),
        },
        'sapience': sapience,
        'communication': cmdts_data.normalize_multi(
            data.get('communication'), cmdts_data.COMMUNICATION_MODES, default_communication
        ),
        'elemental_affinities': cmdts_data.normalize_multi(
            data.get('elements'), cmdts_data.ELEMENTS, []
        ),
        'activity_cycle': cmdts_data.normalize_choice(
            data.get('activity_cycle'), cmdts_data.ACTIVITY_CYCLES, 'diurnal'
        ),
    }

    class_domain = cmdts_data.normalize_choice(
        data.get('class_domain'), list(cmdts_data.CLASS_DOMAINS), None
    )
    class_taxonomy = []
    if class_domain:
        class_taxonomy.append(
            {
                'domain': class_domain,
                'discipline': _clean_str(data.get('class_discipline'), ''),
                'specialization': _clean_str(data.get('class_specialization'), ''),
            }
        )

    return ecology, class_taxonomy


def _assemble_persona(inner: dict, social: dict) -> dict:
    return {
        'core_wish': _clean_str(inner.get('core_wish'), 'To find its place in the world'),
        'motivations': _clean_str(inner.get('motivations'), ''),
        'goals': _clean_list(inner.get('goals'), []),
        'beliefs': _clean_str(inner.get('beliefs'), ''),
        'moral_character': _clean_str(inner.get('moral_character'), ''),
        'fears': _clean_list(inner.get('fears'), []),
        'secret': _clean_str(inner.get('secret'), ''),
        'likes': _clean_list(social.get('likes'), []),
        'dislikes': _clean_list(social.get('dislikes'), []),
        'hobbies': _clean_list(social.get('hobbies'), []),
        'profession': _clean_str(social.get('profession'), ''),
        'attitude_toward_strangers': _clean_str(social.get('attitude_toward_strangers'), ''),
        'responds_well_to': _clean_list(social.get('responds_well_to'), []),
        'responds_poorly_to': _clean_list(social.get('responds_poorly_to'), []),
        'recruitment_lever': _clean_str(social.get('recruitment_lever'), ''),
        'social_bonds': {
            'drawn_to': _clean_str(social.get('drawn_to'), ''),
            'clashes_with': _clean_str(social.get('clashes_with'), ''),
        },
        'speech_style': _clean_str(social.get('speech_style'), ''),
        'battle_line': _clean_str(social.get('battle_line'), ''),
    }


# ===== FACTS TEXT (compact context blocks passed between stages) =====


def _identity_facts_text(identity: dict, rarity: str) -> str:
    taxonomy = identity['taxonomy']
    return (
        f"Name: {identity['name']}\n"
        f"Lineage: {taxonomy['domain']} > {taxonomy['kingdom']} > {taxonomy['family']} > "
        f"{taxonomy['genus']} > {taxonomy['species']} (a {taxonomy['race_label']})\n"
        f"Rarity: {rarity} | Party role: {identity['party_role']} | Size: {identity['size_class']} | "
        f"Lifecycle: {identity['lifecycle_stage']} | Came to be: {identity['creation_mechanism']}"
    )


def _monster_facts_text(monster: Monster) -> str:
    """Every established fact about a blueprinted monster, as prompt context
    for the persona and story stages"""

    taxonomy = monster.taxonomy or {}
    ecology = monster.ecology or {}
    habitat = ecology.get('habitat', {})
    social = ecology.get('social_structure', {})
    diet = ecology.get('diet', {})

    biomes = ", ".join(habitat.get('biomes') or []) or 'unknown'
    lines = [
        f"Name: {monster.name}",
        f"Lineage: {taxonomy.get('domain')} > {taxonomy.get('kingdom')} > {taxonomy.get('family')} > "
        f"{taxonomy.get('genus')} > {taxonomy.get('species')} (a {taxonomy.get('race_label')})",
        f"Rarity: {monster.rarity} | Party role: {monster.party_role} | Size: {ecology.get('size_class')} | "
        f"Lifecycle: {ecology.get('lifecycle_stage')} | Came to be: {ecology.get('creation_mechanism')}",
        f"Habitat: {habitat.get('primary')} (biomes: {biomes})",
        f"Social life: {social.get('primary')}"
        + (f" - {social.get('notes')}" if social.get('notes') else ""),
        f"Diet: {diet.get('feeding_style')}"
        + (f" ({diet.get('notes')})" if diet.get('notes') else "")
        + f", sustained by {', '.join(diet.get('sustenance') or [])}",
        f"Mind: {ecology.get('sapience')} | Communicates by: {', '.join(ecology.get('communication') or [])}",
        f"Elemental affinities: {', '.join(ecology.get('elemental_affinities') or []) or 'none'}",
        f"Trained class: {_class_text(monster.class_taxonomy)}",
        f"Active: {ecology.get('activity_cycle')}",
    ]
    return "\n".join(lines)


def _inner_life_facts_text(inner: dict) -> str:
    goals = ", ".join(_clean_list(inner.get('goals'), [])) or 'none stated'
    fears = ", ".join(_clean_list(inner.get('fears'), [])) or 'none stated'
    return (
        f"Core wish: {inner.get('core_wish')}\n"
        f"Motivations: {inner.get('motivations')}\n"
        f"Goals: {goals}\n"
        f"Beliefs: {inner.get('beliefs')}\n"
        f"Moral character: {inner.get('moral_character')}\n"
        f"Fears: {fears}\n"
        f"Secret (shapes the outward mask, never shown openly): {inner.get('secret')}"
    )


def _persona_facts_text(persona: dict) -> str:
    """Persona context for the story stage. The SECRET is deliberately
    excluded - backstory text is player-visible, and secrets are only
    discovered through earned trust in conversation."""

    fears = ", ".join(persona.get('fears') or []) or 'none stated'
    likes = ", ".join(persona.get('likes') or []) or 'unknown'
    dislikes = ", ".join(persona.get('dislikes') or []) or 'unknown'
    return (
        f"Core wish: {persona.get('core_wish')}\n"
        f"Moral character: {persona.get('moral_character')}\n"
        f"Beliefs: {persona.get('beliefs')}\n"
        f"Profession (self-identity): {persona.get('profession')}\n"
        f"Attitude toward strangers: {persona.get('attitude_toward_strangers')}\n"
        f"Likes: {likes} | Dislikes: {dislikes}\n"
        f"Fears: {fears}\n"
        f"Speech style: {persona.get('speech_style')}"
    )


def _class_text(class_taxonomy) -> str:
    if not class_taxonomy:
        return 'untrained'
    parts = []
    for entry in class_taxonomy:
        chain = " > ".join(
            p
            for p in (entry.get('domain'), entry.get('discipline'), entry.get('specialization'))
            if p
        )
        parts.append(chain)
    return "; ".join(parts)
