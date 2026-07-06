# Monster Template + Context Budget Verification (offline - no LLM, no DB)
# 1. Every prompt template in backend/ai/llm/prompts parses as a valid
#    format string (catches unbalanced {braces} in JSON examples)
# 2. The staged monster templates render with exactly the variables
#    generator.py passes (catches placeholder/variable drift)
# 3. A full battle roster (4 party + 3 enemies) fits the prompt budget
#    at every context-window bin (catches tier-content bloat)
#
# Usage: python -m backend.tests.test_monster_templates   (from project root)

import string
from types import SimpleNamespace

from backend.ai.llm.prompt_engine import get_prompt_engine
from backend.game.monster import cmdts_data

FAILURES = []

def check(label, condition, detail=''):
    if condition:
        print(f'  OK   {label}')
    else:
        FAILURES.append(label)
        print(f'  FAIL {label} {detail}')

def template_placeholders(template_text):
    """All {placeholder} names in a format string"""
    return {
        field for _, field, _, _ in string.Formatter().parse(template_text)
        if field
    }

# ===== 1. every template is a valid format string =====

def test_all_templates_parse():
    print('\n1. All templates parse as format strings')
    engine = get_prompt_engine()
    for name in engine.list_templates():
        template = engine.get_template(name)
        try:
            template_placeholders(template.template)
            check(f'{name} ({template.category})', True)
        except ValueError as e:
            check(f'{name} ({template.category})', False, f'- {e}')

# ===== 2. staged monster templates match generator variables =====

# The exact variable sets generator.py passes to build_and_generate
GENERATOR_VARIABLES = {
    'monster_blueprint_identity': {
        'location_context', 'rarity', 'taxonomy_options', 'role_options',
        'size_options', 'lifecycle_options', 'creation_options'
    },
    'monster_blueprint_ecology': {
        'location_context', 'identity_facts', 'habitat_options', 'biome_options',
        'social_options', 'sustenance_options', 'feeding_options', 'sapience_options',
        'communication_options', 'element_options', 'activity_options',
        'class_domain_options_line', 'class_domain_options'
    },
    'monster_inner_life': {'monster_facts'},
    'monster_social_self': {'monster_facts', 'inner_life_facts'},
    'monster_creative_text': {'location_context', 'monster_facts', 'persona_facts'},
    'generate_ability': {
        'monster_name', 'monster_species', 'monster_description', 'monster_backstory',
        'monster_health', 'monster_attack', 'monster_defense', 'monster_speed',
        'monster_personality', 'monster_role', 'monster_class', 'monster_elements',
        'monster_wish', 'existing_abilities_text', 'ability_count'
    },
    # Inventory generation (backend/game/inventory/generator.py)
    'treasure_item': {'location_name', 'location_description'},
    'reward_item': {'location_name', 'location_description', 'monster_details', 'dialogue_history'},
    'victory_cocatok': {'location_name', 'defeated_names', 'battle_summary', 'color_options'},
    'treasure_discovery': {'location_name', 'location_description', 'party_summary',
                           'dungeon_log', 'item_name', 'item_description'},
    # Item referee (dungeon/registered_workflows.py use_dungeon_item)
    'dungeon_item_use': {'location_name', 'location_description', 'party_details',
                         'item_name', 'item_description', 'uses_remaining',
                         'target_description', 'secret_knowledge', 'dungeon_log'}
}

def test_staged_templates_render():
    print('\n2. Staged templates use only variables the generator provides')
    engine = get_prompt_engine()
    for name, provided in GENERATOR_VARIABLES.items():
        template = engine.get_template(name)
        if not template:
            check(name, False, '- template missing')
            continue
        used = template_placeholders(template.template)
        extra = used - provided
        check(name, not extra, f'- placeholders with no variable: {sorted(extra)}')

        # And it actually renders
        variables = {key: 'sample' for key in provided}
        rendered = engine.build_prompt(name, variables)
        check(f'{name} renders', bool(rendered))

# ===== 3. battle roster fits the prompt budget at every bin =====

def sample_monster(i):
    """A fully fleshed-out monster (persona at realistic prose lengths)"""
    return SimpleNamespace(
        name=f'Monster{i}', species='Cave Petrascarab',
        description='A sturdy beetle with a rock-like exoskeleton, known for its defensive prowess in the deep caves.',
        backstory='Born in the deep caves of the mountain realm, it wandered the dark for years after an earthquake '
                  'took its colony, seeking new allies and a new place to defend as its own.',
        personality_traits=['stalwart', 'patient', 'protective', 'quiet'],
        max_health=144, attack=22, defense=26, speed=12,
        rarity='rare', party_role='tank',
        taxonomy={'domain': 'Materium', 'kingdom': 'Insectoid', 'family': 'Stoneshell Burrowers',
                  'genus': 'Petrascarab', 'species': 'Cave Petrascarab',
                  'type_label': 'Insectoid', 'race_label': 'Beetle'},
        class_taxonomy=[{'domain': 'Martial', 'discipline': 'Bulwark Arts',
                         'specialization': 'Stoneshell Bastion'}],
        ecology={'size_class': 'small', 'lifecycle_stage': 'adult', 'creation_mechanism': 'hatched',
                 'habitat': {'primary': 'subterrain', 'secondary': ['land'], 'biomes': ['cavern', 'mountain']},
                 'social_structure': {'primary': 'colony', 'notes': 'seeks a new colony to protect'},
                 'diet': {'feeds': True, 'sustenance': ['matter'], 'feeding_style': 'lithovore',
                          'notes': 'grazes mineral-rich cave lichen'},
                 'sapience': 'sapient', 'communication': ['speech'],
                 'elemental_affinities': ['earth'], 'activity_cycle': 'nocturnal'},
        persona={'core_wish': 'To find a new colony and never again fail to protect one',
                 'motivations': 'The ache of a lost home drives everything it does',
                 'goals': ['Become a legendary defender', 'Find ground worth guarding'],
                 'beliefs': 'The strong exist to shelter the weak, always',
                 'moral_character': 'Loyal and honorable to a fault',
                 'fears': ['Being the last of its line', 'Cave-ins it cannot hold back'],
                 'secret': 'It froze in fear during the earthquake and blames itself.',
                 'likes': ['interesting stones', 'quiet places', 'loyalty'],
                 'dislikes': ['loud noises', 'sudden movements'],
                 'hobbies': ['collecting stones', 'burrowing'],
                 'profession': 'Guardian',
                 'attitude_toward_strangers': 'Cautiously optimistic; watches before trusting',
                 'responds_well_to': ['patience', 'respect', 'calm'],
                 'responds_poorly_to': ['loud noises', 'aggression'],
                 'recruitment_lever': 'Proof the party protects its own like a colony would',
                 'social_bonds': {'drawn_to': 'patient, steadfast types',
                                  'clashes_with': 'loud tricksters'},
                 'speech_style': 'Terse and formal; geological metaphors; refers to itself by name',
                 'battle_line': 'Intruder detected. Prepare to be crushed under the weight of the mountain!'},
        abilities=[SimpleNamespace(name='Stone Wall', description='Hardens its shell to absorb blows', ability_type='defense'),
                   SimpleNamespace(name='Mandible Crush', description='A slow, unstoppable bite', ability_type='attack')]
    )

def test_roster_fits_budget():
    print('\n3. Full battle roster (4 party + 3 enemies) fits the prompt budget per bin')
    import os
    from backend.game.monster.context_builder import build_monster_block
    from backend.game.utils.context_limits import (
        resolve_detail_tier, get_prompt_char_budget
    )

    roster = [sample_monster(i) for i in range(7)]
    original = os.environ.get('LLM_CONTEXT_SIZE')

    # At least this share of the budget must remain for logs + instructions
    HEADROOM_SHARE = 0.45

    try:
        for context_size in (4096, 8192, 16384):
            os.environ['LLM_CONTEXT_SIZE'] = str(context_size)
            tier = resolve_detail_tier()
            blocks = "\n".join(
                build_monster_block(m, condition='fresh', side_label='HOSTILE ENEMY' if i >= 4 else "PLAYER'S PARTY")
                for i, m in enumerate(roster)
            )
            budget = get_prompt_char_budget()
            used_share = len(blocks) / budget
            check(
                f'{context_size} tokens -> {tier}: roster {len(blocks)} chars '
                f'= {used_share:.0%} of {budget} budget',
                used_share <= (1 - HEADROOM_SHARE)
            )
            secret_leaked = 'froze in fear' in blocks
            check(f'{context_size} tokens -> secret stays out of battle blocks', not secret_leaked)
    finally:
        if original is None:
            os.environ.pop('LLM_CONTEXT_SIZE', None)
        else:
            os.environ['LLM_CONTEXT_SIZE'] = original

def main():
    print('MONSTER TEMPLATE + CONTEXT BUDGET VERIFICATION')
    print('=' * 60)
    test_all_templates_parse()
    test_staged_templates_render()
    test_roster_fits_budget()

    print('\n' + '=' * 60)
    if FAILURES:
        print(f'{len(FAILURES)} FAILURE(S): {FAILURES}')
        raise SystemExit(1)
    print('ALL CHECKS PASS')

if __name__ == '__main__':
    main()
