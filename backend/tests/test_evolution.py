# Evolution Tests - DATABASE ONLY (LLM stubbed, no server)
# Exercises the Evo-M1 layer: stage boost math, the rarity ladder, the
# name-root rule, the full form transform (lineage snapshot, taxonomy
# rules, heal), cap EXEMPTION (evolution must not touch or consume the
# growth caps), persona preservation, prose append rules, ability
# rewords, the finale memory, and eligibility gates.
#
# Usage: python -m backend.tests.test_evolution   (from project root)
# Uses the dedicated test database (harness.py); creates and removes its own rows.

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


HOME_STATE = {
    'in_dungeon': False,
    'current_location': None,
    'available_paths': {},
    'active_encounter': None,
    'party_conditions': {},
    'party_resources': {},
    'run_journal': {},
    'run_id': None,
    'seen_monster_ids': [],
    'dungeon_log': [],
}


def main():
    app = build_test_app()

    with app.app_context():
        import backend.game.utils as game_utils
        from backend.game.dungeon import manager as dungeon
        from backend.game.memory import growth
        from backend.game.monster import evolution
        from backend.models.ability import Ability
        from backend.models.core import create_tables, db
        from backend.models.following_monsters import FollowingMonster
        from backend.models.monster import Monster
        from backend.models.monster_evolution import MonsterEvolution
        from backend.models.monster_memory import MonsterMemory

        print('🧪 EVOLUTION TESTS')
        print('=' * 50)
        create_tables()

        saved_state = dungeon.get_dungeon_state()
        real_build_and_generate = game_utils.build_and_generate
        test_monster = None
        half_made = None

        try:
            dungeon.save_dungeon_state(dict(HOME_STATE))

            # ===== pure math: stages, rarity, names =====
            print('\n-- stage boost math --')
            check('stage 1 leaps 25%', evolution.boost_pct_for_stage(1) == 0.25)
            check('stage 2 leaps 15%', evolution.boost_pct_for_stage(2) == 0.15)
            check('stage 3 settles at 10%', evolution.boost_pct_for_stage(3) == 0.10)
            check('stage 7 stays at 10%', evolution.boost_pct_for_stage(7) == 0.10)
            check('nonsense stage counts as stage 1', evolution.boost_pct_for_stage(0) == 0.25)

            print('\n-- rarity ladder --')
            check('missing rarity climbs to uncommon', evolution.next_rarity(None) == 'uncommon')
            check('common climbs to uncommon', evolution.next_rarity('common') == 'uncommon')
            check('epic climbs to legendary', evolution.next_rarity('Epic ') == 'legendary')
            check('legendary stays legendary', evolution.next_rarity('legendary') == 'legendary')

            print('\n-- name root rule --')
            check(
                'Rokk -> Rokkarath accepted',
                evolution.keep_name_root('Rokk', 'Rokkarath') == 'Rokkarath',
            )
            check('Rokk -> Zephyr rejected', evolution.keep_name_root('Rokk', 'Zephyr') == 'Rokk')
            check(
                'short names still evolve',
                evolution.keep_name_root('Bo', 'Boulderborn') == 'Boulderborn',
            )
            check('empty proposal keeps the name', evolution.keep_name_root('Rokk', None) == 'Rokk')
            check(
                'multi-word names root on the first word',
                evolution.keep_name_root('Rokk the Quiet', 'Rokkarath') == 'Rokkarath',
            )

            # ===== the full form transform =====
            print('\n-- form transform (stage 1) --')
            test_monster = Monster(
                name='Rokk',
                species='Pebble Golem',
                description='A patient pile of pebbles that exists only inside the test suite.',
                backstory='It watched the mountain for a hundred quiet years.',
                max_health=100,
                attack=20,
                defense=16,
                speed=12,
                taxonomy={
                    'domain': 'Materium',
                    'kingdom': 'Construct',
                    'family': 'Stonebound',
                    'genus': 'Pebblus',
                    'species': 'Pebble Golem',
                    'type_label': 'Construct',
                    'race_label': 'Golem',
                },
                ecology={'size_class': 'small', 'sapience': 'sapient'},
                persona={
                    'core_wish': 'To matter more than a landslide',
                    'secret': 'It once crumbled on purpose.',
                    'grudges_and_bonds': ['Owes Fluffy a stone'],
                    'social_bonds': {'drawn_to': 'patient types', 'clashes_with': 'loud ones'},
                    'battle_line': 'The mountain walks!',
                    'speech_style': 'Slow, grinding sentences',
                    'goals': ['Guard something worth guarding'],
                    'motivations': 'The ache of standing still too long',
                },
                appearance={
                    'visual_description': 'A squat golem of round grey pebbles.',
                    'primary_colors': ['grey'],
                    'distinguishing_features': ['pebble skin'],
                },
                card_art_path='monster_card_art/test_rokk_old.png',
            )
            test_monster.save()
            stone_wall = Ability(
                monster_id=test_monster.id,
                name='Stone Wall',
                description='Stacks itself into a low wall that shelters an ally from one blow.',
                ability_type='defense',
            )
            stone_wall.save()

            evo1 = evolution.apply_evolution_form(
                test_monster,
                {
                    'species': 'Basalt Colossus',
                    'evolved_name': 'Rokkarath',
                    'family': None,
                    'genus': 'Basaltus',
                    'race_label': 'Colossus',
                    'size_class': 'large',
                    'form_theme': 'patience hardened into living stone',
                },
                guidance='lean into the mountain',
                stage=1,
            )
            db.session.refresh(test_monster)

            check(
                'all four stats leap 25%',
                (
                    test_monster.max_health,
                    test_monster.attack,
                    test_monster.defense,
                    test_monster.speed,
                )
                == (125, 25, 20, 15),
                f'got {test_monster.max_health}/{test_monster.attack}/{test_monster.defense}/{test_monster.speed}',
            )
            check('body comes out of the ceremony fresh', test_monster.current_health == 125)
            check('rarity climbs (None counts as common)', test_monster.rarity == 'uncommon')
            check('name evolved with its root kept', test_monster.name == 'Rokkarath')
            check('species transformed', test_monster.species == 'Basalt Colossus')
            taxonomy = test_monster.taxonomy or {}
            check(
                'curated domain/kingdom/type_label never move',
                (taxonomy.get('domain'), taxonomy.get('kingdom'), taxonomy.get('type_label'))
                == ('Materium', 'Construct', 'Construct'),
            )
            check('species mirrored into taxonomy', taxonomy.get('species') == 'Basalt Colossus')
            check(
                'genus/race_label evolved, null family kept',
                (taxonomy.get('genus'), taxonomy.get('race_label'), taxonomy.get('family'))
                == ('Basaltus', 'Colossus', 'Stonebound'),
            )
            check(
                'size class change snapped and stored',
                (test_monster.ecology or {}).get('size_class') == 'large',
            )

            check(
                'lineage row snapshots the old form',
                evo1 is not None
                and evo1.stage == 1
                and evo1.old_name == 'Rokk'
                and evo1.old_species == 'Pebble Golem'
                and evo1.old_rarity is None
                and evo1.new_rarity == 'uncommon'
                and evo1.old_stats == {'max_health': 100, 'attack': 20, 'defense': 16, 'speed': 12}
                and evo1.old_card_art_path == 'monster_card_art/test_rokk_old.png'
                and evo1.applied_boost_pct == 0.25,
            )
            check(
                'guidance and theme ride the lineage row',
                evo1.guidance == 'lean into the mountain'
                and (evo1.details or {}).get('form_theme') == 'patience hardened into living stone',
            )

            print('\n-- form transform (stage 2, diminished) --')
            check(
                'next stage counts existing rows', evolution.next_stage_number(test_monster.id) == 2
            )
            before = {stat: getattr(test_monster, stat) for stat in evolution.EVOLVED_STATS}
            evo2 = evolution.apply_evolution_form(
                test_monster,
                {
                    'species': 'Magma Colossus',
                    'evolved_name': 'Zephyr',  # root lost -> name kept
                    'size_class': 'gigantic',  # invalid -> size kept
                },
                guidance='',
                stage=2,
            )
            db.session.refresh(test_monster)
            expected = {stat: max(value + 1, round(value * 1.15)) for stat, value in before.items()}
            check(
                'stage 2 leaps only 15%',
                all(getattr(test_monster, stat) == expected[stat] for stat in expected),
                f'got {[getattr(test_monster, s) for s in expected]}',
            )
            check('rootless name proposal falls back', test_monster.name == 'Rokkarath')
            check(
                'invalid size class keeps the body',
                (test_monster.ecology or {}).get('size_class') == 'large',
            )
            check('rarity keeps climbing', test_monster.rarity == 'rare')
            check('second lineage row is stage 2', evo2.stage == 2 and evo2.old_name == 'Rokkarath')

            # ===== cap exemption: evolution never touches growth math =====
            print('\n-- growth caps stay untouched --')
            evolution.finalize_evolution(
                test_monster,
                evo1,
                narrative='The stone sang and remade itself.',
                memory_note='It became the mountain it once only watched.',
                applied={'new_ability': None, 'reworded': []},
            )
            db.session.refresh(evo1)
            check(
                'narrative saved to the lineage row',
                evo1.narrative == 'The stone sang and remade itself.',
            )
            evolved_rows = [
                m for m in MonsterMemory.for_monster(test_monster.id) if m.kind == 'evolved'
            ]
            check(
                "one 'evolved' memory written",
                len(evolved_rows) == 1
                and evolved_rows[0].details.get('stage') == 1
                and evolved_rows[0].details.get('old_name') == 'Rokk'
                and evolved_rows[0].details.get('amount_pct') == 0.25,
            )
            check(
                'evolved memories are invisible to the lifetime caps',
                MonsterMemory.growth_total_pct(test_monster.id, 'max_health') == 0.0
                and MonsterMemory.growth_total_pct(test_monster.id, 'all_stats') == 0.0,
            )
            attack_before = test_monster.attack
            growth.apply_growth(
                test_monster,
                {
                    'reflection': 'It still grows the slow way too.',
                    'stat': 'attack',
                    'tier': 'slight',
                    'new_ability': 'no',
                    'memory_note': 'Grew a little, the old way.',
                },
            )
            db.session.refresh(test_monster)
            check(
                'ordinary growth still applies after evolving',
                test_monster.attack == max(attack_before + 1, round(attack_before * 1.02)),
            )

            # ===== persona: shift what may shift, preserve the soul =====
            print('\n-- persona shift rules --')
            soul_before = {
                field: (test_monster.persona or {}).get(field)
                for field in ('core_wish', 'secret', 'grudges_and_bonds', 'social_bonds')
            }
            applied = evolution.apply_persona_shift(
                test_monster,
                {
                    'battle_line': 'The colossus does not walk - it arrives!',
                    'speech_style': 'Low volcanic rumble, fewer words',
                    'goals': ['Guard the party', 'Learn what magma remembers'],
                    'motivations': 'Proof that patience was worth it',
                    'memory_note': 'Its voice deepened the day it evolved.',
                    'core_wish': 'INJECTED',
                    'secret': 'INJECTED',  # must be ignored
                },
            )
            db.session.refresh(test_monster)
            persona = test_monster.persona or {}
            check(
                'soul fields byte-identical after the shift',
                all(persona.get(field) == soul_before[field] for field in soul_before),
            )
            check(
                'battle line / voice / goals / motivations evolved',
                persona.get('battle_line') == 'The colossus does not walk - it arrives!'
                and persona.get('speech_style') == 'Low volcanic rumble, fewer words'
                and persona.get('goals') == ['Guard the party', 'Learn what magma remembers']
                and persona.get('motivations') == 'Proof that patience was worth it',
            )
            check(
                'memory note carried out of the shift',
                applied['memory_note'] == 'Its voice deepened the day it evolved.',
            )

            line_before = persona.get('battle_line')
            evolution.apply_persona_shift(
                test_monster,
                {
                    'battle_line': 'x' * (int(max(len(line_before), 60) * 1.3) + 20),
                    'memory_note': 'note',
                },
            )
            db.session.refresh(test_monster)
            check(
                'overlong battle line rejected',
                (test_monster.persona or {}).get('battle_line') == line_before,
            )
            check(
                'empty shift applies nothing',
                evolution.apply_persona_shift(test_monster, None)
                == {'memory_note': '', 'changed': {}},
            )

            print('\n-- persona shift facts --')
            facts = evolution.build_persona_shift_facts(applied)
            check(
                'facts name the new cry and goals',
                'The colossus does not walk' in facts and 'Guard the party' in facts,
            )
            check(
                'unchanged inner life says so',
                'kept its old shape' in evolution.build_persona_shift_facts({'changed': {}}),
            )

            # ===== prose: replace, append, cap =====
            print('\n-- prose rules --')
            backstory_before = test_monster.backstory
            art_worthy = evolution.apply_prose(
                test_monster,
                {
                    'description': 'A colossus of fused basalt, slow as bedrock and twice as sure.',
                    'backstory_addendum': 'Then came the ceremony: '
                    + 'a' * 900,  # over the 800 cap
                    'visual_description': 'A towering basalt figure with molten seams, clearly grown from the old pebble shape.',
                    'primary_colors': 'obsidian black, ember orange',  # string -> list
                    'distinguishing_features': ['molten seams', 'basalt crown'],
                },
            )
            db.session.refresh(test_monster)
            check(
                'description replaced',
                test_monster.description.startswith('A colossus of fused basalt'),
            )
            check(
                'backstory gained a chapter, old story intact',
                test_monster.backstory.startswith(backstory_before)
                and 'Then came the ceremony' in test_monster.backstory,
            )
            addendum_text = test_monster.backstory[len(backstory_before) :].strip()
            check(
                'addendum capped at 800 chars',
                len(addendum_text) <= 800,
                f'got {len(addendum_text)}',
            )
            appearance = test_monster.appearance or {}
            check(
                'appearance rebuilt for the card artist',
                art_worthy is True
                and appearance.get('visual_description', '').startswith('A towering basalt figure')
                and appearance.get('primary_colors') == ['obsidian black', 'ember orange']
                and appearance.get('distinguishing_features') == ['molten seams', 'basalt crown'],
            )
            check('no prose means no art regen', evolution.apply_prose(test_monster, None) is False)

            # ===== abilities: rewords clamped, the new one is a request =====
            print('\n-- ability evolution rules --')
            old_wall_description = stone_wall.description
            applied = evolution.apply_ability_evolution(
                test_monster,
                {
                    'reword_1': 'stone wall',  # case-insensitive match
                    'reword_1_new_name': 'Basalt Rampart',
                    'reword_1_description': old_wall_description[:-8] + ' anew.',
                    'reword_2': 'Unknown Trick',  # not a real ability
                    'reword_2_description': 'Should be ignored.',
                    'new_ability': 'yes',
                    'ability_theme': 'a signature eruption only the new body can hold',
                },
            )
            db.session.refresh(stone_wall)
            check(
                'reword renamed and rewrote the ability',
                stone_wall.name == 'Basalt Rampart' and stone_wall.description.endswith('anew.'),
            )
            check('unknown ability name ignored', applied['reworded'] == ['Basalt Rampart'])
            check(
                'the signature ability is a request, not an act',
                applied['wants_new'] is True and 'eruption' in applied['theme'],
            )

            reworded_description = stone_wall.description
            evolution.apply_ability_evolution(
                test_monster,
                {
                    'reword_1': 'Basalt Rampart',
                    'reword_1_description': reworded_description
                    + ' '
                    + 'x' * len(reworded_description),
                    'new_ability': 'no',
                },
            )
            db.session.refresh(stone_wall)
            check('overlong reword rejected', stone_wall.description == reworded_description)
            check(
                'empty decisions change nothing',
                evolution.apply_ability_evolution(test_monster, None)
                == {'reworded': [], 'wants_new': False, 'theme': ''},
            )

            # ===== eligibility gates =====
            print('\n-- eligibility --')
            check(
                'not following -> blocked',
                'not following' in (evolution.evolution_eligibility_error(test_monster.id) or ''),
            )
            FollowingMonster(monster_id=test_monster.id).save()
            check(
                'following at home base -> eligible',
                evolution.evolution_eligibility_error(test_monster.id) is None,
            )

            in_dungeon = dict(HOME_STATE)
            in_dungeon.update(
                {'in_dungeon': True, 'current_location': {'name': 'Test Deep', 'description': ''}}
            )
            dungeon.save_dungeon_state(in_dungeon)
            check(
                'mid-run -> blocked',
                'in the dungeon' in (evolution.evolution_eligibility_error(test_monster.id) or ''),
            )
            dungeon.save_dungeon_state(dict(HOME_STATE))

            half_made = Monster(
                name='Half',
                species='Test Sketch',
                description='Still generating.',
                generation_stage='blueprint',
            )
            half_made.save()
            FollowingMonster(monster_id=half_made.id).save()
            check(
                'half-generated -> blocked',
                'taking shape' in (evolution.evolution_eligibility_error(half_made.id) or ''),
            )
            check(
                'missing monster -> blocked',
                'not found' in (evolution.evolution_eligibility_error(99999999) or ''),
            )

            # ===== form failure aborts before anything moves =====
            print('\n-- form failure aborts cleanly --')

            def boom(*args, **kwargs):
                raise Exception('LLM unavailable')

            game_utils.build_and_generate = boom
            rows_before = MonsterEvolution.count_for_monster(test_monster.id)
            name_before = test_monster.name
            raised = False
            try:
                evolution.run_form_design(test_monster, 'guidance', 3, 'test')
            except Exception:
                raised = True
            db.session.refresh(test_monster)
            check('form design failure propagates (workflow aborts)', raised)
            check(
                'nothing mutated on abort',
                test_monster.name == name_before
                and MonsterEvolution.count_for_monster(test_monster.id) == rows_before,
            )

        finally:
            print('\n-- cleanup --')
            game_utils.build_and_generate = real_build_and_generate
            try:
                for monster in (test_monster, half_made):
                    if monster:
                        MonsterMemory.query.filter_by(monster_id=monster.id).delete()
                        MonsterEvolution.query.filter_by(monster_id=monster.id).delete()
                        FollowingMonster.query.filter_by(monster_id=monster.id).delete()
                        db.session.commit()
                        monster.delete()  # abilities cascade
                dungeon.save_dungeon_state(saved_state)
                print('  🧹 test rows removed, dungeon state restored')
            except Exception as e:
                print(f'  ⚠️ cleanup problem: {e}')

        print('\n' + '=' * 50)
        print(f'🎉 {PASSED} passed, {FAILED} failed')
        return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
