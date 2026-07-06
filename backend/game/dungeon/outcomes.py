# Dialogue Outcomes - What a Monster Decides To Do With the Party
# After any dialogue exchange the LLM picks ONE outcome word; Python
# applies its mechanical consequences here. This is the extension point
# for future outcome mechanics (items, blessings, curses, lasting
# conditions...) - each handler below grows without touching the LLM flow.

from typing import Dict, Any, List

# Every outcome a dialogue turn can produce. The LLM must pick one.
DIALOGUE_OUTCOMES = (
    'continue_dialogue',   # the conversation goes on - the monster expects a reply
    'begin_battle',        # words are over - the monster attacks
    'allow_passage',       # the monster is satisfied - the party may continue
    'reward',              # the monster grants the party something
    'punish',              # the monster exacts a price, short of battle
    'join_party'           # the monster asks to come along - it joins the followers
)

# Outcomes that end the encounter (everything except an ongoing conversation)
RESOLVING_OUTCOMES = tuple(o for o in DIALOGUE_OUTCOMES if o != 'continue_dialogue')

def validate_outcome(outcome: str) -> str:
    """Coerce a raw LLM outcome to a valid one - unknown words keep talking"""
    cleaned = str(outcome or '').strip().lower()
    return cleaned if cleaned in DIALOGUE_OUTCOMES else 'continue_dialogue'

def apply_dialogue_outcome(outcome: str, monster_ids: List[int], location: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Apply the mechanical consequences of a resolved dialogue outcome.
    Returns {'joined_names': [...], 'log_note': str, 'item': dict|None} for
    the workflow to log and report. 'begin_battle' is NOT handled here - the
    workflow owns battle creation (it needs the battle manager and generators).
    """
    from backend.models.monster import Monster

    joined_names = []
    log_note = ''
    item_data = None

    if outcome == 'join_party':
        from backend.models.following_monsters import FollowingMonster
        for monster_id in monster_ids:
            monster = Monster.get_monster_by_id(int(monster_id))
            if monster:
                FollowingMonster.add_follower(int(monster_id))
                joined_names.append(monster.name)
        log_note = f"{', '.join(joined_names) or 'The monster'} joined the party as a follower."

    elif outcome == 'allow_passage':
        log_note = "The monster allowed the party to continue on their way."

    elif outcome == 'reward':
        # The monster grants a real item, themed on the giver and the
        # conversation that earned it (emits inventory.item_added)
        from backend.game.inventory.generator import generate_reward_item
        from backend.game.dungeon.manager import get_encounter_dialogue_text

        giver = next(
            (m for m in (Monster.get_monster_by_id(int(mid)) for mid in monster_ids) if m),
            None
        )
        if giver:
            item = generate_reward_item(
                location or {'name': 'the dungeon', 'description': ''},
                giver,
                get_encounter_dialogue_text()
            )
            item_data = item.to_dict()
            log_note = (f"{giver.name} rewarded the party with {item.name} "
                        f"({item.description})")
        else:
            log_note = "The monster rewarded the party."

    elif outcome == 'punish':
        # FUTURE: worsen conditions / curse / take something here
        log_note = "The monster punished the party, though it let them live."

    _write_outcome_memories(outcome, monster_ids, location, item_data)

    return {'joined_names': joined_names, 'log_note': log_note, 'item': item_data}

# What each resolving outcome writes into the monster's permanent memory.
# The KIND carries the tone (gave_reward is warm, punished_party is sour) -
# no LLM call needed here.
_OUTCOME_MEMORY = {
    'join_party': ('joined_party',
                   "Chose to join the party at {location} after a conversation that moved it."),
    'allow_passage': ('let_party_pass',
                      "Spoke with the party at {location} and let them pass in peace."),
    'reward': ('gave_reward',
               "Was so taken with the party at {location} that it gifted them {gift}."),
    'punish': ('punished_party',
               "Was crossed by the party at {location} and made them pay a price, short of blood.")
}

def _write_outcome_memories(outcome: str, monster_ids: List[int], location: Dict[str, Any], item_data):
    """
    Permanent memories for a resolved dialogue: what the monster decided,
    plus the conversation excerpt that led there. Never raises.
    """
    try:
        from backend.game.memory.manager import write_memory
        from backend.game.memory.journal import append_party_journal
        from backend.game.dungeon.manager import get_encounter_dialogue_text

        if outcome not in _OUTCOME_MEMORY:
            return

        location_name = (location or {}).get('name', 'the dungeon')
        kind, template = _OUTCOME_MEMORY[outcome]
        content = template.format(
            location=location_name,
            gift=(item_data or {}).get('name', 'a gift')
        )

        # The words that earned this outcome, clipped for the record
        exchange = get_encounter_dialogue_text()
        exchange_clip = exchange[-220:] if exchange else ''
        details = {'location': location_name}
        if exchange_clip:
            details['exchange'] = exchange_clip

        for monster_id in monster_ids:
            write_memory(int(monster_id), kind, content, dict(details))
            if exchange_clip:
                write_memory(
                    int(monster_id), 'talked_with_party',
                    f"Traded words with the party at {location_name}: ...{exchange_clip}",
                    {'location': location_name}
                )

        append_party_journal(f"Dialogue at {location_name} ended: {content}")
    except Exception as e:
        print(f"❌ Dialogue outcome memory writing failed: {e}")
