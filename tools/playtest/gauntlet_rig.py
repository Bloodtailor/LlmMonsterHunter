# The gauntlet's driving frame - how a directed battle scenario stands
# up a forced fight and steers it turn by turn. battle_gauntlet.py owns
# the scenarios and their assertions; this file owns the machinery they
# share: the stall script (nobody can land a blow), live-state answer
# pickers for the scripted stub, the PASS/FAIL collector, and the Rig
# that submits real battle_turn workflows through the production queue.

import random

from tools.playtest.invariants import check_all
from tools.playtest.rig import run_workflow
from tools.playtest.scripted_stub import ScriptedStub  # noqa: F401 - re-export for scenarios


def scenario_registry():
    """A per-suite (registry, decorator) pair - each gauntlet keeps its
    own scenarios so suites can never collide in a shared namespace"""
    registry = {}

    def scenario(func):
        registry[func.__name__] = func
        return func

    return registry, scenario


def run_suite(icon: str, scenarios: dict, args, wrap_factory=None) -> int:
    """The shared gauntlet runner: fresh world + scripted stub per
    scenario, JSONL failure log, exit code = failed checks. Each suite
    passes its own scenario registry; wrap_factory() may return a
    context manager pinning event rolls suite-wide (the battle gauntlet
    pins monster_battle) - scenarios can still layer their own."""
    import json
    import time
    from contextlib import nullcontext
    from datetime import datetime
    from pathlib import Path

    from tools.playtest.rig import build_rig, drain_queue
    from tools.playtest.world_setup import build_world, grant_starter_item

    repo_root = Path(__file__).resolve().parents[2]
    results_dir = repo_root / 'playtest_results'
    results_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    failures_path = results_dir / f'{args.suite_name}_{stamp}.jsonl'
    failures_file = failures_path.open('w', encoding='utf-8')

    def log(payload: dict):
        failures_file.write(json.dumps(payload, default=str) + '\n')
        failures_file.flush()

    app, queue = build_rig()
    chosen = [args.scenario] if args.scenario else sorted(scenarios)
    total_failed = 0
    started = time.time()

    with app.app_context():
        from backend.models.core import create_tables

        create_tables()

        for scenario_index, name in enumerate(chosen):
            print(f"\n{icon} {name}")
            # The game rolls its own dice on the GLOBAL random module
            # (enemy counts, monster stats) - seed it so a scenario's
            # world is reproducible from the CLI seed alone
            random.seed(args.seed * 1000 + scenario_index)
            rng = random.Random(args.seed)
            stub = ScriptedStub(seed=args.seed, mode='happy')
            checks = Checks(name, log)
            stub.install()
            try:
                with wrap_factory() if wrap_factory else nullcontext():
                    build_world(rng)
                    grant_starter_item(rng)
                    scenarios[name](Rig(queue, rng, checks), stub)
            except Exception as scenario_error:
                checks.ok('scenario ran to completion', False, repr(scenario_error))
            finally:
                drain_queue(queue, timeout_seconds=60)
                stub.uninstall()
            total_failed += checks.failed

    failures_file.close()
    print('\n' + '=' * 50)
    print(f"scenarios={len(chosen)} failed_checks={total_failed} ({time.time() - started:.0f}s)")
    print(f"failure log: {failures_path}")
    return total_failed


def suite_args(scenarios: dict, suite_name: str):
    """The shared CLI: --scenario and --seed, tagged with the suite name"""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', choices=sorted(scenarios), default=None)
    parser.add_argument('--seed', type=int, default=99)
    args = parser.parse_args()
    args.suite_name = suite_name
    return args


# Nobody ever lands a blow - the battle can only end the way the
# scenario script says it ends
STALL = {
    'enemy_turn': {'action': 'defend', 'target': '', 'ability_name': '', 'dialogue': ''},
    'ally_autonomous_turn': {'action': 'defend', 'target': '', 'ability_name': ''},
    'action_resolution': {
        'narration': 'The exchange resolves without a mark.',
        'impact': 'none',
        'stamina_cost': 'none',
        'mana_cost': 'none',
    },
    'freeform_action_resolution': {
        'possible': False,
        'narration': 'Nothing comes of it.',
        'impact': 'none',
        'stamina_cost': 'none',
        'mana_cost': 'none',
    },
}


def pick_enemy(stub):
    """next_turn answer naming a real living enemy (read at call time)"""
    from backend.game.battle import manager as battle

    state = battle.get_battle_state()
    ids = battle.active_ids(state, 'enemies')
    return {'next': state['enemies'][ids[0]]['name'] if ids else ''}


def pick_player(stub):
    """next_turn answer naming the player's own monster"""
    from backend.game.player.manager import get_player_monster_id
    from backend.models.monster import Monster

    monster = Monster.get_monster_by_id(get_player_monster_id())
    return {'next': monster.name if monster else ''}


def hostile_streaks(state: dict):
    """Longest run of consecutive hostile-side entries in turn history"""
    longest = current = 0
    for entry in state.get('turn_history', []):
        current = current + 1 if entry.get('side') == 'hostile' else 0
        longest = max(longest, current)
    return longest


class Checks:
    """Collect PASS/FAIL lines for one scenario"""

    def __init__(self, name: str, log):
        self.name = name
        self.log = log
        self.failed = 0

    def ok(self, label: str, condition: bool, detail=None):
        print(f"    {'PASS' if condition else 'FAIL'}: {label}")
        if not condition:
            self.failed += 1
            self.log({'scenario': self.name, 'check': label, 'detail': detail})

    def invariants(self, status: dict):
        violations = check_all(after_workflow_status=status)
        if violations:
            self.ok('invariants hold', False, violations)


class Rig:
    """One scenario's world: forced-battle entry + battle_turn driving"""

    def __init__(self, queue, rng: random.Random, checks: Checks):
        self.queue = queue
        self.rng = rng
        self.checks = checks

    def start_forced_battle(self):
        """Enter the dungeon and walk into a guaranteed monster_battle
        (the caller has ForcedEvents pinning every path to one)"""
        from backend.game.battle import manager as battle
        from backend.game.dungeon import manager as dungeon

        if not dungeon.is_in_dungeon():
            status = run_workflow(self.queue, 'enter_dungeon', {})
            self.checks.ok(
                'entered the dungeon', status['status'] == 'completed', status.get('error')
            )
        state = dungeon.get_dungeon_state()
        walk = [
            pid
            for pid, p in (state.get('available_paths') or {}).items()
            if p.get('type') != 'exit'
        ]
        status = run_workflow(self.queue, 'choose_path', {'path_id': walk[0]})
        self.checks.invariants(status)
        in_battle = battle.get_battle_state().get('in_battle')
        self.checks.ok('forced path started a battle', bool(in_battle))
        return status

    def settle(self, timeout_seconds: int = 120) -> None:
        """Wait out QUEUED FOLLOW-UP WORK, then re-read the database.

        `run_workflow` waits for the workflow it submitted - and several
        workflows queue a second one behind themselves for the player's
        benefit (chat_housekeeping after a chat, condense_dungeon_log
        after a heavy dungeon action). Those run afterwards, on the
        sequential worker.

        So any assertion about what housekeeping PRODUCED has to settle
        first. Skipping this is not a slow-machine problem you can get
        away with locally: the chat scenario passed here every time and
        failed on CI, which snapshotted the extraction mid-write - one
        memory saved, the watermark not yet advanced, the affinity step
        not yet taken.
        """
        from tools.playtest.rig import drain_queue, refresh_session

        drain_queue(self.queue, timeout_seconds=timeout_seconds)
        refresh_session()

    def turn(self, context: dict) -> dict:
        status = run_workflow(self.queue, 'battle_turn', context)
        self.checks.invariants(status)
        return status

    def drive_to_pending(self, max_workflows: int = 8):
        """battle_turn until control comes back to the player (or fail)"""
        status = self.turn({})
        for _ in range(max_workflows):
            result = status.get('result') or {}
            if result.get('pending'):
                return status
            status = self.turn({})
        return status

    def defend(self, status: dict) -> dict:
        """Answer a pending player turn with a defend (keeps the stall)"""
        actor = (status.get('result') or {}).get('pending_actor')
        return self.turn({'player_action': {'type': 'defend', 'target_id': actor}})

    def talk(self, text: str) -> dict:
        return self.turn({'player_action': {'type': 'talk', 'text': text}})

    def walk_onto(self, event: str, monsters_present=None) -> dict:
        """Regenerate the junction under a pinned event, then take a path.
        Events are stamped onto paths at junction-GENERATION time, so the
        pin must cover enter/continue - not the choose itself."""
        from backend.game.dungeon import manager as dungeon
        from tools.playtest.scripted_stub import ForcedEvents

        with ForcedEvents(event=event, monsters_present=monsters_present, include_exit=False):
            if not dungeon.is_in_dungeon():
                status = run_workflow(self.queue, 'enter_dungeon', {})
                self.checks.ok(
                    'entered the dungeon', status['status'] == 'completed', status.get('error')
                )
            else:
                run_workflow(self.queue, 'continue_exploring', {})
            state = dungeon.get_dungeon_state()
            walk = [
                pid
                for pid, p in (state.get('available_paths') or {}).items()
                if p.get('type') != 'exit'
            ]
            status = run_workflow(self.queue, 'choose_path', {'path_id': walk[0]})
        self.checks.invariants(status)
        return status

    def exit_run(self) -> dict:
        """Walk out alive: force an exit path into the junction, take it"""
        from backend.game.dungeon import manager as dungeon
        from tools.playtest.scripted_stub import ForcedEvents

        with ForcedEvents(event='location_explore', monsters_present=False, include_exit=True):
            for _ in range(3):
                state = dungeon.get_dungeon_state()
                exits = [
                    pid
                    for pid, p in (state.get('available_paths') or {}).items()
                    if p.get('type') == 'exit'
                ]
                if exits:
                    status = run_workflow(self.queue, 'choose_path', {'path_id': exits[0]})
                    self.checks.invariants(status)
                    return status
                run_workflow(self.queue, 'continue_exploring', {})
        self.checks.ok('found an exit path', False)
        return {}
