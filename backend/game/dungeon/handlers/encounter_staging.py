# Dressing a freshly generated encounter monster - abilities and card
# art - WITHOUT letting that dressing end the expedition.
#
# The party has already arrived by the time these run: choose_path has
# set the new location. Anything that raises from here aborts the
# workflow after the move, leaving the player standing in a room with no
# encounter and no way onward. That is exactly what happened in a real
# playthrough: one ability generation returned prose instead of JSON
# three times running, and the run became unplayable.
#
# So the rule is: a monster is allowed to arrive with one ability, or
# none, or no portrait. It is never allowed to take the run down with
# it. The failure is printed and lives on in the generation log; the
# expedition continues.

MAX_ABILITIES_PER_ENCOUNTER_MONSTER = 2


def equip_encounter_monster(monster, step=None, ability_count: int = None) -> dict:
    """Give a new encounter monster its abilities and art, defensively.

    Returns {'abilities': int, 'art': bool, 'failures': [str]} so callers
    can report what the moment actually managed to produce.
    """
    from backend.game.monster.card_art import generate_card_art
    from backend.game.monster.generator import generate_ability

    wanted = MAX_ABILITIES_PER_ENCOUNTER_MONSTER if ability_count is None else ability_count
    outcome = {'abilities': 0, 'art': False, 'failures': []}

    for index in range(wanted):
        if step is not None:
            step.emit('generate_first_ability' if index == 0 else 'generate_second_ability')
        try:
            generate_ability(monster)
            outcome['abilities'] += 1
        except Exception as ability_error:
            outcome['failures'].append(f"ability {index + 1}: {ability_error}")
            print(
                f"⚠️ {monster.name} arrives without ability {index + 1} "
                f"(the expedition continues): {ability_error}"
            )

    if step is not None:
        step.emit('generate_card_art')
    try:
        generate_card_art(monster)
        outcome['art'] = True
    except Exception as art_error:
        outcome['failures'].append(f"card art: {art_error}")
        print(
            f"⚠️ {monster.name} arrives without a portrait (the expedition continues): {art_error}"
        )

    return outcome
