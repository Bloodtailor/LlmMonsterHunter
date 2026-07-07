# Player Creation Tests - OFFLINE (no LLM, no ComfyUI, test DB)
# Exercises Ngx-M3 (docs/plans/new-game-experience.md): option sets
# (count/length clamps, junk dropped), the staged finalize (choices are
# LAW: wish and appearance verbatim, taxonomy normalized, code-owned
# stats, pointer set, partial retry, complete refusal), and the portrait
# stage (path validation, upload guardrails, select semantics).
#
# Usage: python -m backend.tests.test_player_creation   (from project root)

import shutil
import tempfile
from pathlib import Path

from backend.tests.harness import build_test_app

PASSED = 0
FAILED = 0


def check(name: str, condition: bool, detail: str = ''):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  ✅ {name}")
    else:
        FAILED += 1
        print(f"  ❌ {name}{f' - {detail}' if detail else ''}")


# Canned LLM answers per template - the stub returns these
STUB_ANSWERS = {
    'player_options': {
        'options': [
            '  Human - a baker who walked away from the ovens  ',
            'A soot-winged fey moth the size of a child',
            42,  # junk - must be dropped
            'x' * 500,  # overlong - must be clipped
            'One option too many',
            'And another',
        ]
    },
    'player_blueprint': {
        'domain': 'materium',  # case-insensitive normalization
        'kingdom': 'Kinfolk',
        'family': 'Bakers of the Low Road',
        'genus': 'Wandering Baker',
        'species': 'Human',
        'race_label': 'Human',
        'size_class': 'MEDIUM',
        'lifecycle_stage': 'adult',
        'creation_mechanism': 'born',
    },
    'player_persona': {
        'personality_traits': ['stubborn', 'warm', 'practical'],
        'motivations': 'Bread did not fill the hole the wish left.',
        'goals': ['Reach the deep places'],
        'beliefs': 'Anything kneaded long enough takes shape.',
        'moral_character': 'Fair, and generous with crusts.',
        'fears': ['dying unremarkable'],
        'likes': ['warm stone', 'first light'],
        'dislikes': ['wasted flour'],
        'hobbies': ['baking'],
        'profession': 'Baker',
        'attitude_toward_strangers': 'Feeds them first, asks second.',
        'responds_well_to': ['honesty'],
        'responds_poorly_to': ['flattery'],
        'drawn_to': 'quiet perseverance',
        'clashes_with': 'cruelty',
        'speech_style': 'Short, floury proverbs.',
        'battle_line': 'The oven is hot enough.',
    },
    'player_story': {
        'description': 'Marla the baker stands square-shouldered at the dungeon mouth.',
        'backstory': 'She left the ovens the morning the dream came back.',
        'primary_colors': ['flour white', 'ember orange'],
        'distinguishing_features': ['burn-scarred forearms', 'a wooden peel on her back'],
    },
    'generate_ability': {
        'name': 'Proving Rise',
        'description': 'A test ability from the stub.',
        'type': 'support',
    },
}

CHOICES = {
    'kind': 'Human - a stubborn baker',
    'name': 'Marla',
    'background': 'Ran the last bakery on the Low Road.',
    'personality': 'Stubborn, warm, allergic to nonsense.',
    'wish': 'To taste the bread her grandmother baked once more.',
    'role': 'Support',  # normalize_choice must lowercase this
    'appearance': 'A square-shouldered woman with burn-scarred forearms and a wooden peel.',
}


def stub_build_and_generate(template_name, prompt_type, variables=None):
    return STUB_ANSWERS[template_name]


def main():
    app = build_test_app()

    with app.app_context():
        from backend.game.monster import generator as generator_module
        from backend.game.player import creation as creation_module
        from backend.game.player import options as options_module
        from backend.game.player import portrait as portrait_module
        from backend.game.player import registered_workflows as player_workflows
        from backend.game.player.manager import (
            PLAYER_MONSTER_KEY,
            get_player_monster,
            get_player_monster_id,
        )
        from backend.models.ability import Ability
        from backend.models.core import create_tables
        from backend.models.global_variables import GlobalVariable
        from backend.models.monster import Monster
        from backend.services import player_service

        print('🧪 PLAYER CREATION TESTS')
        print('=' * 50)
        create_tables()

        real_creation_llm = creation_module.build_and_generate
        real_options_llm = options_module.build_and_generate
        real_generator_llm = generator_module.build_and_generate
        real_outputs_dir = portrait_module.outputs_dir
        temp_outputs = Path(tempfile.mkdtemp(prefix='player_portrait_test_'))
        created_ids = []

        def note(step, data):  # a quiet on_update
            pass

        try:
            creation_module.build_and_generate = stub_build_and_generate
            options_module.build_and_generate = stub_build_and_generate
            generator_module.build_and_generate = stub_build_and_generate
            portrait_module.outputs_dir = lambda: temp_outputs
            GlobalVariable.delete_key(PLAYER_MONSTER_KEY)

            # ===== option sets =====
            print('\n-- option sets --')
            options = options_module.generate_options('kind', {})
            check('kind offers 4 options', len(options) == 4, str(len(options)))
            check('options are trimmed', options[0].startswith('Human -'))
            check('junk entries are dropped', all(isinstance(o, str) for o in options))
            check(
                'overlong options are clipped to the field cap',
                all(len(o) <= options_module.FIELD_MAX_CHARS['kind'] for o in options),
            )

            result = player_workflows.generate_player_options({'field': 'nonsense'}, note)
            check('an unknown field fails the workflow', result['success'] is False)
            # Workflow failures nest their envelope under 'error' (the
            # codebase-wide error_response(dict) pattern)
            check(
                '...at validation',
                (result.get('error') or {}).get('failed_at') == 'validate_context',
            )

            # ===== the finalize =====
            print('\n-- the finalize --')
            result = player_workflows.create_player_character(dict(CHOICES), note)
            check('the character is created', result['success'] is True, str(result.get('error')))

            player = get_player_monster()
            created_ids.append(player.id)
            check('the pointer names the new row', player is not None)
            check('the stage is complete', player.generation_stage == 'complete')
            check('the name is the chosen name', player.name == 'Marla')
            check('rarity is fixed at common', player.rarity == 'common')
            check('the role normalized from "Support"', player.party_role == 'support')
            check(
                'the taxonomy snapped onto the tree',
                player.taxonomy.get('domain') == 'Materium'
                and player.taxonomy.get('kingdom') == 'Kinfolk',
            )
            check('stats were derived by code', player.max_health > 0 and player.attack > 0)
            check(
                'the wish is core_wish VERBATIM',
                player.persona.get('core_wish') == CHOICES['wish'],
            )
            check('the player keeps no invented secret', player.persona.get('secret') == '')
            check(
                'the appearance text is kept verbatim',
                player.appearance.get('visual_description') == CHOICES['appearance'],
            )
            check(
                'colors and features were pulled from it',
                player.appearance.get('primary_colors') == ['flour white', 'ember orange'],
            )
            check(
                'two abilities were learned',
                Ability.query.filter_by(monster_id=player.id).count() == 2,
            )
            check('no card art yet - the portrait stage owns that', player.card_art_path is None)

            # A COMPLETE character refuses a second creation
            result = player_workflows.create_player_character(dict(CHOICES), note)
            check('a complete character refuses recreation', result['success'] is False)
            check('...naming the character', 'Marla' in str(result.get('error')))
            service_result = player_service.create_character(dict(CHOICES))
            check('the service refuses too', service_result['success'] is False)

            # A PARTIAL character (failed mid-creation) is discarded and rebuilt
            player.generation_stage = 'persona'
            player.save()
            old_id = player.id
            result = player_workflows.create_player_character(dict(CHOICES), note)
            check('a partial character is rebuilt', result['success'] is True)
            check('...as a fresh row', get_player_monster_id() != old_id)
            check('...and the old partial is gone', Monster.get_monster_by_id(old_id) is None)
            player = get_player_monster()
            created_ids.append(player.id)

            # ===== the portrait stage =====
            print('\n-- the portrait stage --')
            check(
                'an empty path is refused',
                portrait_module.candidate_path_error('') is not None,
            )
            check(
                'traversal is refused',
                portrait_module.candidate_path_error('player_uploads/../secrets.png') is not None,
            )
            check(
                'foreign folders are refused',
                portrait_module.candidate_path_error('monster_card_art/00000001.png') is not None,
            )
            check(
                'a missing file is refused',
                portrait_module.candidate_path_error('player_uploads/99999999.png') is not None,
            )

            png_bytes = b'\x89PNG\r\n\x1a\n' + b'test-image-payload'
            check(
                'a renamed non-image is refused',
                portrait_module.upload_error('fake.png', b'MZ-not-an-image') is not None,
            )
            check(
                'an oversized image is refused',
                portrait_module.upload_error(
                    'big.png', b'\x89PNG\r\n\x1a\n' + b'0' * portrait_module.UPLOAD_MAX_BYTES
                )
                is not None,
            )
            check(
                'a wrong extension is refused',
                portrait_module.upload_error('script.exe', png_bytes) is not None,
            )
            check('a real png passes', portrait_module.upload_error('me.png', png_bytes) is None)

            upload_result = player_service.upload_portrait('me.png', png_bytes)
            check('an upload is stored and auto-selected', upload_result['success'] is True)
            player = get_player_monster()
            check(
                'the portrait points at the upload',
                (player.card_art_path or '').startswith('player_uploads/'),
                str(player.card_art_path),
            )

            # A painted candidate can be selected after the fact
            candidate_dir = temp_outputs / portrait_module.GENERATED_FOLDER
            candidate_dir.mkdir(parents=True, exist_ok=True)
            (candidate_dir / '00000001.png').write_bytes(png_bytes)
            select_result = player_service.select_portrait('player_card_art/00000001.png')
            check('a painted candidate can be selected', select_result['success'] is True)
            check(
                'the portrait switched to it',
                get_player_monster().card_art_path == 'player_card_art/00000001.png',
            )

            # The portrait prompt carries identity + the brief
            prompt = portrait_module.compose_portrait_prompt(player, 'a floury silhouette')
            check(
                'the portrait prompt carries name and brief',
                'Marla' in prompt and 'a floury silhouette' in prompt,
                prompt,
            )

        finally:
            creation_module.build_and_generate = real_creation_llm
            options_module.build_and_generate = real_options_llm
            generator_module.build_and_generate = real_generator_llm
            portrait_module.outputs_dir = real_outputs_dir
            shutil.rmtree(temp_outputs, ignore_errors=True)
            GlobalVariable.delete_key(PLAYER_MONSTER_KEY)
            for monster_id in created_ids:
                fresh = Monster.get_monster_by_id(monster_id)
                if fresh:
                    fresh.delete()

    print('\n' + '=' * 50)
    print(f'PASSED: {PASSED}  FAILED: {FAILED}')
    return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
