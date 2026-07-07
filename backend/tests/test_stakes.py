# Stakes Tests - OFFLINE (no LLM, test DB)
# Exercises Game Loop M4: provisional spoils. Monsters recruited and
# possessions gained mid-run are kept only by exiting alive - defeat and
# abandonment release the recruits (memories REMAIN) and take back the
# items and keepsakes. Pre-run followers are never at stake.
#
# Usage: python -m backend.tests.test_stakes   (from project root)

import copy

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


def _make_monster(name: str):
    from backend.models.monster import Monster

    monster = Monster(
        name=name,
        species='Test Species',
        description='A creature that exists only inside the stakes suite.',
        max_health=50,
        attack=10,
        defense=10,
        speed=10,
    )
    monster.save()
    return monster


def _make_item(name: str):
    from backend.models.item import Item

    item = Item(name=name, description='A trinket for the stakes suite.', uses_remaining=1)
    item.save()
    return item


def _make_cocatok(title: str):
    from backend.models.cocatok import CoCaTok

    cocatok = CoCaTok(title=title, commemoration='A victory that exists only in this suite.')
    cocatok.save()
    return cocatok


def _in_dungeon_state(manager):
    state = copy.deepcopy(manager._EMPTY_STATE)
    state.update(
        {
            'in_dungeon': True,
            'current_location': {'name': 'Stakes Hall', 'description': ''},
            'dungeon_log': ['The party entered.'],
        }
    )
    manager.save_dungeon_state(state)


def main():
    app = build_test_app()

    with app.app_context():
        from backend.game.dungeon import manager, spoils
        from backend.models.cocatok import CoCaTok
        from backend.models.core import create_tables
        from backend.models.following_monsters import FollowingMonster
        from backend.models.item import Item
        from backend.models.monster import Monster
        from backend.models.monster_memory import MonsterMemory

        print('🧪 STAKES TESTS')
        print('=' * 50)
        create_tables()

        saved_state = manager.get_dungeon_state()
        created_monsters, created_items, created_cocatoks = [], [], []

        try:
            # ===== recording only counts inside a run =====
            print('\n-- recording is run-scoped --')
            manager.save_dungeon_state(copy.deepcopy(manager._EMPTY_STATE))
            spoils.record_run_recruit(12345)
            check(
                'no run -> nothing records',
                spoils.get_run_spoils()['run_recruits'] == [],
            )

            _in_dungeon_state(manager)
            recruit = _make_monster('Provisional Pal')
            created_monsters.append(recruit)
            veteran = _make_monster('Old Friend')
            created_monsters.append(veteran)
            item = _make_item('Glimmering Bauble')
            created_items.append(item)
            keepsake = _make_cocatok('First Blood in the Stakes Hall')
            created_cocatoks.append(keepsake)

            # The veteran was a follower BEFORE the run - never at stake
            FollowingMonster.add_follower(veteran.id)

            # The run gathers its provisional spoils
            FollowingMonster.add_follower(recruit.id)
            spoils.record_run_recruit(recruit.id)
            spoils.record_run_item(item.id)
            spoils.record_run_cocatok(keepsake.id)

            recorded = spoils.get_run_spoils()
            check('recruit recorded', recorded['run_recruits'] == [recruit.id])
            check('item recorded', recorded['run_item_ids'] == [item.id])
            check('keepsake recorded', recorded['run_cocatok_ids'] == [keepsake.id])

            spoils.record_run_item(item.id)
            check(
                'double-recording stays unique',
                spoils.get_run_spoils()['run_item_ids'] == [item.id],
            )

            # ===== defeat: the spoils never leave the dungeon =====
            print('\n-- defeat forfeits the run spoils --')
            result = spoils.forfeit_run_spoils('defeat')

            check(
                'the provisional recruit was released',
                not FollowingMonster.is_following(recruit.id),
            )
            check(
                'the pre-run follower was untouched',
                FollowingMonster.is_following(veteran.id),
            )
            check('the run item was taken back', Item.get_item_by_id(item.id) is None)
            check('the run keepsake was taken back', CoCaTok.query.get(keepsake.id) is None)
            check(
                'the forfeit reports what it cost',
                result['released_names'] == ['Provisional Pal']
                and result['lost_item_names'] == ['Glimmering Bauble'],
            )

            memories = MonsterMemory.query.filter_by(monster_id=recruit.id).all()
            check(
                'the released recruit REMEMBERS the broken bond',
                any(m.kind == 'bond_broken' for m in memories),
                f'kinds: {[m.kind for m in memories]}',
            )
            log_text = ' '.join(manager.get_dungeon_log_entries())
            check('the cost went on the record', 'Provisional Pal' in log_text)

            # ===== victory: exiting alive keeps everything =====
            print('\n-- a living exit keeps the spoils --')
            _in_dungeon_state(manager)
            survivor = _make_monster('Kept Companion')
            created_monsters.append(survivor)
            kept_item = _make_item('Kept Bauble')
            created_items.append(kept_item)

            FollowingMonster.add_follower(survivor.id)
            spoils.record_run_recruit(survivor.id)
            spoils.record_run_item(kept_item.id)

            # The victory exit calls NO forfeit - the wipe drops tracking
            manager.exit_dungeon()

            check(
                'victory exit keeps the recruit',
                FollowingMonster.is_following(survivor.id),
            )
            check(
                'victory exit keeps the item',
                Item.get_item_by_id(kept_item.id) is not None,
            )
            check(
                'the tracking lists are gone with the run',
                spoils.get_run_spoils()['run_recruits'] == [],
            )

            # ===== abandonment forfeits like defeat =====
            print('\n-- abandonment forfeits too --')
            _in_dungeon_state(manager)
            deserter = _make_monster('Left Behind')
            created_monsters.append(deserter)
            FollowingMonster.add_follower(deserter.id)
            spoils.record_run_recruit(deserter.id)

            spoils.forfeit_run_spoils('abandoned')
            check(
                'abandonment releases the recruit',
                not FollowingMonster.is_following(deserter.id),
            )
            abandoned_memories = MonsterMemory.query.filter_by(
                monster_id=deserter.id, kind='bond_broken'
            ).all()
            check(
                "the abandoned recruit's memory says the party turned back",
                any('turned back' in (m.content or '') for m in abandoned_memories),
            )

            # ===== an interrupted session sweeps with a story =====
            print('\n-- the interrupted-run sweep (title screen Continue) --')
            from backend.services import dungeon_service

            _in_dungeon_state(manager)
            stranded = _make_monster('Stranded Mid-Run')
            created_monsters.append(stranded)
            FollowingMonster.add_follower(stranded.id)
            spoils.record_run_recruit(stranded.id)

            result = dungeon_service.abandon_run(interrupted=True)
            check('the sweep reports the run closed', result.get('abandoned') is True)
            check('the world is out of the dungeon', not manager.is_in_dungeon())
            check(
                'the stranded recruit was released',
                not FollowingMonster.is_following(stranded.id),
            )
            last_run = manager.get_last_run_log() or {}
            check(
                'the unknown force made it into the run story',
                any('unknown force' in str(entry) for entry in last_run.get('entries', [])),
            )

        finally:
            # Leave no debris in the shared test DB
            for monster in created_monsters:
                FollowingMonster.remove_follower(monster.id)
                for memory in MonsterMemory.query.filter_by(monster_id=monster.id).all():
                    memory.delete()
                fresh = Monster.get_monster_by_id(monster.id)
                if fresh:
                    fresh.delete()
            for item in created_items:
                fresh = Item.get_item_by_id(item.id)
                if fresh:
                    fresh.delete()
            for cocatok in created_cocatoks:
                fresh = CoCaTok.query.get(cocatok.id)
                if fresh:
                    fresh.delete()
            manager.save_dungeon_state(saved_state)

    print('\n' + '=' * 50)
    print(f'PASSED: {PASSED}  FAILED: {FAILED}')
    return FAILED


if __name__ == '__main__':
    raise SystemExit(main())
