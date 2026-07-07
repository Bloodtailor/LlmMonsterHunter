# New Game - the moment the world starts over
# "New Game" is a promise: nothing of the previous world survives it.
# wipe_world() deletes every game-domain row in FK-safe order (children
# before parents) inside ONE transaction - a failure rolls back and the
# old world stands untouched. The three developer log tables
# (generation_logs / llm_logs / image_logs) deliberately survive: they
# are observability, not world state (locked decision,
# docs/plans/new-game-experience.md), and art files on disk stay too.

from backend.core.utils.console import print_success
from backend.models.core import db


def wipe_world() -> dict[str, int]:
    """
    Delete all game-domain rows. Returns per-table deleted-row counts
    (for the service response and the console). Raises on failure after
    rolling back.
    """
    from backend.models.ability import Ability
    from backend.models.active_party import ActiveParty
    from backend.models.chat_message import ChatMessage
    from backend.models.chat_summary import ChatSummary
    from backend.models.chat_thread import ChatThread
    from backend.models.cocatok import CoCaTok
    from backend.models.dungeon_run import DungeonRun
    from backend.models.following_monsters import FollowingMonster
    from backend.models.game_workflow import GameWorkflow
    from backend.models.global_variables import GlobalVariable
    from backend.models.item import Item
    from backend.models.monster import Monster
    from backend.models.monster_evolution import MonsterEvolution
    from backend.models.monster_memory import MonsterMemory

    # Children before parents: everything holding a monsters.id foreign
    # key goes before Monster, and memories (dungeon_runs.id FK) before
    # DungeonRun. Items, CoCaToks, workflows, and globals stand alone.
    wipe_order = (
        ActiveParty,
        FollowingMonster,
        ChatMessage,
        ChatSummary,
        ChatThread,
        MonsterMemory,
        MonsterEvolution,
        Ability,
        Monster,
        DungeonRun,
        Item,
        CoCaTok,
        GameWorkflow,
        GlobalVariable,
    )

    try:
        deleted = {model.__tablename__: model.query.delete() for model in wipe_order}
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    print_success(f"World wiped for a new game ({sum(deleted.values())} rows erased)")

    # Post-commit, so every listener that refetches on this reads the
    # empty world (the frontend's roster state empties itself live)
    from backend.core.events import emit_game_world_erased

    emit_game_world_erased(deleted_rows=deleted)
    return deleted
