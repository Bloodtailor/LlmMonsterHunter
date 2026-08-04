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

SCENARIOS = {}


def scenario(func):
    """Register a gauntlet scenario under its function name"""
    SCENARIOS[func.__name__] = func
    return func


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
