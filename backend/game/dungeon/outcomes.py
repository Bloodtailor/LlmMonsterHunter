# Dialogue Outcomes - What a Monster Decides To Do With the Party
# After any dialogue exchange the LLM picks ONE outcome word; Python
# applies its mechanical consequences here. This is the extension point
# for future outcome mechanics (items, blessings, curses, lasting
# conditions...) - each handler below grows without touching the LLM flow.

from typing import Any

# Every outcome a dialogue turn can produce. The LLM must pick one.
DIALOGUE_OUTCOMES = (
    'continue_dialogue',  # the conversation goes on - the monster expects a reply
    'begin_battle',  # words are over - the monster attacks
    'allow_passage',  # the monster is satisfied - the party may continue
    'reward',  # the monster grants the party something
    'punish',  # the monster exacts a price, short of battle
    'join_party',  # the monster asks to come along - it joins the followers
)

# Outcomes that end the encounter (everything except an ongoing conversation)
RESOLVING_OUTCOMES = tuple(o for o in DIALOGUE_OUTCOMES if o != 'continue_dialogue')


def validate_outcome(outcome: str) -> str:
    """Coerce a raw LLM outcome to a valid one - unknown words keep talking"""
    cleaned = str(outcome or '').strip().lower()
    return cleaned if cleaned in DIALOGUE_OUTCOMES else 'continue_dialogue'


def apply_dialogue_outcome(
    outcome: str, monster_ids: list[int], location: dict[str, Any] = None
) -> dict[str, Any]:
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
        from backend.game.dungeon.spoils import record_run_recruit
        from backend.game.state.manager import add_following_monster

        for monster_id in monster_ids:
            monster = Monster.get_monster_by_id(int(monster_id))
            if monster:
                # Provisional until the party exits alive (only NEW
                # followers are at stake). A new follower auto-seats
                # into any open party slot.
                if add_following_monster(int(monster_id))['newly_following']:
                    record_run_recruit(int(monster_id))

                    # Choosing the party AGAIN - with memories of them -
                    # is a reunion; the renewed bond starts a step warmer
                    from backend.game.monster.affinity import step_affinity
                    from backend.models.monster_memory import MonsterMemory

                    if MonsterMemory.query.filter_by(monster_id=int(monster_id)).count() > 0:
                        step_affinity(int(monster_id), 'rejoined_after_memories')
                joined_names.append(monster.name)
        log_note = f"{', '.join(joined_names) or 'The monster'} joined the party as a follower."

        _apply_first_run_recruitment(monster_ids)

    elif outcome == 'allow_passage':
        log_note = "The monster allowed the party to continue on their way."

    elif outcome == 'reward':
        # The monster grants a real item, themed on the giver and the
        # conversation that earned it (emits inventory.item_added)
        from backend.game.dungeon.manager import get_encounter_dialogue_text
        from backend.game.inventory.generator import generate_reward_item

        giver = next(
            (m for m in (Monster.get_monster_by_id(int(mid)) for mid in monster_ids) if m), None
        )
        if giver:
            item = generate_reward_item(
                location or {'name': 'the dungeon', 'description': ''},
                giver,
                get_encounter_dialogue_text(),
            )
            from backend.game.dungeon.spoils import record_run_item

            record_run_item(item.id)  # provisional until the exit
            item_data = item.to_dict()
            log_note = f"{giver.name} rewarded the party with {item.name} ({item.description})"
        else:
            log_note = "The monster rewarded the party."

    elif outcome == 'punish':
        # FUTURE: worsen conditions / curse / take something here
        log_note = "The monster punished the party, though it let them live."

    _write_outcome_memories(outcome, monster_ids, location, item_data)

    return {'joined_names': joined_names, 'log_note': log_note, 'item': item_data}


def _apply_first_run_recruitment(monster_ids: list[int]) -> None:
    """
    The guided first run's turning point: the FIRST companion joins. It
    steps straight into the (empty) active party so the scripted battle
    has an ally, and the fixed goal completes right here - recruited, not
    generated. Never raises; a no-op outside the first run.
    """
    try:
        from backend.game.dungeon.first_run import is_first_run

        if not is_first_run() or not monster_ids:
            return

        from backend.game.dungeon.goal import complete_goal_directly
        from backend.game.state.manager import set_active_party
        from backend.models.active_party import ActiveParty

        # "Empty" means no COMPANION rows - the player character is
        # always in the party and must not block the first recruit
        if not ActiveParty.get_party_monster_ids():
            set_active_party([int(monster_ids[0])])

        complete_goal_directly('The first companion chose to come along.')
    except Exception as first_run_error:
        print(f"❌ First-run recruitment step failed (the join stands): {first_run_error}")


# What each resolving outcome writes into the monster's permanent memory.
# The KIND carries the tone (gave_reward is warm, punished_party is sour) -
# no LLM call needed here.
_OUTCOME_MEMORY = {
    'join_party': (
        'joined_party',
        "Chose to join the party at {location} after a conversation that moved it.",
    ),
    'allow_passage': (
        'let_party_pass',
        "Spoke with the party at {location} and let them pass in peace.",
    ),
    'reward': (
        'gave_reward',
        "Was so taken with the party at {location} that it gifted them {gift}.",
    ),
    'punish': (
        'punished_party',
        "Was crossed by the party at {location} and made them pay a price, short of blood.",
    ),
}


def _write_outcome_memories(
    outcome: str, monster_ids: list[int], location: dict[str, Any], item_data
):
    """
    Permanent memories for a resolved dialogue: what the monster decided,
    plus the conversation excerpt that led there. Never raises.
    """
    try:
        from backend.game.dungeon.manager import get_encounter_dialogue_text
        from backend.game.memory.journal import append_party_journal
        from backend.game.memory.manager import write_memory

        if outcome not in _OUTCOME_MEMORY:
            return

        location_name = (location or {}).get('name', 'the dungeon')
        kind, template = _OUTCOME_MEMORY[outcome]
        content = template.format(
            location=location_name, gift=(item_data or {}).get('name', 'a gift')
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
                    int(monster_id),
                    'talked_with_party',
                    f"Traded words with the party at {location_name}: ...{exchange_clip}",
                    {'location': location_name},
                )

        append_party_journal(f"Dialogue at {location_name} ended: {content}")
    except Exception as e:
        print(f"❌ Dialogue outcome memory writing failed: {e}")
