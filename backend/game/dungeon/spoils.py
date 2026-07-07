# Provisional Spoils - what a run has gathered but not yet secured
# The design's core tension, enforced: monsters recruited and possessions
# found THIS RUN belong to the party only if they exit alive. Every
# source of spoils records here; defeat and abandonment call
# forfeit_run_spoils() BEFORE the run state is wiped. Victory needs no
# call at all - walking out is what makes the spoils real, and the wipe
# simply drops the tracking lists.
# The released monsters KEEP their memories - that is the fun part, and
# prime returning-monster fuel.

from typing import Any

from backend.game.dungeon import manager

# What a released recruit remembers, by how the run ended
_PARTING_MEMORIES = {
    'defeat': (
        "Joined the party mid-run, but they fell before reaching the "
        "surface - the bond never made it out of the dungeon."
    ),
    'abandoned': (
        "Joined the party mid-run, but they turned back and the bond was left behind in the dark."
    ),
}


# ===== RECORDING (called by every source of spoils) =====


def record_run_recruit(monster_id: int) -> None:
    """A monster joined the party mid-run - provisional until the exit"""
    _record('run_recruits', int(monster_id))


def record_run_item(item_id: int) -> None:
    """An item was found/granted mid-run - provisional until the exit"""
    _record('run_item_ids', int(item_id))


def record_run_cocatok(cocatok_id: int) -> None:
    """A victory keepsake was minted mid-run - provisional until the exit"""
    _record('run_cocatok_ids', int(cocatok_id))


def _record(key: str, value: int) -> None:
    state = manager.get_dungeon_state()
    if not state.get('in_dungeon'):
        return  # sanctuary battles, home flows - nothing at stake
    recorded = state.get(key, [])
    if value not in recorded:
        recorded.append(value)
    state[key] = recorded
    manager.save_dungeon_state(state)


def get_run_spoils() -> dict[str, list[int]]:
    state = manager.get_dungeon_state()
    return {
        'run_recruits': list(state.get('run_recruits', [])),
        'run_item_ids': list(state.get('run_item_ids', [])),
        'run_cocatok_ids': list(state.get('run_cocatok_ids', [])),
    }


# ===== FORFEITURE (defeat and abandonment) =====


def forfeit_run_spoils(reason: str) -> dict[str, Any]:
    """
    The run ended without a living exit: release this run's recruits
    (their memories REMAIN) and take back its items and keepsakes.
    Appends the cost to the dungeon log (call BEFORE the snapshot/wipe).
    Never raises - a failed forfeit must not block the run's ending.
    Returns {'released_names': [...], 'lost_item_names': [...]} for
    payloads and logging.
    """
    released_names: list[str] = []
    lost_item_names: list[str] = []

    try:
        spoils = get_run_spoils()

        # --- recruits: released, but never forgotten ---
        from backend.game.memory.manager import write_memory
        from backend.game.state.manager import remove_following_monster
        from backend.models.monster import Monster

        parting = _PARTING_MEMORIES.get(reason, _PARTING_MEMORIES['defeat'])
        for monster_id in spoils['run_recruits']:
            monster = Monster.get_monster_by_id(monster_id)
            if not monster:
                continue
            remove_following_monster(monster_id)  # clears ActiveParty too
            write_memory(monster_id, 'bond_broken', parting, {'reason': reason})
            released_names.append(monster.name)

        # --- items: taken back by the dungeon ---
        from backend.core.events.inventory_events import emit_inventory_item_consumed
        from backend.models.item import Item

        for item_id in spoils['run_item_ids']:
            item = Item.get_item_by_id(item_id)
            if not item:
                continue
            lost_item_names.append(item.name)
            emit_inventory_item_consumed(item.id, item.name)
            item.delete()

        # --- victory keepsakes: minted mid-run, lost with the run ---
        from backend.core.events.inventory_events import emit_inventory_cocatok_removed
        from backend.models.cocatok import CoCaTok

        for cocatok_id in spoils['run_cocatok_ids']:
            cocatok = CoCaTok.query.get(cocatok_id)
            if not cocatok:
                continue
            emit_inventory_cocatok_removed(cocatok.id, cocatok.title)
            cocatok.delete()

        # The cost goes on the record while the log still exists
        if released_names or lost_item_names:
            costs = []
            if released_names:
                costs.append(f"companions lost: {', '.join(released_names)}")
            if lost_item_names:
                costs.append(f"possessions lost: {', '.join(lost_item_names)}")
            manager.append_dungeon_log(
                f"The run's spoils never left the dungeon ({reason}) - {'; '.join(costs)}."
            )

    except Exception as forfeit_error:
        print(f"❌ Spoils forfeit failed (the run still ends): {forfeit_error}")

    return {'released_names': released_names, 'lost_item_names': lost_item_names}
