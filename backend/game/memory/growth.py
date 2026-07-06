# Growth - Monsters Change Because of What They Lived
# Reflections read a monster's RUN JOURNAL (what it actually did and
# wished) and produce: a clamped stat bump, sometimes a new ability the
# journal justifies, sometimes a REWORDING of an ability's description to
# match how it was truly used (similar length, never longer), and a
# permanent memory. The LLM chooses words; CODE owns every number.

from typing import Dict, Any, List, Optional

# The LLM's tier words -> percent growth. Numbers are code-owned.
GROWTH_STAT_TIERS = {
    'slight': 0.02,
    'notable': 0.05
}

# The LLM's stat words -> Monster columns
GROWTH_STAT_WORDS = {
    'health': 'max_health',
    'attack': 'attack',
    'defense': 'defense',
    'speed': 'speed'
}

LIFETIME_GROWTH_CAP = 0.30   # per stat, across every growth reflection ever
MAX_ABILITIES = 6
REWORD_MAX_RATIO = 1.15      # a reworded description may not outgrow the old one
SPOTLIGHT_CAP = 2

MODE_NOTES = {
    'camp': ("A quiet moment by the campfire, mid-journey. Growth here is a "
             "small, earned step - the journey is not over."),
    'exit': ("The run is over and the party walked out alive. Reflect on the "
             "WHOLE journey - this is the moment lessons settle into strength.")
}

def run_growth_reflection(monster, mode: str, workflow_name: str) -> Optional[Dict[str, Any]]:
    """One LLM call: how this run changed this monster. None on failure."""
    from backend.game.utils import build_and_generate
    from backend.game.monster.context_builder import build_speaker_block
    from backend.game.memory.journal import build_journal_block
    from backend.game.memory.manager import build_memory_block

    try:
        return build_and_generate('growth_reflection', workflow_name, {
            'monster_details': build_speaker_block(monster),
            'run_journal': build_journal_block(monster.id),
            'monster_memories': build_memory_block(monster.id),
            'mode_note': MODE_NOTES.get(mode, MODE_NOTES['camp'])
        })
    except Exception as e:
        print(f"❌ Growth reflection failed for {monster.name}: {e}")
        return None

def apply_growth(monster, reflection: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply a reflection with every clamp enforced in code. Returns a
    summary dict for the workflow response (and the frontend).
    """
    from backend.models.monster_memory import MonsterMemory
    from backend.game.memory.manager import write_memory
    from backend.core.events.monster_events import emit_monster_updated

    applied = {
        'monster_id': monster.id,
        'monster_name': monster.name,
        'reflection': str(reflection.get('reflection') or '').strip(),
        'stat': None, 'tier': None,
        'new_ability': None, 'reworded_ability': None
    }

    # ----- stat bump: word -> column -> clamped percent -----
    stat_word = str(reflection.get('stat', '')).strip().lower()
    tier_word = str(reflection.get('tier', '')).strip().lower()
    column = GROWTH_STAT_WORDS.get(stat_word)
    pct = GROWTH_STAT_TIERS.get(tier_word)
    if column and pct:
        already = MonsterMemory.growth_total_pct(monster.id, column)
        if already + pct <= LIFETIME_GROWTH_CAP:
            old_value = getattr(monster, column) or 0
            setattr(monster, column, max(old_value + 1, round(old_value * (1 + pct))))
            if column == 'max_health':
                monster.current_health = monster.max_health
            applied['stat'], applied['tier'] = stat_word, tier_word
        else:
            pct = None  # capped out - the reflection still counts, the number does not
    else:
        pct = None

    # ----- a new ability, when the journal earned one -----
    wants_ability = str(reflection.get('new_ability', '')).strip().lower() in ('yes', 'true')
    theme = str(reflection.get('ability_theme') or '').strip()
    if wants_ability and theme and len(monster.abilities or []) < MAX_ABILITIES:
        try:
            from backend.game.monster.generator import generate_ability
            from backend.game.memory.journal import get_journal_lines
            recent = '; '.join(get_journal_lines(monster.id)[-3:])
            ability = generate_ability(
                monster,
                growth_context=(f"Grown from this run: {theme}."
                                f" What it lived through: {recent}" if recent else
                                f"Grown from this run: {theme}.")
            )
            applied['new_ability'] = ability.name
        except Exception as e:
            print(f"❌ Growth ability failed for {monster.name}: {e}")

    # ----- rewording: align an ability's words with how it was used -----
    reword_name = str(reflection.get('reword_ability') or '').strip().lower()
    new_description = str(reflection.get('reworded_description') or '').strip()
    if reword_name and reword_name not in ('none', 'null') and new_description:
        target = next(
            (a for a in (monster.abilities or []) if a.name.strip().lower() == reword_name),
            None
        )
        if target and len(new_description) <= int(len(target.description or '') * REWORD_MAX_RATIO):
            target.description = new_description
            target.save()
            applied['reworded_ability'] = target.name

    monster.save()

    # ----- the growth becomes a permanent memory -----
    note = str(reflection.get('memory_note') or '').strip() or applied['reflection'][:200]
    if note:
        write_memory(monster.id, 'growth', note, {
            'stat': GROWTH_STAT_WORDS.get(applied['stat'] or ''),
            'amount_pct': pct or 0,
            'new_ability': applied['new_ability'],
            'reworded': applied['reworded_ability']
        })

    emit_monster_updated(monster.to_dict())
    return applied

def pick_spotlight(party_monsters: List[Any], workflow_name: str) -> List[Any]:
    """
    The 1-2 party monsters whose story mattered most this run (LLM pick,
    validated; fallback: whoever has the fullest journal).
    """
    from backend.game.utils import build_and_generate
    from backend.game.memory.journal import get_journal_lines

    if not party_monsters:
        return []
    if len(party_monsters) <= SPOTLIGHT_CAP:
        return list(party_monsters)

    journal_map = {m: get_journal_lines(m.id) for m in party_monsters}
    fallback = sorted(party_monsters, key=lambda m: len(journal_map[m]), reverse=True)[:1]

    highlights = "\n".join(
        f"- {m.name}: {len(lines)} journal entries. Recent: " +
        ("; ".join(line[:70] for line in lines[-2:]) if lines else "nothing notable")
        for m, lines in journal_map.items()
    )

    try:
        result = build_and_generate('camp_spotlight', workflow_name, {
            'party_names': ", ".join(m.name for m in party_monsters),
            'journal_highlights': highlights
        })
        wanted = [str(n).strip().lower() for n in (result.get('spotlight') or [])]
        picked = [m for m in party_monsters if m.name.strip().lower() in wanted]
        return picked[:SPOTLIGHT_CAP] if picked else fallback
    except Exception as e:
        print(f"❌ Spotlight pick failed - fullest journal steps forward: {e}")
        return fallback

def run_defeat_reflection(party_monsters: List[Any], battle_state: Dict[str, Any],
                          workflow_name: str) -> Optional[str]:
    """
    ONE collective call after a defeat: the lesson the party takes out of
    the dungeon. Writes a shared 'lesson' memory to every member. Returns
    the reflection text (None if even the fallback has nothing to say).
    """
    from backend.game.utils import build_and_generate
    from backend.game.battle.generator import build_recent_log
    from backend.game.state.manager import get_party_details
    from backend.game.memory.manager import write_memory
    from backend.game.memory.journal import get_journal_lines

    if not party_monsters:
        return None

    highlights = "\n".join(
        f"- {m.name}: " + ("; ".join(line[:60] for line in get_journal_lines(m.id)[-2:]) or "fought quietly")
        for m in party_monsters
    )

    reflection_text = None
    note = None
    try:
        result = build_and_generate('defeat_reflection', workflow_name, {
            'party_details': get_party_details(),
            'battle_log': build_recent_log(battle_state),
            'journal_highlights': highlights
        })
        reflection_text = str(result.get('reflection') or '').strip() or None
        note = str(result.get('memory_note') or '').strip() or None
    except Exception as e:
        print(f"❌ Defeat reflection failed - the lesson is survival itself: {e}")

    note = note or "Was carried out of the dungeon in defeat, and lived to remember it."
    for monster in party_monsters:
        write_memory(monster.id, 'lesson', note, {'shared': True})

    return reflection_text
