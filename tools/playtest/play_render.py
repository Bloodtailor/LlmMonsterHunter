# How the step CLI SHOWS things - the player-facing half of play.py.
# Split out when play.py crossed the 500-line ceiling; play.py owns the
# commands and the workflow calls, this owns every word they print:
# the status block, the battle board, and the narration each workflow
# produced (which the CLI used to throw away - see render_result).

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def render_status() -> str:
    """The world as the player sees it - the text agents will read"""
    from backend.game.battle import manager as battle
    from backend.game.dungeon import manager, run_context
    from backend.game.dungeon.goal import goal_snapshot
    from backend.game.state.manager import get_party_monster_ids
    from backend.models.item import Item
    from backend.models.monster import Monster

    lines = ['=== EXPEDITION STATUS ===']

    party_ids = get_party_monster_ids()
    conditions = manager.get_party_conditions()
    resources = manager.get_party_resources()
    party_bits = []
    for monster_id in party_ids:
        monster = Monster.get_monster_by_id(monster_id)
        if not monster:
            continue
        condition = conditions.get(str(monster_id), 'fresh')
        pools = resources.get(str(monster_id)) or {}
        # Reserves exist only inside a run - they refill on entry. Showing
        # 'stamina=?' at home base read as a broken display to a live
        # playtester, so say what is actually true instead.
        if manager.is_in_dungeon():
            pools_text = (
                f"stamina={pools.get('stamina', 'brimming')} mana={pools.get('mana', 'brimming')}"
            )
        else:
            pools_text = 'reserves full (they refill on entering the dungeon)'
        party_bits.append(
            f"  - {monster.name} ({monster.species}) [id {monster.id}] "
            f"condition={condition} {pools_text}"
        )
    lines.append('Party:')
    lines.extend(party_bits or ['  (no party - run new-world first)'])

    items = Item.query.filter(Item.uses_remaining > 0).limit(10).all()
    if items:
        lines.append('Inventory:')
        lines.extend(
            f"  - [id {item.id}] {item.name} (uses left: {item.uses_remaining}) - "
            f"{item.description}"
            for item in items
        )

    battle_state = battle.get_battle_state()
    if battle_state.get('in_battle'):
        lines.extend(_render_battle(battle_state))
        lines.extend(_render_actions_battle(battle_state))
        return '\n'.join(lines)

    if not manager.is_in_dungeon():
        lines.append('Location: outside the dungeon (home base).')
        board = run_context.get_pending_notices()
        if board:
            lines.append('Expedition notices posted:')
            for notice in board:
                lines.append(
                    f"  - {notice.get('id')}: {notice.get('title')} "
                    f"[danger: {notice.get('danger')}] - {notice.get('pitch')}"
                )
            lines.append('Actions: `enter <notice_id>` to answer a notice.')
        else:
            lines.append('Actions: `notices` to post the expedition board.')
        return '\n'.join(lines)

    location = manager.get_current_location() or {}
    lines.append(f"Location: {location.get('name', 'Unknown')} - {location.get('description', '')}")

    goal = goal_snapshot()
    if goal:
        lines.append(f"Run goal ({goal.get('status')}): {goal.get('text')}")

    log_entries = manager.get_dungeon_log_entries()
    if log_entries:
        lines.append('Recently:')
        lines.extend(f'  * {entry}' for entry in log_entries[-6:])

    encounter = manager.get_active_encounter() or {}
    event = encounter.get('event')

    if event == 'monster_dialogue':
        lines.append('A conversation is underway:')
        for spoken in (encounter.get('dialogue') or [])[-6:]:
            lines.append(f"  {spoken.get('speaker')}: \"{spoken.get('text')}\"")
        lines.append(
            'Actions: `act talk "<your words>"` to keep talking, or `act explore` to walk away.'
        )
        return '\n'.join(lines)

    if event == 'location_explore' and encounter.get('monster_ids'):
        names = _monster_names(encounter['monster_ids'])
        lines.append(f"Creatures here (they have NOT noticed you): {names}")
        lines.append(
            'Actions: `act talk "<words>"` to approach, `act sneak` to slip past, '
            '`act ambush` to strike first, `act explore` to move on.'
        )
        return '\n'.join(lines)

    if event == 'location_explore':
        camped = ' (already camped here)' if encounter.get('camped') else ''
        lines.append(f'The area is clear{camped}.')

    # Paths are shown only when NO encounter is active. After an arrival
    # the stored path list still belongs to the PREVIOUS junction (only
    # continue_exploring refreshes it - run_lifecycle.py:161), and the
    # real frontend funnels the player through Continue Exploring at that
    # point. Showing the stale list here let a playtest agent walk paths
    # no real player could see - the CLI now mirrors the frontend.
    actions = []
    if not encounter:
        paths = manager.get_public_paths()
        if paths:
            lines.append('Paths from here:')
            for path_id, path in paths.items():
                marker = ' [EXIT]' if path.get('type') == 'exit' else ''
                lines.append(
                    f"  - {path_id}{marker}: {path.get('name')} - {path.get('description')}"
                )
            actions.append('`act path <path_id>` to take a path')
    if event == 'location_explore' and not encounter.get('camped'):
        actions.append('`act camp` to rest')
    actions.append('`act explore` for fresh paths')
    actions.append('`act ability <monster_id> <ability_id> [target words]`')
    actions.append('`act item <item_id> [target words]`')
    lines.append('Actions: ' + ', '.join(actions) + '.')
    return '\n'.join(lines)


def _render_battle(state: dict) -> list:
    lines = [f"IN BATTLE - phase: {state.get('phase')}"]
    for side, label in (('allies', 'Your side'), ('enemies', 'Enemies')):
        lines.append(f'{label}:')
        for entry_id, entry in (state.get(side) or {}).items():
            flags = []
            if entry.get('fled'):
                flags.append('fled')
            if entry.get('defending'):
                flags.append('defending')
            flag_text = f" ({', '.join(flags)})" if flags else ''
            lines.append(
                f"  - {entry.get('name')} [id {entry_id}] condition={entry.get('condition')}"
                + flag_text
            )
    if state.get('pending_talk'):
        talk = state['pending_talk']
        speaker = (state.get('enemies') or {}).get(str(talk.get('speaker_id')), {})
        lines.append(f"{speaker.get('name', 'An enemy')} says: \"{talk.get('dialogue')}\"")
    return lines


def _render_actions_battle(state: dict) -> list:
    phase = state.get('phase')
    if phase == 'awaiting_player_response':
        return ['Actions: `act reply "<your answer>"`.']
    if phase == 'awaiting_player_turn':
        from backend.models.monster import Monster

        actor_id = state.get('pending_actor')
        actor = Monster.get_monster_by_id(int(actor_id)) if actor_id else None
        ability_bits = ''
        if actor and actor.abilities:
            named = ', '.join(f'"{a.name}"' for a in actor.abilities)
            ability_bits = f' Abilities: {named}.'
        return [
            f"It is {actor.name if actor else 'your monster'}'s turn.{ability_bits}",
            'Actions: `act battle attack|defend [--target "<name>"]`, '
            '`act battle ability --ability "<name>" [--target "<name>"]`, '
            '`act battle custom --text "<what they try>"`, '
            '`act battle talk --text "<words>"`, '
            '`act battle item --item <id> [--target "<name>"]`.',
        ]
    if phase in ('victory', 'defeat'):
        return [f'The battle ended in {phase}. Actions: `act explore` to move on.']
    return ['Actions: `act battle continue` to let the battle open.']


def _monster_names(monster_ids) -> str:
    from backend.models.monster import Monster

    names = []
    for monster_id in monster_ids:
        monster = Monster.get_monster_by_id(int(monster_id))
        if monster:
            names.append(f'{monster.name} ({monster.species}) [id {monster.id}]')
    return ', '.join(names) or 'unknown creatures'


# What each workflow's RESULT carries that the player is meant to read.
# The status block shows the world; these are the words the game wrote
# about what just happened. Until a live playtester pointed out that the
# exit ceremony "generated a chronicle I never saw", the CLI printed the
# state and threw the prose away - so every judgement of narrative
# quality was made on a fraction of the narration.
RESULT_TEXT_FIELDS = (
    ('entry_text', 'ENTERING'),
    ('narration', None),
    ('response', None),
    ('greeting', None),
    ('question', None),
    ('battle_intro', 'BATTLE'),
    ('outcome_text', 'OUTCOME'),
    ('exit_text', 'LEAVING'),
    ('chronicle', 'THE CHRONICLE'),
    ('defeat_reflection', 'WHAT THE PARTY TOOK FROM IT'),
)


def render_result(status: dict) -> str:
    """The narration the workflow produced, as the player should read it"""
    result = (status or {}).get('result') or {}
    if not isinstance(result, dict):
        return ''

    lines = []
    for key, heading in RESULT_TEXT_FIELDS:
        value = result.get(key)
        if isinstance(value, dict):
            value = value.get('reflection') or value.get('text')
        if not value or not str(value).strip():
            continue
        text = str(value).strip()
        lines.append(f"\n--- {heading} ---\n{text}" if heading else text)

    item = result.get('item')
    if isinstance(item, dict) and item.get('name'):
        lines.append(f"\nFOUND: {item['name']} - {item.get('description', '')}")
    cocatok = result.get('cocatok')
    if isinstance(cocatok, dict) and cocatok.get('title'):
        lines.append(f"\nKEEPSAKE: {cocatok['title']} - {cocatok.get('commemoration', '')}")
    joined = result.get('joined_names')
    if joined:
        lines.append(f"\nJOINED THE PARTY: {', '.join(joined)}")
    for growth in result.get('growth') or []:
        if isinstance(growth, dict) and growth.get('reflection'):
            lines.append(
                f"\nGREW: {growth.get('monster_name', 'A companion')} - {growth['reflection']}"
            )
    spoils = result.get('spoils_lost') or {}
    if spoils.get('released_names') or spoils.get('lost_item_names'):
        lines.append(
            "\nLOST WITH THE RUN: "
            + ', '.join(spoils.get('released_names', []) + spoils.get('lost_item_names', []))
        )

    return '\n'.join(lines).strip()


def inherited_world_warning(session: str) -> str:
    """All playtests share one test-DB world, so a session that starts
    without `new-world` silently inherits whatever the last one left -
    mid-run, mid-battle, with someone else's dungeon log. Two live
    playtesters in a row did exactly that and reported the leftovers as
    game behaviour, so the CLI now says so out loud on the first command
    of a session."""
    from backend.game.dungeon import manager
    from backend.game.state.manager import get_party_monster_ids
    from tools.playtest.play import session_path

    if session_path(session).exists():
        return ''
    if not manager.is_in_dungeon() and not get_party_monster_ids():
        return ''
    where = 'MID-RUN' if manager.is_in_dungeon() else 'ALREADY POPULATED'
    return (
        f"\n⚠️  THIS WORLD IS {where} FROM AN EARLIER SESSION. Everything below - "
        "the party, the location, the dungeon log - belongs to whoever played last. "
        "Run `new-world` (then `notices` and `enter`) for a clean expedition.\n"
    )
