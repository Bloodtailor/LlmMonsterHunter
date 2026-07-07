# Dungeon Manager - Dungeon Run State
# Owns the persistent dungeon state stored in GlobalVariable ('dungeon_state')
# Hidden information (path events and destinations) lives ONLY here -
# use get_public_paths() for anything that leaves the backend
# Also owns the DUNGEON LOG: the rolling record of everything that has
# happened this run, fed as context into every dungeon LLM generation

from typing import Any, Optional

from backend.game.utils.context_limits import clamp_context
from backend.models.global_variables import GlobalVariable

DUNGEON_STATE_KEY = 'dungeon_state'

# Where the previous run's log survives after the run state is wiped -
# home-base monster chats read it as context
LAST_RUN_LOG_KEY = 'last_run_log'

# Hard safety valve on stored log entries. Old entries are KEPT (rolling
# summaries condense them; prompts clamp further at build time) - this
# only guards against a truly runaway run. If it ever trips, summary
# coverage indexes are shifted down to stay honest.
DUNGEON_LOG_MAX_ENTRIES = 1000

_EMPTY_STATE = {
    'in_dungeon': False,
    'current_location': None,
    'available_paths': {},
    'active_encounter': None,
    'party_conditions': {},  # monster_id: condition - battle damage persists in the run
    'party_resources': {},  # monster_id: {'stamina': word, 'mana': word} - reset only on entry
    'run_journal': {},  # monster_id: [what it did this run] - feeds growth reflections
    'run_id': None,  # the DungeonRun row this run writes memories against
    'seen_monster_ids': [],  # every monster staged this run (excluded from returning pools)
    'dungeon_log': [],  # everything that has happened this run, oldest first
    'dungeon_log_summaries': [],  # [{'through': int, 'text': str}] - rolling condensed batches
    # Provisional spoils - kept only by exiting alive (dungeon/spoils.py)
    'run_recruits': [],  # monster ids recruited this run
    'run_item_ids': [],  # item ids found/granted this run
    'run_cocatok_ids': [],  # victory keepsakes minted this run
}

# ===== CORE STATE ACCESS =====


def get_dungeon_state() -> dict[str, Any]:
    """Get the full dungeon state (includes hidden info - backend use only)"""
    return GlobalVariable.get(DUNGEON_STATE_KEY, dict(_EMPTY_STATE))


def save_dungeon_state(state: dict[str, Any]) -> None:
    """Persist the full dungeon state"""
    GlobalVariable.set(DUNGEON_STATE_KEY, state)


def is_in_dungeon() -> bool:
    return get_dungeon_state().get('in_dungeon', False)


# ===== DUNGEON RUN LIFECYCLE =====


def start_dungeon(location: dict[str, Any], paths: dict[str, Any], run_id: int = None) -> None:
    """Begin a dungeon run at a starting location with its first paths"""
    import copy

    # Deep copy - the fresh state's lists must never alias _EMPTY_STATE's
    state = copy.deepcopy(_EMPTY_STATE)
    state.update(
        {
            'in_dungeon': True,
            'current_location': location,
            'available_paths': paths,
            'run_id': run_id,
        }
    )
    save_dungeon_state(state)


def exit_dungeon() -> None:
    """End the dungeon run and clear all state - including the run's
    modifiers (every run ending passes through here: victory, defeat,
    abandonment)"""
    from backend.game.dungeon.run_context import clear_run_context

    clear_run_context()
    save_dungeon_state(dict(_EMPTY_STATE))


# ===== LOCATION =====


def get_current_location() -> Optional[dict[str, Any]]:
    return get_dungeon_state().get('current_location')


def set_current_location(location: dict[str, Any]) -> None:
    state = get_dungeon_state()
    state['current_location'] = location
    save_dungeon_state(state)


# ===== PATHS =====


def get_path(path_id: str) -> Optional[dict[str, Any]]:
    """Get a single path INCLUDING its hidden event (backend use only)"""
    return get_dungeon_state().get('available_paths', {}).get(path_id)


def set_available_paths(paths: dict[str, Any]) -> None:
    state = get_dungeon_state()
    state['available_paths'] = paths
    save_dungeon_state(state)


# Fields the player must never see - what waits behind each path
_HIDDEN_PATH_FIELDS = ('event', 'destination')


def get_public_paths() -> dict[str, Any]:
    """
    Get available paths SAFE to send to the frontend
    Strips the hidden 'event' and 'destination' fields - the player
    must not know what waits behind each path
    """
    paths = get_dungeon_state().get('available_paths', {})
    return {
        path_id: {key: value for key, value in path.items() if key not in _HIDDEN_PATH_FIELDS}
        for path_id, path in paths.items()
    }


# ===== PARTY CONDITIONS (battle damage persists within the run) =====


def get_party_conditions() -> dict[str, str]:
    """Current conditions of the party for this dungeon run {monster_id: condition}"""
    return get_dungeon_state().get('party_conditions', {})


def set_party_conditions(conditions: dict[str, str]) -> None:
    state = get_dungeon_state()
    state['party_conditions'] = conditions
    save_dungeon_state(state)


# ===== PARTY RESOURCES (stamina/mana pools - reset only on dungeon entry) =====


def get_party_resources() -> dict[str, dict[str, str]]:
    """Current resource pools of the party {monster_id: {'stamina', 'mana'}}"""
    return get_dungeon_state().get('party_resources', {})


def set_party_resources(resources: dict[str, dict[str, str]]) -> None:
    state = get_dungeon_state()
    state['party_resources'] = resources
    save_dungeon_state(state)


# ===== RUN IDENTITY (which DungeonRun row this run belongs to) =====


def get_run_id():
    return get_dungeon_state().get('run_id')


# ===== SEEN MONSTERS (staged this run - excluded from returning pools) =====


def get_seen_monster_ids() -> list[int]:
    return get_dungeon_state().get('seen_monster_ids', [])


def add_seen_monster_ids(monster_ids: list[int]) -> None:
    state = get_dungeon_state()
    if not state.get('in_dungeon'):
        return  # sanctuary battles etc. - there is no run to track
    seen = state.get('seen_monster_ids', [])
    for monster_id in monster_ids:
        if monster_id not in seen:
            seen.append(monster_id)
    state['seen_monster_ids'] = seen
    save_dungeon_state(state)


# ===== ACTIVE ENCOUNTER =====
# Two encounter shapes share this slot:
#   monster_dialogue: {'event', 'monster_ids', 'dialogue': [{'speaker', 'text'}]}
#   location_explore: {'event', 'monster_ids', 'monsters_present', 'camped'}
# An explore encounter converts to a dialogue when the party talks to
# the monsters they found


def get_active_encounter() -> Optional[dict[str, Any]]:
    """Get the active encounter (backend use only)"""
    return get_dungeon_state().get('active_encounter')


def set_active_encounter(encounter: dict[str, Any]) -> None:
    state = get_dungeon_state()
    state['active_encounter'] = encounter
    save_dungeon_state(state)


def clear_active_encounter() -> None:
    state = get_dungeon_state()
    state['active_encounter'] = None
    save_dungeon_state(state)


def append_encounter_dialogue(speaker: str, text: str) -> None:
    """Add one spoken line to the active encounter's dialogue history"""
    state = get_dungeon_state()
    encounter = state.get('active_encounter')
    if not encounter:
        return
    dialogue = encounter.get('dialogue', [])
    dialogue.append({'speaker': speaker, 'text': text})
    encounter['dialogue'] = dialogue
    save_dungeon_state(state)


def get_encounter_dialogue_text() -> str:
    """The encounter conversation as clamped LLM context, oldest first"""
    encounter = get_active_encounter() or {}
    lines = [
        f"{line.get('speaker', 'Someone')}: \"{line.get('text', '')}\""
        for line in encounter.get('dialogue', [])
    ]
    if not lines:
        return "Nothing has been said yet."
    return clamp_context('dialogue_history', "\n".join(lines))


# ===== DUNGEON LOG =====
# The rolling record of the run. Every meaningful moment gets one entry,
# and every dungeon LLM generation receives the (budget-clamped) log as
# context so the story stays coherent across the whole run.
# Old entries are progressively CONDENSED into rolling summaries (see
# game/utils/rolling_summary.py) while recent entries stay verbatim; the
# raw entries themselves are kept for the whole run.


def append_dungeon_log(entry: str) -> None:
    """Record one thing that happened in the dungeon"""
    if not entry or not str(entry).strip():
        return
    state = get_dungeon_state()
    if not state.get('in_dungeon'):
        return
    log = state.get('dungeon_log', [])
    log.append(str(entry).strip())
    dropped = max(len(log) - DUNGEON_LOG_MAX_ENTRIES, 0)
    if dropped:
        # Safety valve tripped - shift summary coverage with the head-drop
        log = log[dropped:]
        state['dungeon_log_summaries'] = [
            {'through': max(int(s.get('through', 0)) - dropped, 0), 'text': s.get('text', '')}
            for s in state.get('dungeon_log_summaries', [])
        ]
    state['dungeon_log'] = log
    save_dungeon_state(state)


def get_dungeon_log_entries() -> list[str]:
    return get_dungeon_state().get('dungeon_log', [])


def get_dungeon_log_summaries() -> list[dict[str, Any]]:
    return get_dungeon_state().get('dungeon_log_summaries', [])


def record_dungeon_log_summary(through: int, text: str) -> None:
    """Store one condensed batch covering entries[0:through]"""
    if not text or not str(text).strip():
        return
    state = get_dungeon_state()
    if not state.get('in_dungeon'):
        return
    summaries = state.get('dungeon_log_summaries', [])
    summaries.append({'through': int(through), 'text': str(text).strip()})
    state['dungeon_log_summaries'] = summaries
    save_dungeon_state(state)


def get_dungeon_log_text() -> str:
    """The dungeon log as clamped LLM context: condensed old + verbatim recent"""
    from backend.game.utils.rolling_summary import compose_history, covered_count

    summaries = get_dungeon_log_summaries()
    entries = get_dungeon_log_entries()
    return compose_history(
        'dungeon_log',
        summaries,
        entries[covered_count(summaries) :],
        'dungeon_log',
        empty_text="The adventure has just begun - nothing has happened yet.",
    )


def queue_log_condense_if_due() -> None:
    """
    Queue a condense_dungeon_log workflow when enough old entries have
    piled up. Called at the tail of the heavier dungeon workflows - the
    sequential worker runs it AFTER the player already has their result.
    Never raises.
    """
    try:
        from backend.game.utils.rolling_summary import covered_count, plan_batch

        state = get_dungeon_state()
        if not state.get('in_dungeon'):
            return
        batch = plan_batch(
            'dungeon_log',
            len(state.get('dungeon_log', [])),
            covered_count(state.get('dungeon_log_summaries', [])),
        )
        if not batch:
            return
        from backend.workflow.workflow_gateway import request_workflow

        request_workflow('condense_dungeon_log', context={})
    except Exception as e:
        print(f"❌ Failed to queue dungeon log condense: {e}")


# ===== LAST RUN LOG (survives the run-state wipe - home chats read it) =====


def snapshot_last_run_log(result: str) -> None:
    """
    Preserve this run's log (raw entries + rolling summaries) before the
    dungeon state is wiped, so conversations back home can look back on
    what happened. Never raises - losing the snapshot never blocks an exit.
    """
    try:
        from datetime import datetime

        state = get_dungeon_state()
        entries = state.get('dungeon_log', [])
        run_number = None
        run_id = state.get('run_id')
        if run_id:
            from backend.models.dungeon_run import DungeonRun

            run = DungeonRun.get_by_id(run_id)
            if run:
                run_number = run.run_number
        GlobalVariable.set(
            LAST_RUN_LOG_KEY,
            {
                'run_id': run_id,
                'run_number': run_number,
                'result': result,
                'entries': entries,
                'summaries': state.get('dungeon_log_summaries', []),
                'saved_at': datetime.utcnow().isoformat(),
            },
        )
    except Exception as e:
        print(f"❌ Failed to snapshot last run log: {e}")


def get_last_run_log() -> Optional[dict[str, Any]]:
    """The previous run's snapshot, or None if no run has finished yet"""
    return GlobalVariable.get(LAST_RUN_LOG_KEY, None)
