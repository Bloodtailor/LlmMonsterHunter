# Player Character Creation - the player's answers become a monster row
# Staged like monster generation (blueprint -> persona -> story), but
# every stage is CONDITIONED ON THE PLAYER'S OWN ANSWERS - the LLM
# translates and expands, it never overrides. The player's appearance
# text is kept VERBATIM as appearance.visual_description (it is the
# portrait brief), and their wish IS persona.core_wish, word for word.
#
# Code owns the numbers: rarity is fixed at 'common' (an ordinary
# dreamer walking into the deep - growth raises them), the role is a
# static player pick, and stats come from cmdts_data.derive_stats.

from backend.core.events import emit_monster_created, emit_monster_updated
from backend.game.monster import cmdts_data
from backend.game.player.manager import set_player_monster
from backend.game.player.options import choices_so_far_text
from backend.game.utils import build_and_generate
from backend.models.monster import Monster

# The player character's rarity, forever (locked decision,
# docs/plans/new-game-experience.md) - power is EARNED through growth
PLAYER_RARITY = 'common'

# A player-authored character keeps no LLM-invented secret, and needs
# no recruitment lever - those persona fields exist for monsters the
# party must win over
_PERSONA_DEFAULTS = {'secret': '', 'recruitment_lever': ''}


def create_player_blueprint(choices: dict[str, str]) -> Monster:
    """Stage 1: place the player's chosen kind on the curated taxonomy,
    derive stats, save the row, set the player pointer, announce it."""

    placement_raw = build_and_generate(
        'player_blueprint',
        'player_generation',
        {
            'choices_so_far': choices_so_far_text(choices),
            'taxonomy_options': cmdts_data.taxonomy_options_text(),
            'size_options': cmdts_data.options_line(cmdts_data.SIZE_CLASSES),
            'lifecycle_options': cmdts_data.options_line(cmdts_data.LIFECYCLE_STAGES),
            'creation_options': cmdts_data.options_line(cmdts_data.CREATION_MECHANISMS),
        },
    )

    domain, kingdom = cmdts_data.normalize_taxonomy_pick(
        placement_raw.get('domain'), placement_raw.get('kingdom')
    )
    species = _clean_str(placement_raw.get('species'), choices.get('kind', 'Adventurer'), 100)
    size_class = cmdts_data.normalize_choice(
        placement_raw.get('size_class'), cmdts_data.SIZE_CLASSES, 'medium'
    )
    role = cmdts_data.normalize_choice(choices.get('role'), cmdts_data.PARTY_ROLES, 'striker')
    stats = cmdts_data.derive_stats(role, PLAYER_RARITY, size_class)

    ecology = {
        'size_class': size_class,
        'lifecycle_stage': cmdts_data.normalize_choice(
            placement_raw.get('lifecycle_stage'), cmdts_data.LIFECYCLE_STAGES, 'adult'
        ),
        'creation_mechanism': cmdts_data.normalize_choice(
            placement_raw.get('creation_mechanism'), cmdts_data.CREATION_MECHANISMS, 'born'
        ),
        # The player speaks for themself - chat gating must never bite
        'sapience': 'sapient',
        'communication': ['speech'],
    }

    monster = Monster(
        name=choices['name'],
        species=species,
        description=f"{choices['name']}, {choices.get('kind', 'an adventurer')} - the adventurer themself.",
        backstory=None,
        max_health=stats['health'],
        current_health=stats['health'],
        attack=stats['attack'],
        defense=stats['defense'],
        speed=stats['speed'],
        personality_traits=[],
        rarity=PLAYER_RARITY,
        party_role=role,
        generation_stage='blueprint',
        taxonomy={
            'domain': domain,
            'kingdom': kingdom,
            'family': _clean_str(placement_raw.get('family'), 'Wandering Line', 100),
            'genus': _clean_str(placement_raw.get('genus'), 'Dreamer', 100),
            'species': species,
            'type_label': kingdom,
            'race_label': _clean_str(placement_raw.get('race_label'), kingdom, 50),
        },
        class_taxonomy=[],
        ecology=ecology,
        persona=None,
        appearance=None,
        card_art_path=None,
    )
    monster.save()
    set_player_monster(monster.id)

    monster = Monster.get_monster_by_id(monster.id)
    emit_monster_created(monster.to_dict())
    return monster


def create_player_persona(monster: Monster, choices: dict[str, str]) -> Monster:
    """Stage 2: expand the player's personality/wish/background answers
    into the full persona. Their wish becomes core_wish VERBATIM."""

    expanded = build_and_generate(
        'player_persona',
        'player_generation',
        {
            'choices_so_far': choices_so_far_text(choices),
            'blueprint_facts': _blueprint_facts_text(monster),
        },
    )

    monster.persona = {
        'core_wish': choices.get('wish') or 'To claim the wish that sleeps below',
        'motivations': _clean_str(expanded.get('motivations'), ''),
        'goals': _clean_list(expanded.get('goals'), []),
        'beliefs': _clean_str(expanded.get('beliefs'), ''),
        'moral_character': _clean_str(expanded.get('moral_character'), ''),
        'fears': _clean_list(expanded.get('fears'), []),
        'likes': _clean_list(expanded.get('likes'), []),
        'dislikes': _clean_list(expanded.get('dislikes'), []),
        'hobbies': _clean_list(expanded.get('hobbies'), []),
        'profession': _clean_str(expanded.get('profession'), ''),
        'attitude_toward_strangers': _clean_str(expanded.get('attitude_toward_strangers'), ''),
        'responds_well_to': _clean_list(expanded.get('responds_well_to'), []),
        'responds_poorly_to': _clean_list(expanded.get('responds_poorly_to'), []),
        'social_bonds': {
            'drawn_to': _clean_str(expanded.get('drawn_to'), ''),
            'clashes_with': _clean_str(expanded.get('clashes_with'), ''),
        },
        'speech_style': _clean_str(expanded.get('speech_style'), ''),
        'battle_line': _clean_str(expanded.get('battle_line'), ''),
        **_PERSONA_DEFAULTS,
    }
    monster.personality_traits = _clean_list(expanded.get('personality_traits'), ['determined'])[:5]
    monster.generation_stage = 'persona'
    monster.save()

    emit_monster_updated(monster.to_dict())
    return monster


def create_player_story(monster: Monster, choices: dict[str, str]) -> Monster:
    """Stage 3: the finished prose. The player's appearance text is kept
    verbatim as the visual description; the LLM only pulls the color and
    feature lists out of it and writes description/backstory around it."""

    appearance_text = choices.get('appearance') or (
        f"{choices.get('kind', 'An adventurer')}, dressed for a long walk into the dark"
    )

    prose = build_and_generate(
        'player_story',
        'player_generation',
        {
            'choices_so_far': choices_so_far_text(choices),
            'blueprint_facts': _blueprint_facts_text(monster),
            'appearance_text': appearance_text,
        },
    )

    monster.description = _clean_str(prose.get('description'), monster.description)
    monster.backstory = _clean_str(prose.get('backstory'), '') or None
    monster.appearance = {
        'visual_description': appearance_text,
        'primary_colors': _clean_list(prose.get('primary_colors'), []),
        'distinguishing_features': _clean_list(prose.get('distinguishing_features'), []),
    }
    monster.generation_stage = 'complete'
    monster.save()

    emit_monster_updated(monster.to_dict())
    return monster


def discard_partial_player() -> None:
    """A creation that failed midway leaves a half-built row + pointer;
    starting over clears both so the wizard can run clean. A COMPLETE
    player is never touched here (the service refuses those upstream)."""
    from backend.game.player.manager import PLAYER_MONSTER_KEY, get_player_monster
    from backend.models.global_variables import GlobalVariable

    partial = get_player_monster()
    if partial is not None and partial.generation_stage != 'complete':
        partial.delete()
        GlobalVariable.delete_key(PLAYER_MONSTER_KEY)


# ===== FACTS + CLEANUP HELPERS =====


def _blueprint_facts_text(monster: Monster) -> str:
    """The settled skeleton as prompt context for later stages"""
    taxonomy = monster.taxonomy or {}
    ecology = monster.ecology or {}
    return (
        f"Name: {monster.name}\n"
        f"Lineage: {taxonomy.get('domain')} > {taxonomy.get('kingdom')} > "
        f"{taxonomy.get('family')} > {taxonomy.get('genus')} > {taxonomy.get('species')} "
        f"(a {taxonomy.get('race_label')})\n"
        f"Role: {monster.party_role} | Size: {ecology.get('size_class')} | "
        f"Lifecycle: {ecology.get('lifecycle_stage')} | Came to be: {ecology.get('creation_mechanism')}"
    )


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
