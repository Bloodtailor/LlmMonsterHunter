# Affinity Tests - OFFLINE (LLM stubbed, test DB)
# Exercises Game Loop M5: the affinity ladder math, the per-run step
# valve, wary battle autonomy (the LLM picks the action, code validates
# targets, the turn carries autonomous=True), and the healed-by-an-ally
# affinity hook inside combat resolution.
#
# Usage: python -m backend.tests.test_affinity   (from project root)

import copy

from backend.core.workflow_steps import WorkflowStep
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


def _make_monster(name: str, affinity_tier=None):
    from backend.models.monster import Monster

    monster = Monster(
        name=name,
        species='Test Species',
        description='A creature that exists only inside the affinity suite.',
        max_health=50,
        attack=10,
        defense=10,
        speed=10,
        affinity=affinity_tier,
    )
    monster.save()
    return monster


def main():
    app = build_test_app()

    with app.app_context():
        from backend.game.battle import generator as battle_generator
        from backend.game.battle import manager as battle
        from backend.game.dungeon import manager as dungeon
        from backend.game.monster import affinity
        from backend.models.core import create_tables
        from backend.models.monster import Monster
        from backend.models.monster_memory import MonsterMemory

        print('🧪 AFFINITY TESTS')
        print('=' * 50)
        create_tables()

        saved_dungeon_state = dungeon.get_dungeon_state()
        saved_battle_state = battle.get_battle_state()
        real_generate = battle_generator.build_and_generate
        real_stream = battle_generator.build_and_stream
        created = []

        try:
            # ===== ladder math =====
            print('\n-- ladder basics --')
            wary = _make_monster('Wary One')
            created.append(wary)
            devoted = _make_monster('Devoted One', 'devoted')
            created.append(devoted)

            check('NULL affinity reads as wary', affinity.get_affinity(wary) == 'wary')
            check('wary is autonomous', affinity.is_autonomous(wary))
            check('devoted is not autonomous', not affinity.is_autonomous(devoted))
            check(
                'unknown tier reads as wary',
                affinity.get_affinity(_FakeTier('astronomical')) == 'wary',
            )
            check(
                'context line carries the tier word',
                'devoted' in affinity.affinity_context_line(devoted),
            )

            print('\n-- stepping outside a run (no valve) --')
            dungeon.save_dungeon_state(copy.deepcopy(dungeon._EMPTY_STATE))
            check(
                'wary steps to familiar',
                affinity.step_affinity(wary.id, 'campfire_chat') == 'familiar',
            )
            check(
                'familiar steps to trusting',
                affinity.step_affinity(wary.id, 'campfire_chat') == 'trusting',
            )
            check(
                'trusting steps to devoted',
                affinity.step_affinity(wary.id, 'campfire_chat') == 'devoted',
            )
            check(
                'devoted never steps further',
                affinity.step_affinity(wary.id, 'campfire_chat') is None,
            )
            memories = MonsterMemory.query.filter_by(monster_id=wary.id, kind='affinity_grew').all()
            check('every step wrote a memory', len(memories) == 3, f'got {len(memories)}')

            print('\n-- the per-run valve --')
            valved = _make_monster('Valved One')
            created.append(valved)
            run_state = copy.deepcopy(dungeon._EMPTY_STATE)
            run_state.update({'in_dungeon': True, 'dungeon_log': []})
            dungeon.save_dungeon_state(run_state)

            check('step 1 in a run lands', affinity.step_affinity(valved.id, 'camp_rest') == 'familiar')
            check(
                'step 2 in a run lands',
                affinity.step_affinity(valved.id, 'healed_by_ally') == 'trusting',
            )
            check(
                'step 3 hits the per-run valve',
                affinity.step_affinity(valved.id, 'survived_run_together') is None,
            )
            fresh = Monster.get_monster_by_id(valved.id)
            check('the tier stayed at the valve', affinity.get_affinity(fresh) == 'trusting')

            dungeon.save_dungeon_state(copy.deepcopy(dungeon._EMPTY_STATE))
            check(
                'outside the run the same monster steps again',
                affinity.step_affinity(valved.id, 'campfire_chat') == 'devoted',
            )

            # ===== wary battle autonomy =====
            print('\n-- autonomous ally turns --')
            from backend.game.battle.turn import autonomy as autonomy_module
            from backend.game.battle.turn.context import TurnContext

            actor = _make_monster('Lone Wolf')  # NULL affinity -> wary
            created.append(actor)
            enemy = _make_monster('Test Foe', 'devoted')  # tier irrelevant for enemies
            created.append(enemy)

            state = {
                'in_battle': True,
                'allies': {
                    str(actor.id): {
                        'name': 'Lone Wolf',
                        'condition': 'fresh',
                        'stamina': 'brimming',
                        'mana': 'brimming',
                    }
                },
                'enemies': {
                    str(enemy.id): {
                        'name': 'Test Foe',
                        'condition': 'fresh',
                        'stamina': 'brimming',
                        'mana': 'brimming',
                    }
                },
                'recent_log': [],
                'turn_history': [],
                'last_acted': {},
                'turn_count': 0,
            }

            emitted = []
            step = WorkflowStep(lambda name, data: emitted.append((name, copy.deepcopy(data))))

            def scripted_llm(template, workflow, variables=None):
                if template == 'ally_autonomous_turn':
                    # The LLM tries to attack a PARTY member - code must
                    # redirect a wary ally's attack onto an enemy
                    return {'action': 'attack', 'ability_name': None, 'target': 'Lone Wolf'}
                if template == 'action_resolution':
                    return {
                        'narration': 'Lone Wolf lunges on its own terms.',
                        'impact': 'light',
                        'stamina_cost': 'minor',
                        'mana_cost': 'none',
                    }
                raise AssertionError(f'unexpected template {template}')

            battle_generator.build_and_generate = scripted_llm
            battle_generator.build_and_stream = lambda *args, **kwargs: 777

            ctx = TurnContext(state, step, 'test')
            autonomy_module.resolve_autonomous_ally_turn(ctx, str(actor.id))

            turn_events = [d for n, d in emitted if n == 'action_resolved']
            check('the autonomous turn emitted a resolved action', len(turn_events) == 1)
            if turn_events:
                payload = turn_events[0]['action_result']
                check('the turn is marked autonomous', payload.get('autonomous') is True)
                check(
                    'the attack was redirected onto the enemy',
                    payload.get('target_name') == 'Test Foe',
                    f"hit {payload.get('target_name')}",
                )
            check(
                'the enemy took the hit',
                state['enemies'][str(enemy.id)]['condition'] == 'scuffed',
            )
            check(
                'the acting ally was recorded as having acted',
                str(actor.id) in state.get('last_acted', {}),
            )

            # ===== the healed-by-an-ally hook =====
            print('\n-- healing deepens trust --')
            healer = _make_monster('Healer', 'devoted')
            created.append(healer)
            hurt = _make_monster('Hurt One')  # wary
            created.append(hurt)

            run_state = copy.deepcopy(dungeon._EMPTY_STATE)
            run_state.update({'in_dungeon': True, 'dungeon_log': []})
            dungeon.save_dungeon_state(run_state)

            heal_state = {
                'in_battle': True,
                'allies': {
                    str(healer.id): {'name': 'Healer', 'condition': 'fresh'},
                    str(hurt.id): {'name': 'Hurt One', 'condition': 'wounded'},
                },
                'enemies': {},
                'recent_log': [],
                'turn_history': [],
                'last_acted': {},
                'turn_count': 0,
            }

            def healing_llm(template, workflow, variables=None):
                return {
                    'narration': 'A soothing light.',
                    'impact': 'heal_light',
                    'stamina_cost': 'none',
                    'mana_cost': 'minor',
                }

            battle_generator.build_and_generate = healing_llm

            from backend.game.battle.turn.actions import resolve_combat_turn

            heal_ctx = TurnContext(heal_state, WorkflowStep(lambda n, d: None), 'test')
            resolve_combat_turn(
                heal_ctx, 'allies', str(healer.id), 'attack', None, 'allies', str(hurt.id)
            )

            check(
                "being healed stepped the hurt monster's affinity",
                affinity.get_affinity(Monster.get_monster_by_id(hurt.id)) == 'familiar',
            )
            check(
                'the healer itself did not step',
                affinity.get_affinity(Monster.get_monster_by_id(healer.id)) == 'devoted',
            )

        finally:
            battle_generator.build_and_generate = real_generate
            battle_generator.build_and_stream = real_stream
            dungeon.save_dungeon_state(saved_dungeon_state)
            battle.save_battle_state(saved_battle_state)
            for monster in created:
                for memory in MonsterMemory.query.filter_by(monster_id=monster.id).all():
                    memory.delete()
                fresh = Monster.get_monster_by_id(monster.id)
                if fresh:
                    fresh.delete()

    print('\n' + '=' * 50)
    print(f'PASSED: {PASSED}  FAILED: {FAILED}')
    return FAILED


class _FakeTier:
    def __init__(self, tier):
        self.affinity = tier


if __name__ == '__main__':
    raise SystemExit(main())
