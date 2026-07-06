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

    return {'joined_names': joined_names, 'log_note': log_note, 'item': item_data}
