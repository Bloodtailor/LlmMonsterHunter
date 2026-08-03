# play.py - the step CLI for agent (and human) playtesting.
#
# Game state lives in the TEST database, so separate invocations form a
# natural turn protocol: `play.py status` shows the world exactly as a
# player would see it (public paths only - hidden events stay hidden),
# `play.py act ...` takes one action through the real workflow queue,
# and the process exits. With the provider row seeded
# (tools/playtest/seed_provider.py) every generation is REAL DeepSeek
# narration; with --stub happy the LLM seam is stubbed for free dry runs.
#
# Usage (from repo root, ./venv/Scripts/python.exe tools/playtest/play.py ...):
#   play.py new-world              stand up player + companions (no LLM)
#   play.py notices                post the expedition board
#   play.py enter notice_2         answer a notice and enter the dungeon
#   play.py status                 where am I, what can I do
#   play.py act path path_1        take a path
#   play.py act talk "We come in peace"
#   play.py act sneak | ambush | camp | explore
#   play.py act battle attack --target "Gorse"
#   play.py act battle custom --text "Kick the brazier over!"
#   play.py act reply "We want no quarrel"
#   play.py act item 3 --target "the sealed door"
#
# Every invocation appends one JSONL line to
# playtest_results/play_sessions/<session>.jsonl (--session, default
# 'default') - the raw transcript Pt-M3's analysis reads.

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import backend  # noqa: F401 - loads .env
from tools.playtest.rig import build_rig, drain_queue, run_workflow


def render_status() -> str:
    """The world as the player sees it - the text agents will read"""
    from backend.game.battle import manager as battle
    from backend.game.dungeon import manager, run_context
    from backend.game.dungeon.goal import goal_snapshot
    from backend.game.state.manager import get_party_monster_ids
    from backend.models.item import Item
    from backend.models.monster import Monster

    lines = ['=== EXPEDITION STATUS ===']

    party_ids = get_party_monster_ids()
    conditions = manager.get_party_conditions()
    resources = manager.get_party_resources()
    party_bits = []
    for monster_id in party_ids:
        monster = Monster.get_monster_by_id(monster_id)
        if not monster:
            continue
        condition = conditions.get(str(monster_id), 'fresh')
        pools = resources.get(str(monster_id)) or {}
        party_bits.append(
            f"  - {monster.name} ({monster.species}) [id {monster.id}] "
            f"condition={condition} stamina={pools.get('stamina', '?')} "
            f"mana={pools.get('mana', '?')}"
        )
    lines.append('Party:')
    lines.extend(party_bits or ['  (no party - run new-world first)'])

    items = Item.query.filter(Item.uses_remaining > 0).limit(10).all()
    if items:
        lines.append('Inventory:')
        lines.extend(
            f"  - [id {item.id}] {item.name} (uses left: {item.uses_remaining}) - "
            f"{item.description}"
            for item in items
        )

    battle_state = battle.get_battle_state()
    if battle_state.get('in_battle'):
        lines.extend(_render_battle(battle_state))
        lines.extend(_render_actions_battle(battle_state))
        return '\n'.join(lines)

    if not manager.is_in_dungeon():
        lines.append('Location: outside the dungeon (home base).')
        board = run_context.get_pending_notices()
        if board:
            lines.append('Expedition notices posted:')
            for notice in board:
                lines.append(
                    f"  - {notice.get('id')}: {notice.get('title')} "
                    f"[danger: {notice.get('danger')}] - {notice.get('pitch')}"
                )
            lines.append('Actions: `enter <notice_id>` to answer a notice.')
        else:
            lines.append('Actions: `notices` to post the expedition board.')
        return '\n'.join(lines)

    location = manager.get_current_location() or {}
    lines.append(f"Location: {location.get('name', 'Unknown')} - {location.get('description', '')}")

    goal = goal_snapshot()
    if goal:
        lines.append(f"Run goal ({goal.get('status')}): {goal.get('text')}")

    log_entries = manager.get_dungeon_log_entries()
    if log_entries:
        lines.append('Recently:')
        lines.extend(f'  * {entry}' for entry in log_entries[-6:])

    encounter = manager.get_active_encounter() or {}
    event = encounter.get('event')

    if event == 'monster_dialogue':
        lines.append('A conversation is underway:')
        for spoken in (encounter.get('dialogue') or [])[-6:]:
            lines.append(f"  {spoken.get('speaker')}: \"{spoken.get('text')}\"")
        lines.append(
            'Actions: `act talk "<your words>"` to keep talking, or `act explore` to walk away.'
        )
        return '\n'.join(lines)

    if event == 'location_explore' and encounter.get('monster_ids'):
        names = _monster_names(encounter['monster_ids'])
        lines.append(f"Creatures here (they have NOT noticed you): {names}")
        lines.append(
            'Actions: `act talk "<words>"` to approach, `act sneak` to slip past, '
            '`act ambush` to strike first, `act explore` to move on.'
        )
        return '\n'.join(lines)

    if event == 'location_explore':
        camped = ' (already camped here)' if encounter.get('camped') else ''
        lines.append(f'The area is clear{camped}.')

    paths = manager.get_public_paths()
    if paths:
        lines.append('Paths from here:')
        for path_id, path in paths.items():
            marker = ' [EXIT]' if path.get('type') == 'exit' else ''
            lines.append(f"  - {path_id}{marker}: {path.get('name')} - {path.get('description')}")
    actions = ['`act path <path_id>` to take a path']
    if event == 'location_explore' and not encounter.get('camped'):
        actions.append('`act camp` to rest')
    actions.append('`act explore` for fresh paths')
    actions.append('`act ability <monster_id> <ability_id> [target words]`')
    actions.append('`act item <item_id> [target words]`')
    lines.append('Actions: ' + ', '.join(actions) + '.')
    return '\n'.join(lines)


def _render_battle(state: dict) -> list:
    lines = [f"IN BATTLE - phase: {state.get('phase')}"]
    for side, label in (('allies', 'Your side'), ('enemies', 'Enemies')):
        lines.append(f'{label}:')
        for entry_id, entry in (state.get(side) or {}).items():
            flags = []
            if entry.get('fled'):
                flags.append('fled')
            if entry.get('defending'):
                flags.append('defending')
            flag_text = f" ({', '.join(flags)})" if flags else ''
            lines.append(
                f"  - {entry.get('name')} [id {entry_id}] condition={entry.get('condition')}"
                + flag_text
            )
    if state.get('pending_talk'):
        talk = state['pending_talk']
        speaker = (state.get('enemies') or {}).get(str(talk.get('speaker_id')), {})
        lines.append(f"{speaker.get('name', 'An enemy')} says: \"{talk.get('dialogue')}\"")
    return lines


def _render_actions_battle(state: dict) -> list:
    phase = state.get('phase')
    if phase == 'awaiting_player_response':
        return ['Actions: `act reply "<your answer>"`.']
    if phase == 'awaiting_player_turn':
        from backend.models.monster import Monster

        actor_id = state.get('pending_actor')
        actor = Monster.get_monster_by_id(int(actor_id)) if actor_id else None
        ability_bits = ''
        if actor and actor.abilities:
            named = ', '.join(f'"{a.name}"' for a in actor.abilities)
            ability_bits = f' Abilities: {named}.'
        return [
            f"It is {actor.name if actor else 'your monster'}'s turn.{ability_bits}",
            'Actions: `act battle attack|defend [--target "<name>"]`, '
            '`act battle ability --ability "<name>" [--target "<name>"]`, '
            '`act battle custom --text "<what they try>"`, '
            '`act battle talk --text "<words>"`, '
            '`act battle item --item <id> [--target "<name>"]`.',
        ]
    if phase in ('victory', 'defeat'):
        return [f'The battle ended in {phase}. Actions: `act explore` to move on.']
    return ['Actions: `act battle continue` to let the battle open.']


def _monster_names(monster_ids) -> str:
    from backend.models.monster import Monster

    names = []
    for monster_id in monster_ids:
        monster = Monster.get_monster_by_id(int(monster_id))
        if monster:
            names.append(f'{monster.name} ({monster.species}) [id {monster.id}]')
    return ', '.join(names) or 'unknown creatures'


def _battle_target_id(state: dict, name: str):
    if not name:
        return None
    wanted = name.strip().lower()
    for side in ('enemies', 'allies'):
        for entry_id, entry in (state.get(side) or {}).items():
            if str(entry.get('name', '')).strip().lower() == wanted:
                return entry_id
    return None


def build_action(args) -> tuple:
    """Map a CLI action onto (workflow_type, context)"""
    from backend.game.battle import manager as battle

    action = args.action
    words = ' '.join(args.words) if args.words else ''

    if action == 'path':
        return 'choose_path', {'path_id': args.words[0] if args.words else ''}
    if action == 'talk':
        return 'respond_to_monster', {'message': words}
    if action == 'sneak':
        return 'sneak_past', {}
    if action == 'ambush':
        return 'surprise_attack', {}
    if action == 'camp':
        return 'setup_camp', {}
    if action == 'explore':
        return 'continue_exploring', {}
    if action == 'reply':
        return 'battle_turn', {'player_response': words}
    if action == 'ability':
        monster_id, ability_id = args.words[0], args.words[1]
        target = ' '.join(args.words[2:]) or 'the surroundings'
        return 'use_dungeon_ability', {
            'monster_id': monster_id,
            'ability_id': ability_id,
            'target': target,
        }
    if action == 'item':
        item_id = args.words[0]
        target = ' '.join(args.words[1:]) or 'the surroundings'
        return 'use_dungeon_item', {'item_id': item_id, 'target': target}
    if action == 'battle':
        state = battle.get_battle_state()
        kind = args.words[0] if args.words else 'continue'
        if kind == 'continue':
            return 'battle_turn', {}
        player_action = {'type': kind}
        target_id = _battle_target_id(state, args.target or '')
        if target_id is not None:
            player_action['target_id'] = target_id
        if kind == 'ability':
            actor_id = state.get('pending_actor')
            from backend.models.monster import Monster

            actor = Monster.get_monster_by_id(int(actor_id)) if actor_id else None
            wanted = (args.ability or '').strip().lower()
            ability = next(
                (a for a in (actor.abilities if actor else []) if a.name.strip().lower() == wanted),
                None,
            )
            if ability:
                player_action['ability_id'] = ability.id
        if kind in ('custom', 'talk'):
            player_action['text'] = args.text or words
        if kind == 'item' and args.item:
            player_action['item_id'] = int(args.item)
        return 'battle_turn', {'player_action': player_action}

    raise SystemExit(f'Unknown action: {action}')


def append_transcript(session: str, entry: dict):
    sessions_dir = REPO_ROOT / 'playtest_results' / 'play_sessions'
    sessions_dir.mkdir(parents=True, exist_ok=True)
    with (sessions_dir / f'{session}.jsonl').open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(entry, default=str) + '\n')


def main() -> int:
    parser = argparse.ArgumentParser(description='Step CLI for playtesting')
    parser.add_argument('--session', default='default', help='transcript name')
    parser.add_argument('--stub', choices=['happy', 'broken', 'chaos'], default=None)
    subparsers = parser.add_subparsers(dest='command', required=True)

    subparsers.add_parser('status')
    world_parser = subparsers.add_parser('new-world')
    world_parser.add_argument('--companions', type=int, default=2)
    subparsers.add_parser('notices')
    enter_parser = subparsers.add_parser('enter')
    enter_parser.add_argument('notice_id')
    act_parser = subparsers.add_parser('act')
    act_parser.add_argument(
        'action',
        choices=[
            'path',
            'talk',
            'sneak',
            'ambush',
            'camp',
            'explore',
            'reply',
            'battle',
            'ability',
            'item',
        ],
    )
    act_parser.add_argument('words', nargs='*')
    act_parser.add_argument('--target', default=None)
    act_parser.add_argument('--ability', default=None)
    act_parser.add_argument('--text', default=None)
    act_parser.add_argument('--item', default=None)

    args = parser.parse_args()

    app, workflow_queue = build_rig()

    stub = None
    if args.stub:
        from tools.playtest.stub_llm import StubLLM

        stub = StubLLM(seed=int(time.time()), mode=args.stub)
        stub.install()

    exit_code = 0
    try:
        with app.app_context():
            from backend.models.core import create_tables

            create_tables()

            workflow_type, context, status = None, None, None

            if args.command == 'status':
                pass

            elif args.command == 'new-world':
                import random as random_module

                from tools.playtest.world_setup import build_world, grant_starter_item

                world = build_world(random_module.Random(), companion_count=args.companions)
                grant_starter_item(random_module.Random())
                print(
                    f"World ready: player id {world['player_id']}, "
                    f"companions {world['companion_ids']}"
                )

            elif args.command == 'notices':
                workflow_type, context = 'generate_expedition_notices', {}

            elif args.command == 'enter':
                from backend.game.dungeon.run_context import get_pending_notice

                notice = get_pending_notice(args.notice_id)
                if not notice:
                    print(f'No such notice: {args.notice_id} (run `notices` first)')
                    return 1
                workflow_type, context = 'enter_dungeon', {'notice': notice}

            elif args.command == 'act':
                workflow_type, context = build_action(args)

            if workflow_type:
                status = run_workflow(workflow_queue, workflow_type, context)
                if status['status'] == 'failed':
                    exit_code = 1
                    print(f"WORKFLOW FAILED: {json.dumps(status.get('error'), default=str)}")

            state_text = render_status()
            print(state_text)

            append_transcript(
                args.session,
                {
                    'at': datetime.now().isoformat(timespec='seconds'),
                    'argv': sys.argv[1:],
                    'workflow': workflow_type,
                    'context': context,
                    'workflow_status': (status or {}).get('status'),
                    'workflow_error': (status or {}).get('error'),
                    'status_text': state_text,
                },
            )

            drain_queue(workflow_queue)
    finally:
        if stub:
            stub.uninstall()

    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
