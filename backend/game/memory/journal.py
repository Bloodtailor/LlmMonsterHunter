# Run Journal - What Each Party Monster Did This Run
# Short factual lines appended by code during battles and dungeon events
# (actions taken, words spoken, wishes voiced). Growth reflections read
# the journal to see what a monster actually DID - it lives in dungeon
# state and vanishes when the run ends; reflections turn it into
# permanent memories before that.


from backend.game.utils.context_limits import clamp_context

JOURNAL_MAX_LINES = 30    # per monster, oldest dropped first
JOURNAL_LINE_CLIP = 160   # characters per line

def append_journal(monster_id, line: str) -> None:
    """Add one line to a party monster's run journal (no-op outside a run)"""
    try:
        from backend.game.dungeon import manager as dungeon

        if not line or not str(line).strip():
            return
        state = dungeon.get_dungeon_state()
        if not state.get('in_dungeon'):
            return

        journal = state.get('run_journal', {})
        lines = journal.get(str(monster_id), [])
        clipped = str(line).strip()[:JOURNAL_LINE_CLIP]

        # Repeated identical moments add nothing (e.g. attack spam)
        if lines and lines[-1] == clipped:
            return

        lines.append(clipped)
        journal[str(monster_id)] = lines[-JOURNAL_MAX_LINES:]
        state['run_journal'] = journal
        dungeon.save_dungeon_state(state)
    except Exception as e:
        print(f"❌ Failed to append journal for monster {monster_id}: {e}")

def append_party_journal(line: str) -> None:
    """Add the same line to every active-party member's journal"""
    try:
        from backend.game.state.manager import get_party_monster_ids
        for monster_id in get_party_monster_ids():
            append_journal(monster_id, line)
    except Exception as e:
        print(f"❌ Failed to append party journal: {e}")

def get_journal_lines(monster_id) -> list[str]:
    """One monster's journal lines, oldest first"""
    try:
        from backend.game.dungeon import manager as dungeon
        journal = dungeon.get_dungeon_state().get('run_journal', {})
        return journal.get(str(monster_id), [])
    except Exception as e:
        print(f"❌ Failed to read journal for monster {monster_id}: {e}")
        return []

def build_journal_block(monster_id) -> str:
    """A monster's run journal as a clamped LLM context block"""
    lines = get_journal_lines(monster_id)
    if not lines:
        return "It has done nothing notable yet this run."
    return clamp_context('run_journal', "\n".join(f"- {line}" for line in lines))
