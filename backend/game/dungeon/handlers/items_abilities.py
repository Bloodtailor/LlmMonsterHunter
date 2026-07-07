# Out-of-battle ability and item use - the dungeon referee decides what
# actually happens (heals land, keen senses reveal true path hints, most
# odd attempts fizzle). Shared target/effect/resource logic lives here too.

from typing import Any

from backend.core.utils.responses import success_response
from backend.core.utils.validation import require_keys
from backend.core.workflow_steps import WorkflowStep

# ===== SHARED TARGET / EFFECT / RESOURCE LOGIC =====


def resolve_dungeon_target(context: dict, manager, location: dict):
    """
    Describe an out-of-battle target and gather any secret knowledge
    (paths know their hidden destination - a perceptive use can hint at it).
    Shared by the ability and item dungeon-referee workflows.
    Returns (target_type, target_id, target_label, target_description, secret_knowledge)
    """
    from backend.game.dungeon.generator import build_monsters_details
    from backend.models.monster import Monster

    target_type = str(context.get('target_type') or 'location')
    target_id = context.get('target_id')
    target_text = str(context.get('target_text') or '').strip()
    secret_knowledge = ''

    if target_type == 'path' and target_id:
        path = manager.get_path(str(target_id))
        if not path:
            raise Exception(f"Unknown path: {target_id}")
        target_label = f"the path '{path.get('name', 'unknown')}'"
        target_description = (
            f"A path leading onward: {path.get('name', 'unknown')} - {path.get('description', '')}"
        )
        if path.get('type') == 'exit':
            secret_knowledge = "This path truly leads OUT of the dungeon, back to the surface."
        else:
            destination = path.get('destination') or {}
            secret_knowledge = (
                f"Beyond this path lies: {destination.get('name', 'an unknown place')} - "
                f"{destination.get('description', '')}"
            )

    elif target_type == 'monster' and target_id:
        target_monster = Monster.get_monster_by_id(int(target_id))
        if not target_monster:
            raise Exception(f"Unknown monster: {target_id}")
        condition = manager.get_party_conditions().get(str(target_monster.id))
        condition_note = f" Its current condition: {condition}." if condition else ""
        target_label = target_monster.name
        target_description = (
            f"A monster.{condition_note}\n{build_monsters_details([target_monster])}"
        )

    elif target_type == 'custom' and target_text:
        target_label = target_text
        target_description = f"The player describes the target as: {target_text}"

    else:
        target_label = f"the location ({location.get('name', 'this place')})"
        target_description = (
            f"The location itself: {location.get('name', 'this place')} - "
            f"{location.get('description', '')}"
        )

    return target_type, target_id, target_label, target_description, secret_knowledge


def apply_party_heal_effect(effect: str, target_type: str, target_id, manager) -> str:
    """Healing effects stick only to party members; returns the (possibly
    downgraded) effect. Shared by the ability and item workflows."""
    from backend.game.battle.constants import CONDITION_LADDER, IMPACT_STEPS

    if effect in ('heal_light', 'heal_major') and target_type == 'monster':
        conditions = manager.get_party_conditions()
        key = str(target_id)
        if key in conditions:
            current_index = CONDITION_LADDER.index(conditions.get(key, 'fresh'))
            new_index = max(0, min(len(CONDITION_LADDER) - 1, current_index + IMPACT_STEPS[effect]))
            conditions[key] = CONDITION_LADDER[new_index]
            manager.set_party_conditions(conditions)
        else:
            effect = 'none'  # healing only sticks to the party
    return effect


def apply_dungeon_resource_deltas(
    manager, actor, ability, stamina_delta, mana_delta, target_type, target_id
):
    """
    Out-of-battle resource accounting. The referee's words rule; when it
    stays silent on both pools, the ability's type picks the pool and the
    cost is moderate. Costs tire the ACTOR; restores land on a party-member
    target (else the actor). Pools live in dungeon party_resources.
    """
    from backend.game.battle.constants import (
        ABILITY_POOL_BY_TYPE,
        BRIMMING,
        RESOURCE_DELTAS,
        RESOURCE_LADDER,
        full_resources,
    )
    from backend.game.state.manager import get_party_monster_ids

    if stamina_delta is None and mana_delta is None:
        pool = ABILITY_POOL_BY_TYPE.get(ability.ability_type, 'stamina')
        stamina_delta, mana_delta = ('moderate', None) if pool == 'stamina' else (None, 'moderate')

    resources = manager.get_party_resources()

    def step_pool(monster_id, resource, delta_word):
        pools = resources.get(str(monster_id))
        if pools is None:
            pools = full_resources()
        steps = RESOURCE_DELTAS.get(delta_word, 0)
        current_index = RESOURCE_LADDER.index(pools.get(resource, BRIMMING))
        new_index = max(0, min(len(RESOURCE_LADDER) - 1, current_index + steps))
        pools[resource] = RESOURCE_LADDER[new_index]
        resources[str(monster_id)] = pools

    restore_target_id = actor.id
    if target_type == 'monster' and target_id and int(target_id) in get_party_monster_ids():
        restore_target_id = int(target_id)

    for resource, delta in (('stamina', stamina_delta), ('mana', mana_delta)):
        if not delta or delta == 'none':
            continue
        if RESOURCE_DELTAS.get(delta, 0) > 0:
            step_pool(actor.id, resource, delta)
        else:
            step_pool(restore_target_id, resource, delta)

    manager.set_party_resources(resources)


# ===== THE WORKFLOW BODIES =====


def run_use_dungeon_ability(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """A party monster uses an ability on anything outside battle"""
    workflow_name = 'use_dungeon_ability'

    from backend.game.dungeon import manager
    from backend.game.dungeon.generator import build_monsters_details, resolve_dungeon_ability
    from backend.models.monster import Monster

    # Step 0 - validate required keys
    step.emit("validate_context")
    require_keys(context, ["monster_id", "ability_id"])

    actor = Monster.get_monster_by_id(int(context['monster_id']))
    if not actor:
        raise Exception("Unknown monster")
    ability = next((a for a in (actor.abilities or []) if a.id == context['ability_id']), None)
    if not ability:
        raise Exception(f"{actor.name} does not have that ability")

    location = manager.get_current_location() or {'name': 'the dungeon', 'description': ''}

    # Step 1 - describe the target and gather any secret knowledge
    step.emit("resolve_target")
    target_type, target_id, target_label, target_description, secret_knowledge = (
        resolve_dungeon_target(context, manager, location)
    )

    # Step 2 - the dungeon referee judges what actually happens
    step.emit("resolve_ability")
    result = resolve_dungeon_ability(
        location,
        build_monsters_details([actor]),
        ability.name,
        ability.description,
        target_description,
        secret_knowledge,
        workflow_name,
    )

    # Step 3 - apply any mechanical effect (only party members heal)
    step.emit("apply_effect")
    effect = apply_party_heal_effect(result['effect'], target_type, target_id, manager)

    # Step 4 - the ability drains (or restores) reserves. Costs hit the
    # actor; restores land on a party-member target, else the actor.
    step.emit("apply_resource_costs")
    apply_dungeon_resource_deltas(
        manager,
        actor,
        ability,
        result.get('stamina_delta'),
        result.get('mana_delta'),
        target_type,
        target_id,
    )

    manager.append_dungeon_log(
        f"{actor.name} used {ability.name} on {target_label}: {result['narration']}"
    )
    from backend.game.memory.journal import append_journal

    append_journal(
        actor.id,
        f"Used {ability.name} on {target_label} outside battle: {result['narration'][:100]}",
    )

    return success_response(
        {
            "narration": result['narration'],
            "effect": effect,
            "party_conditions": manager.get_party_conditions(),
            "party_resources": manager.get_party_resources(),
        }
    )


def run_use_dungeon_item(context: dict, step: WorkflowStep) -> dict[str, Any]:
    """The party uses an inventory item on anything outside battle"""
    workflow_name = 'use_dungeon_item'

    from backend.game.dungeon import manager
    from backend.game.dungeon.generator import resolve_dungeon_item
    from backend.game.inventory.manager import spend_item_use
    from backend.models.item import Item

    # Step 0 - validate required keys
    step.emit("validate_context")
    require_keys(context, ["item_id"])

    item = Item.get_item_by_id(int(context['item_id']))
    if not item or item.uses_remaining < 1:
        raise Exception("That item is not in the party's inventory")

    location = manager.get_current_location() or {'name': 'the dungeon', 'description': ''}

    # Step 1 - describe the target and gather any secret knowledge
    step.emit("resolve_target")
    target_type, target_id, target_label, target_description, secret_knowledge = (
        resolve_dungeon_target(context, manager, location)
    )

    # Step 2 - the dungeon referee judges what actually happens
    step.emit("resolve_item")
    result = resolve_dungeon_item(
        location, item, target_description, secret_knowledge, workflow_name
    )

    # Step 3 - apply any mechanical effect (only party members heal)
    step.emit("apply_effect")
    effect = apply_party_heal_effect(result['effect'], target_type, target_id, manager)

    # Step 4 - one use is spent no matter what came of it
    # (emits inventory.item_updated or inventory.item_consumed)
    step.emit("spend_item_use")
    item_name = item.name
    spend_result = spend_item_use(item)
    step.data.update({"item_spend": spend_result})

    manager.append_dungeon_log(
        f"The party used {item_name} on {target_label}: {result['narration']}"
    )

    return success_response(
        {
            "narration": result['narration'],
            "effect": effect,
            "item_spend": spend_result,
            "party_conditions": manager.get_party_conditions(),
        }
    )
