# Player Character Tests - OFFLINE (no LLM, test DB)
# Exercises Ngx-M2 (docs/plans/new-game-experience.md): the player
# pointer, always-in-party threading (prepend, cap, readiness), every
# exemption (autonomy, affinity ladder, chat target, following,
# evolution, returning pool), battle inheritance through party ids,
# and graceful absence (no pointer = the world before this feature).
#
# Usage: python -m backend.tests.test_player_character   (from project root)

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


def make_monster(name: str, affinity: str = None):
    from backend.models.monster import Monster

    monster = Monster(
        name=name,
        species='Test Species',
        description=f'{name} exists only in this suite.',
        max_health=50,
        attack=10,
        defense=10,
        speed=10,
        affinity=affinity,
    )
    monster.save()
    return monster


def main():
    app = build_test_app()

    with app.app_context():
        from backend.game.chat.manager import chat_eligibility_error
        from backend.game.memory.manager import eligible_returning_ids
        from backend.game.monster import affinity as affinity_module
        from backend.game.monster.evolution_eligibility import evolution_eligibility_error
        from backend.game.player import manager as player_manager
        from backend.game.state import manager as state_manager
        from backend.models.active_party import ActiveParty
        from backend.models.core import create_tables
        from backend.models.following_monsters import FollowingMonster
        from backend.models.global_variables import GlobalVariable
        from backend.models.monster import Monster
        from backend.models.monster_memory import MonsterMemory
        from backend.services import game_state_service

        print('🧪 PLAYER CHARACTER TESTS')
        print('=' * 50)
        create_tables()

        created = []
        try:
            # ===== graceful absence (the world before the feature) =====
            print('\n-- graceful absence --')
            GlobalVariable.delete_key(player_manager.PLAYER_MONSTER_KEY)
            ActiveParty.clear_party()

            check('no pointer reads as no player', player_manager.get_player_monster_id() is None)
            check('no player exists', not player_manager.player_exists())
            check('nothing is the player', not player_manager.is_player_monster(1))
            check('the companion cap stays at 4', state_manager.companion_cap() == 4)
            check(
                'an empty party is not dungeon-ready',
                not state_manager.is_party_ready_for_dungeon(),
            )

            companion = make_monster('Loyal Friend', affinity='trusting')
            wary_one = make_monster('Wary Stranger', affinity='wary')
            created += [companion, wary_one]
            state_manager.set_active_party([companion.id])
            check(
                'a playerless party is just its companions',
                state_manager.get_party_monster_ids() == [companion.id],
            )

            # ===== the pointer =====
            print('\n-- the player pointer --')
            player = make_monster('The Adventurer')
            created.append(player)
            player_manager.set_player_monster(player.id)

            check('the pointer round-trips', player_manager.get_player_monster_id() == player.id)
            check('the player exists', player_manager.player_exists())
            check('the player is the player', player_manager.is_player_monster(player.id))
            check('a companion is not the player', not player_manager.is_player_monster(companion.id))

            # ===== always in the party =====
            print('\n-- always in the party --')
            check(
                'the player leads the party ids',
                state_manager.get_party_monster_ids() == [player.id, companion.id],
            )
            check('the companion cap drops to 3', state_manager.companion_cap() == 3)

            ActiveParty.clear_party()
            check(
                'the player alone is a real party',
                state_manager.get_party_monster_ids() == [player.id],
            )
            check(
                'the player alone is dungeon-ready',
                state_manager.is_party_ready_for_dungeon(),
            )

            state_manager.set_active_party([player.id, companion.id])
            check(
                'the manager strips the player from companion rows',
                ActiveParty.get_party_monster_ids() == [companion.id],
            )

            details = state_manager.get_party_details()
            check(
                'party details lead with the adventurer',
                details.startswith(f'- {player.name}'),
                details[:60],
            )
            check('the adventurer is labeled as such', 'THE ADVENTURER' in details)
            summary = state_manager.get_party_summary()
            check('the summary names the player first', summary.startswith(player.name), summary)

            # ===== the service cap =====
            print('\n-- the companion cap (service) --')
            extras = [make_monster(f'Extra {i}') for i in range(1, 5)]
            created += extras
            result = game_state_service.set_active_party([m.id for m in extras])
            check('4 companions beside a player is refused', result['success'] is False)
            result = game_state_service.set_active_party([m.id for m in extras[:3]])
            check('3 companions beside a player is allowed', result['success'] is True)
            result = game_state_service.set_active_party([player.id, companion.id])
            check(
                'the player id is quietly filtered, not counted',
                result['success'] is True and ActiveParty.get_party_monster_ids() == [companion.id],
            )

            # ===== exemptions =====
            print('\n-- exemptions --')
            player_fresh = Monster.get_monster_by_id(player.id)
            check(
                'the player is never autonomous (affinity unset)',
                not affinity_module.is_autonomous(player_fresh),
            )
            check(
                'a wary companion still is',
                affinity_module.is_autonomous(wary_one),
            )
            check(
                'the player climbs no ladder',
                affinity_module.step_affinity(player.id, 'camp_rest') is None,
            )
            check(
                'its affinity column stays unset',
                Monster.get_monster_by_id(player.id).affinity is None,
            )
            check(
                'its context line names the adventurer',
                'adventurer' in affinity_module.affinity_context_line(player_fresh),
            )

            chat_error = chat_eligibility_error(player.id)
            check('the player is not a chat target', chat_error is not None, str(chat_error))
            evolution_error = evolution_eligibility_error(player.id)
            check('the altar refuses the player', evolution_error is not None, str(evolution_error))
            result = game_state_service.add_following_monster(player.id)
            check('the player cannot follow themself', result['success'] is False)

            # ===== the returning pool =====
            print('\n-- the returning pool --')
            MonsterMemory.add(player.id, 'joined_party', 'The adventurer remembers everything.')
            stranger = make_monster('Old Acquaintance')
            created.append(stranger)
            MonsterMemory.add(stranger.id, 'let_party_pass', 'It let the party pass, once.')

            returning_ids = eligible_returning_ids()
            check('a remembered stranger can return', stranger.id in returning_ids)
            check('the player can never "return"', player.id not in returning_ids)

            # ===== battle inherits the player through party ids =====
            print('\n-- battle --')
            from backend.game.battle import manager as battle_manager

            party_conditions = {
                str(monster_id): {'name': Monster.get_monster_by_id(monster_id).name}
                for monster_id in state_manager.get_party_monster_ids()
            }
            state = battle_manager.start_battle(
                party_conditions, {'999': {'name': 'Test Enemy'}}
            )
            check('the player stands among the allies', str(player.id) in state['allies'])

            battle_manager.apply_impact(state, 'allies', str(player.id), 'devastating')
            battle_manager.apply_impact(state, 'allies', str(player.id), 'devastating')
            battle_manager.apply_impact(state, 'allies', str(player.id), 'devastating')
            check(
                'a fallen player alone is not defeat',
                battle_manager.derive_outcome(state) == 'unresolved',
            )
            for monster_id in list(state['allies']):
                state['allies'][monster_id]['condition'] = 'incapacitated'
            check(
                'the whole party falling is',
                battle_manager.derive_outcome(state) == 'defeat',
            )
            battle_manager.end_battle()

        finally:
            from backend.game.battle.manager import end_battle

            end_battle()
            ActiveParty.clear_party()
            GlobalVariable.delete_key(player_manager.PLAYER_MONSTER_KEY)
            for monster in created:
                FollowingMonster.remove_follower(monster.id)
                for memory in MonsterMemory.query.filter_by(monster_id=monster.id).all():
                    memory.delete()
                fresh = Monster.get_monster_by_id(monster.id)
                if fresh:
                    fresh.delete()

    print('\n' + '=' * 50)
    print(f'PASSED: {PASSED}  FAILED: {FAILED}')
    return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
