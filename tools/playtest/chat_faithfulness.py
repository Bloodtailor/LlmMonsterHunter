# Chat-memory faithfulness - COUNTING, not judgment. An extracted memory
# is faithful when its content words actually appear in the transcript
# stretch it was extracted from; a confabulated memory talks about things
# nobody said. This is the same counting-beats-judgment rule the variety
# metrics live by: never ask a model whether another model was faithful.
#
# Used two ways:
#   - life_gauntlet.py validates the checker itself against planted
#     faithful/fabricated memories (stub mode, zero cost)
#   - live playtests (Px-M3+) score REAL extractions:
#     PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe tools/playtest/chat_faithfulness.py <monster_id>

import re
import sys
from pathlib import Path

# Words too common to count as evidence either way
STOPWORDS = frozenset(
    [
        'a',
        'an',
        'and',
        'are',
        'as',
        'at',
        'be',
        'but',
        'by',
        'for',
        'from',
        'had',
        'has',
        'have',
        'i',
        'in',
        'is',
        'it',
        'its',
        'me',
        'my',
        'of',
        'on',
        'or',
        'our',
        'so',
        'that',
        'the',
        'their',
        'them',
        'they',
        'this',
        'to',
        'was',
        'we',
        'what',
        'when',
        'where',
        'who',
        'will',
        'with',
        'you',
        'your',
    ]
)

# Below this overlap a memory is a confabulation suspect: fewer than half
# of its content words were ever actually said
SUSPECT_THRESHOLD = 0.5


def content_tokens(text: str) -> set:
    """Lowercased word set minus stopwords - the words that carry meaning"""
    words = re.findall(r"[a-z']+", str(text).lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def overlap_score(memory_content: str, transcript_text: str) -> float:
    """What fraction of the memory's content words the transcript contains"""
    memory_words = content_tokens(memory_content)
    if not memory_words:
        return 1.0  # nothing claimed, nothing to betray
    transcript_words = content_tokens(transcript_text)
    return len(memory_words & transcript_words) / len(memory_words)


def score_chat_memories(monster_id: int) -> list[dict]:
    """Score every home_chat memory of a monster against the exact
    message span it was extracted from (details.message_span). Returns
    [{'memory_id', 'kind', 'score', 'suspect', 'content'}] worst-first."""
    from backend.models.chat_message import ChatMessage
    from backend.models.monster_memory import MonsterMemory

    rows = MonsterMemory.query.filter_by(monster_id=int(monster_id)).all()
    scored = []
    for row in rows:
        details = row.details or {}
        if details.get('source') != 'home_chat':
            continue
        span = details.get('message_span') or []
        if len(span) == 2:
            messages = [
                m
                for m in ChatMessage.query.filter_by(monster_id=int(monster_id)).all()
                if span[0] <= m.id <= span[1]
            ]
        else:
            messages = ChatMessage.query.filter_by(monster_id=int(monster_id)).all()
        transcript = ' '.join(m.text for m in messages)
        score = overlap_score(row.content, transcript)
        scored.append(
            {
                'memory_id': row.id,
                'kind': row.kind,
                'score': round(score, 3),
                'suspect': score < SUSPECT_THRESHOLD,
                'content': row.content,
            }
        )
    return sorted(scored, key=lambda entry: entry['score'])


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo_root))
    import backend  # noqa: F401 - loads .env
    from tools.playtest.rig import build_rig

    monster_id = int(sys.argv[1])
    app, _ = build_rig()
    with app.app_context():
        results = score_chat_memories(monster_id)
        suspects = [r for r in results if r['suspect']]
        for entry in results:
            flag = '🚩' if entry['suspect'] else '✅'
            print(f"{flag} {entry['score']:.2f} [{entry['kind']}] {entry['content'][:90]}")
        print(f"\n{len(results)} home-chat memories, {len(suspects)} confabulation suspects")
        return len(suspects)


if __name__ == '__main__':
    raise SystemExit(main())
