# Resource Pool Tests - OFFLINE (pure logic, no LLM, no DB writes)
# Exercises the Mem-M2 layer: the resource ladders, referee word
# validation, code cost defaults, and the reserve lines in prompt blocks.
#
# Usage: python -m backend.tests.test_resources   (from project root)

from types import SimpleNamespace

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

def main():
    from backend.game.battle import manager as battle
    from backend.game.battle.constants import (
        RESOURCE_LADDER, RESOURCE_KEYS, RESOURCE_DELTAS,
        ABILITY_POOL_BY_TYPE, BRIMMING, SPENT, full_resources
    )
    from backend.game.battle.generator import _validated_resource_delta

    print('🧪 RESOURCE POOL TESTS')
    print('=' * 50)

    # ===== Ladder stepping and clamping =====
    print('\n-- apply_resource ladder math --')
    state = {'allies': {'1': {'name': 'A', 'stamina': 'brimming', 'mana': 'steady'}}}

    check('minor cost steps one level',
          battle.apply_resource(state, 'allies', '1', 'stamina', 'minor') == 'steady')
    check('heavy cost steps three levels',
          battle.apply_resource(state, 'allies', '1', 'stamina', 'heavy') == 'spent')
    check('costs clamp at spent',
          battle.apply_resource(state, 'allies', '1', 'stamina', 'moderate') == 'spent')
    check('restore_minor steps back one',
          battle.apply_resource(state, 'allies', '1', 'stamina', 'restore_minor') == 'drained')
    check('restore_major steps back two',
          battle.apply_resource(state, 'allies', '1', 'stamina', 'restore_major') == 'steady')
    check('restores clamp at brimming',
          battle.apply_resource(state, 'allies', '1', 'mana', 'restore_major') == 'brimming')
    check('none moves nothing',
          battle.apply_resource(state, 'allies', '1', 'mana', 'none') == 'brimming')
    check('unknown word moves nothing',
          battle.apply_resource(state, 'allies', '1', 'mana', 'astronomical') == 'brimming')
    check('unknown monster returns None',
          battle.apply_resource(state, 'allies', '99', 'mana', 'minor') is None)
    check('unknown resource returns None',
          battle.apply_resource(state, 'allies', '1', 'luck', 'minor') is None)

    # ===== Referee word validation =====
    print('\n-- referee cost word validation --')
    check('valid word passes', _validated_resource_delta('moderate') == 'moderate')
    check('case and spacing normalized', _validated_resource_delta(' Heavy ') == 'heavy')
    check('restore words pass', _validated_resource_delta('restore_major') == 'restore_major')
    check('garbage becomes None (code default)', _validated_resource_delta('a lot') is None)
    check('empty becomes None', _validated_resource_delta('') is None)
    check('None becomes None', _validated_resource_delta(None) is None)

    # ===== Battle seeding =====
    print('\n-- start_battle pool seeding --')
    # Offline: stub out persistence so no app context is needed
    battle.save_battle_state = lambda state: None
    seeded = battle.start_battle(
        {'1': {'name': 'Ally', 'condition': 'wounded', 'stamina': 'strained', 'mana': 'drained'}},
        {'7': {'name': 'Enemy', 'condition': 'fresh'}}
    )
    check('ally pools carry in from the run',
          seeded['allies']['1']['stamina'] == 'strained' and seeded['allies']['1']['mana'] == 'drained')
    check('enemy pools seed at brimming',
          seeded['enemies']['7']['stamina'] == BRIMMING and seeded['enemies']['7']['mana'] == BRIMMING)
    check('finishing_blows starts empty', seeded.get('finishing_blows') == {})
    snapshot = battle.get_battle_snapshot(seeded)
    check('snapshot entries carry pools to the frontend',
          snapshot['allies']['1']['stamina'] == 'strained')

    # ===== Ability-type pool defaults =====
    print('\n-- ability pool defaults --')
    import json, pathlib
    ability_json = json.loads(
        pathlib.Path('backend/ai/llm/prompts/ability_generation.json').read_text(encoding='utf-8')
    )
    template_text = json.dumps(ability_json)
    missing = [t for t in ABILITY_POOL_BY_TYPE if t not in template_text]
    check('every mapped ability type appears in ability_generation.json',
          not missing, f'unmapped-in-template: {missing}')
    check('all mapped pools are real pools',
          all(pool in RESOURCE_KEYS for pool in ABILITY_POOL_BY_TYPE.values()))

    # ===== Prompt context lines =====
    print('\n-- reserves in prompt blocks --')
    from backend.game.monster.context_builder import build_monster_block
    monster = SimpleNamespace(
        name='Testling', species='Test Sprite', description='desc', backstory='story',
        personality_traits=[], max_health=100, attack=20, defense=15, speed=10,
        rarity='common', party_role='striker', taxonomy={}, class_taxonomy=[],
        ecology={}, persona={}, abilities=[]
    )
    block = build_monster_block(monster, condition='fresh',
                                resources={'stamina': 'strained', 'mana': 'spent'})
    check('reserves line appears when resources given',
          'Reserves: stamina strained, mana spent' in block)
    block_without = build_monster_block(monster, condition='fresh')
    check('no reserves line without resources', 'Reserves:' not in block_without)

    memory_block = build_monster_block(monster, memory_lines=['[run 1] was_defeated: Fell.'])
    check('memory lines appear when given', 'Remembers the party:' in memory_block)

    from backend.game.battle.generator import build_battle_situation
    situation = build_battle_situation({
        'allies': {'1': {'name': 'A', 'condition': 'fresh', 'stamina': 'steady', 'mana': 'spent'}},
        'enemies': {'2': {'name': 'B', 'condition': 'wounded', 'defending': True,
                          'stamina': 'brimming', 'mana': 'brimming'}}
    })
    check('situation lines carry pools',
          'stamina steady, mana spent' in situation and 'defending' in situation)

    print('\n' + '=' * 50)
    print(f'🎉 {PASSED} passed, {FAILED} failed')
    raise SystemExit(1 if FAILED else 0)

if __name__ == '__main__':
    main()
