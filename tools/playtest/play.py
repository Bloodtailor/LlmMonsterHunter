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

# Windows consoles default to cp1252, and the backend prints emoji on
# import - reconfigure stdout/stderr so the CLI works without the
# caller having to know about PYTHONIOENCODING (found by a playtest
# agent that crashed on the very first invocation)
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, 'reconfigure'):
        stream.reconfigure(encoding='utf-8', errors='replace')

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import backend  # noqa: F401 - loads .env
from tools.playtest.play_render import inherited_world_warning, render_result, render_status
from tools.playtest.rig import build_rig, drain_queue, run_workflow


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


def session_path(session: str) -> Path:
    return REPO_ROOT / 'playtest_results' / 'play_sessions' / f'{session}.jsonl'


def append_transcript(session: str, entry: dict):
    path = session_path(session)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as handle:
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
            warning = inherited_world_warning(args.session)

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

            narration = render_result(status)
            state_text = render_status()
            if warning:
                print(warning)
            if narration:
                print(narration)
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
                    'narration': narration,
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
