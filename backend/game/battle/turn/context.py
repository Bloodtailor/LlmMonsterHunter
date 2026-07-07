# TurnContext - everything one battle turn shares across its phases:
# the battle state, loaded Monster objects, the location, and the small
# lookups every phase needs. Mutating helpers change `state` in place,
# exactly as the monolithic battle_turn's closures did.

from typing import Any

from backend.core.workflow_steps import WorkflowStep


class TurnContext:
    """Shared state and helpers for one battle_turn execution"""

    def __init__(self, state: dict, step: WorkflowStep, workflow_name: str):
        from backend.game.dungeon import manager as dungeon
        from backend.models.monster import Monster

        self.state = state
        self.step = step
        self.workflow_name = workflow_name

        # Load Monster objects for everyone in the battle
        self.monsters = {}
        for side in ('allies', 'enemies'):
            for monster_id in state.get(side, {}):
                self.monsters[monster_id] = Monster.get_monster_by_id(int(monster_id))

        self.location = dungeon.get_current_location() or {
            'name': 'the dungeon',
            'description': '',
        }

    # ===== LOOKUPS =====

    def entry_name(self, side, monster_id):
        return self.state.get(side, {}).get(str(monster_id), {}).get('name', 'Unknown')

    def find_side(self, monster_id):
        for side in ('allies', 'enemies'):
            if str(monster_id) in self.state.get(side, {}):
                return side
        return None

    def find_by_name(self, name, sides=('allies', 'enemies')):
        """Resolve a monster name (LLM output) to (side, id) among active fighters"""
        from backend.game.battle import manager as battle

        wanted = str(name or '').strip().lower()
        for side in sides:
            for monster_id in battle.active_ids(self.state, side):
                if self.entry_name(side, monster_id).strip().lower() == wanted:
                    return side, monster_id
        return None, None

    def details_of(self, side, monster_id):
        from backend.game.battle.generator import build_monster_battle_details

        monster = self.monsters.get(str(monster_id))
        if monster:
            # Side is baked into the details so the referee always
            # knows who fights for whom
            return build_monster_battle_details(monster, self.state[side][str(monster_id)], side)
        return self.entry_name(side, monster_id)

    # ===== EMISSION =====

    def emit_turn(self, entry: dict[str, Any]):
        """One resolved turn for the frontend's click-through log"""
        from backend.game.battle import manager as battle

        entry['battle_snapshot'] = battle.get_battle_snapshot(self.state)
        self.step.emit_event("action_resolved", {"action_result": entry})

    # ===== IN-PLACE STATE RULES =====

    def record_finishing_blow(
        self, prior_condition, new_condition, target_id, actor_side, actor_id, action, used_name
    ):
        """
        Remember WHO dropped a monster and WITH WHAT (in place) - the
        monster's 'was_defeated' memory names its defeater, and a
        returning grudge can answer that exact move.
        """
        if new_condition != 'incapacitated' or prior_condition == 'incapacitated':
            return
        blows = self.state.get('finishing_blows', {})
        blows[str(target_id)] = {
            'by_id': str(actor_id),
            'by_name': self.entry_name(actor_side, actor_id),
            'action': action,
            'ability_name': used_name,
        }
        self.state['finishing_blows'] = blows

    def apply_resource_deltas(
        self, actor_side, actor_id, target_side, target_id, stamina_delta, mana_delta
    ):
        """
        Spend and restore reserves (in place). Costs (positive deltas)
        always tire the ACTOR; restores (negative deltas) land on the
        TARGET - so a defend rests the defender, and a soothing mist
        aimed at an ally rests the ally.
        """
        from backend.game.battle import manager as battle
        from backend.game.battle.constants import RESOURCE_DELTAS

        for resource, delta in (('stamina', stamina_delta), ('mana', mana_delta)):
            if not delta or delta == 'none':
                continue
            if RESOURCE_DELTAS.get(delta, 0) > 0:
                battle.apply_resource(self.state, actor_side, actor_id, resource, delta)
            else:
                restore_side = target_side or actor_side
                restore_id = target_id or actor_id
                battle.apply_resource(self.state, restore_side, restore_id, resource, delta)

    def default_resource_deltas(self, action, ability):
        """The code's own cost ruling when the referee stays silent"""
        from backend.game.battle.constants import ABILITY_POOL_BY_TYPE

        if action == 'ability' and ability:
            pool = ABILITY_POOL_BY_TYPE.get(ability.ability_type, 'stamina')
            return ('moderate', None) if pool == 'stamina' else (None, 'moderate')
        if action == 'attack':
            return 'minor', None
        if action == 'defend':
            # Standing guard is also catching your breath
            return 'restore_minor', None
        return None, None  # items and talk cost the monster nothing
