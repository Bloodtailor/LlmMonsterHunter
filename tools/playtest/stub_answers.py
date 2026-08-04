# The stub's answer catalog - one plausible, template-shaped fabricator
# per prompt template (parser catalog: ai/llm/prompts/*.json), plus the
# word pools and outcome weights they draw from. stub_llm.py owns the
# seam and the modes; this file owns WHAT a happy answer looks like.
# Each fabricator receives the StubLLM instance (for its seeded RNG and
# phrase helpers) and returns the parsed_data dict the game would have
# received from a well-behaved model.

# fmt: off
# NOTE: no word here may also be a variety WATCHWORD (variety_metrics.
# SILENCE_WORDS). The stub's vocabulary ends up inside anything measured
# from a stubbed run - a chronicle corpus once read as 88% silence-obsessed
# purely because 'quiet' lived in this list. The harness must never be
# able to answer its own question.
WORDS = [
    'ashen', 'brackish', 'bright', 'cold', 'drowned', 'frozen', 'gilded', 'hollow',
    'iron', 'lichen', 'mossy', 'rusted', 'sunken', 'twisting', 'veiled', 'woven',
]
NOUNS = [
    'archive', 'belfry', 'cistern', 'causeway', 'gallery', 'grotto', 'hall', 'lantern',
    'orchard', 'reliquary', 'spire', 'stair', 'sump', 'vault', 'warren', 'well',
]
CREATURES = [
    'Bram', 'Colm', 'Doss', 'Ember', 'Fenn', 'Gorse', 'Hale', 'Isla', 'Juniper', 'Kest',
    'Lorn', 'Moth', 'Nettle', 'Oriel', 'Pyx', 'Quill', 'Rowan', 'Sorrel', 'Tarn',
    'Umber', 'Vesper', 'Wick',
]
# fmt: on

DIALOGUE_OUTCOME_WEIGHTS = {
    'continue_dialogue': 0.40,
    'allow_passage': 0.16,
    'begin_battle': 0.12,
    'join_party': 0.12,
    'reward': 0.10,
    'punish': 0.10,
}
TALK_DECISION_WEIGHTS = {
    'continue': 0.50,
    'enemies_yield': 0.15,
    'enemies_flee': 0.15,
    'enemies_join': 0.10,
    'party_spared': 0.10,
}
IMPACT_WEIGHTS = {'light': 0.5, 'heavy': 0.25, 'none': 0.1, 'devastating': 0.05, 'heal_light': 0.1}
GARBAGE_SHAPES = (
    {},
    {'unexpected': 42},
    {'name': None, 'description': None},
    {'paths': 'not-a-list'},
    {'notices': [None, 'text', 7]},
    {'outcome': 'ATTACK THEM ALL!!', 'response': 123},
    {'impact': 'obliterating', 'narration': ''},
    {'answer': 'absolutely certainly yes'},
    {'action': {'nested': 'wrong'}},
    {'success': 'maybe'},
)


def _location(stub):
    return {'name': stub._title(), 'description': f"A place of {stub._phrase()}."}


def _item(stub):
    return {
        'name': f"{stub.random.choice(WORDS).title()} Charm",
        'emoji': '🗝️',
        'description': f"A trinket humming with {stub._phrase()}.",
        'uses': stub.random.randint(1, 3),
    }


def _ability(stub):
    return {
        'name': f"{stub.random.choice(WORDS).title()} {stub.random.choice(NOUNS).title()}",
        'description': f"Calls on {stub._phrase()} to turn the moment.",
        'type': stub.random.choice(['attack', 'defense', 'support', 'special', 'utility']),
    }


FABRICATORS = {
    'expedition_notices': lambda s: {
        'notices': [
            {'title': s._title(), 'pitch': f"Word of {s._phrase()}.", 'theme': s._phrase()}
            for _ in range(3)
        ]
    },
    'run_goal': lambda s: {'goal': f"Find {s._phrase()} said to lie in these halls."},
    'goal_check': lambda s: {
        'answer': s._pick({'no': 0.55, 'progress': 0.3, 'complete': 0.15}),
        'note': 'A stub referee note.',
    },
    'random_location': _location,
    'arrival_location': _location,
    'exit_path': lambda s: {
        'name': 'Stair to the Surface',
        'description': 'A worn stair climbing toward daylight.',
    },
    'path_choices': lambda s: {
        'paths': [
            {'name': s._title(), 'description': f"A way toward {s._phrase()}."} for _ in range(4)
        ]
    },
    'monster_blueprint_identity': lambda s: {
        'name': s._name(),
        'domain': s.random.choice(['Beast', 'Spirit', 'Construct', 'Verdant', 'Not-A-Domain']),
        'kingdom': s.random.choice(['Beast', 'Fey', 'Wyrm', 'Shade', 'Mineral']),
        'family': f"{s.random.choice(WORDS).title()}kin",
        'genus': f"{s.random.choice(NOUNS).title()}born",
        'species': f"{s.random.choice(WORDS).title()} {s.random.choice(NOUNS).title()}",
        'race_label': s.random.choice(['beastfolk', 'wisp', 'golem', 'drake']),
        'party_role': s.random.choice(['striker', 'guardian', 'support', 'trickster', 'oddball']),
        'size_class': s.random.choice(['small', 'medium', 'large', 'towering']),
        'lifecycle_stage': s.random.choice(['young', 'adult', 'elder']),
        'creation_mechanism': s.random.choice(['born', 'made', 'condensed', 'awakened']),
    },
    'monster_blueprint_ecology': lambda s: {
        'habitat_primary': s.random.choice(['land', 'water', 'air', 'underground']),
        'habitat_secondary': [],
        'biomes': [s.random.choice(['cavern', 'marsh', 'ruin', 'forest'])],
        'social_structure': s.random.choice(['solitary', 'pair', 'pack', 'colony']),
        'social_notes': '',
        'sustenance': [s.random.choice(['matter', 'emotion', 'light', 'memory'])],
        'feeding_style': s.random.choice(['omnivore', 'herbivore', 'predator', 'siphon']),
        'diet_notes': '',
        'sapience': s.random.choice(['feral', 'clever', 'sapient', 'erudite']),
        'communication': [s.random.choice(['speech', 'gesture', 'scent', 'song'])],
        'elements': [s.random.choice(['fire', 'water', 'earth', 'air', 'shadow', 'light'])],
        'activity_cycle': s.random.choice(['diurnal', 'nocturnal', 'crepuscular']),
        'class_domain': s.random.choice(['warrior', 'mystic', 'artisan', '']),
        'class_discipline': '',
        'class_specialization': '',
    },
    'monster_inner_life': lambda s: {
        'core_wish': f"To keep {s._phrase()} from being forgotten.",
        'motivations': f"Drawn always back to {s._phrase()}.",
        'goals': [f"Reach {s._phrase()}"],
        'beliefs': 'What is mended holds better than what never broke.',
        'moral_character': s.random.choice(['gentle', 'stern', 'sly', 'earnest']),
        'fears': [f"losing {s._phrase()}"],
        'secret': f"Once abandoned {s._phrase()} and never told a soul.",
    },
    'monster_social_self': lambda s: {
        'personality_traits': s.random.sample(
            ['curious', 'wary', 'boastful', 'patient', 'mischievous', 'solemn'], 3
        ),
        'likes': ['rainfall', 'riddles'],
        'dislikes': ['iron bells'],
        'hobbies': ['collecting stones'],
        'profession': 'wayfinder',
        'attitude_toward_strangers': 'measured',
        'responds_well_to': ['honesty'],
        'responds_poorly_to': ['flattery'],
        'recruitment_lever': 'a shared purpose',
        'drawn_to': 'quiet menders',
        'clashes_with': 'braggarts',
        'speech_style': 'short, weighed sentences',
        'battle_line': 'Stand where I can see you!',
    },
    'monster_creative_text': lambda s: {
        'description': f"A creature of {s._phrase()}, watchful and strange.",
        'backstory': f"It wandered out of {s._phrase()} a season ago and never left.",
        'visual_description': f"Hide like {s._phrase()}, eyes like lamplight.",
        'primary_colors': ['slate', 'ember'],
        'distinguishing_features': ['a notched ear', 'a trailing scarf of moss'],
    },
    'generate_ability': _ability,
    'monster_question': lambda s: {
        'greeting': 'Something steps into the light ahead.',
        'question': 'What do you carry, and what would you trade for passage?',
    },
    'monster_dialogue_turn': lambda s: {
        'response': f"It considers, tail flicking toward {s._phrase()}.",
        'outcome': s._pick(DIALOGUE_OUTCOME_WEIGHTS),
    },
    'sneak_attempt': lambda s: {
        'narration': 'The party hugs the wall, breath held.',
        'success': s.random.random() < 0.6,
    },
    'next_turn': lambda s: {'next': '' if s.random.random() < 0.7 else s._name()},
    'enemy_turn': lambda s: {
        'action': s._pick(
            {'attack': 0.6, 'defend': 0.1, 'ability': 0.1, 'talk': 0.15, 'flee': 0.05}
        ),
        'target': '',
        'ability_name': '',
        'dialogue': 'Enough! Why do you trespass here?',
    },
    'ally_autonomous_turn': lambda s: {
        'action': s._pick({'attack': 0.7, 'defend': 0.2, 'ability': 0.1}),
        'target': '',
        'ability_name': '',
    },
    'action_resolution': lambda s: {
        'narration': f"The blow lands near {s._phrase()}.",
        'impact': s._pick(IMPACT_WEIGHTS),
        'stamina_cost': s._pick({'minor': 0.6, 'moderate': 0.3, 'none': 0.1}),
        'mana_cost': 'none',
    },
    'freeform_action_resolution': lambda s: {
        'possible': s.random.random() < 0.7,
        'narration': 'An improvised gambit unfolds.',
        'impact': s._pick(IMPACT_WEIGHTS),
        'stamina_cost': 'minor',
        'mana_cost': 'none',
    },
    'battle_talk': lambda s: {
        'response': 'The creatures pause, weighing the offer.',
        'decision': s._pick(TALK_DECISION_WEIGHTS),
    },
    'treasure_item': _item,
    'reward_item': _item,
    'goal_reward_item': _item,
    'victory_cocatok': lambda s: {
        'title': f"Token of {s._phrase().title()}",
        'emoji': '🏅',
        'color': 'ember',
        'commemoration': 'For a battle weathered together.',
    },
    'growth_reflection': lambda s: {
        'reflection': f"It thinks back on {s._phrase()} and stands a little taller.",
        'stat': s.random.choice(['health', 'attack', 'defense', 'speed', 'luck']),
        'tier': s.random.choice(['minor', 'notable', 'profound', 'legendary']),
        'memory_note': 'Grew a little on the road.',
    },
    'defeat_reflection': lambda s: {
        'reflection': 'The loss sits heavy, and teaches.',
        'memory_note': 'Carried a defeat home.',
    },
    'camp_spotlight': lambda s: {'spotlight': s._name(), 'reason': 'Its story turned today.'},
    'camp_restore': lambda s: {
        'restores': [
            {'name': s._name(), 'stamina': 'restore_major', 'mana': 'restore_minor'}
            for _ in range(2)
        ]
    },
    'returning_transform': lambda s: {
        'disposition': s.random.choice(['warm', 'wary', 'grudging', 'unreadable']),
        'greeting': 'You again. The halls said you might come.',
        'stat_boost': 'minor',
        'battle_line': 'This time, side by side.',
        'grudge_note': '',
        'new_ability': 'no',
        'ability_theme': '',
    },
    'chat_memory_extraction': lambda s: {'memories': []},
    'dungeon_ability_use': lambda s: {
        'narration': 'The gift stirs, briefly.',
        'effect': s._pick({'none': 0.55, 'heal_light': 0.2, 'heal_major': 0.1, 'reveal': 0.15}),
        'stamina_cost': 'minor',
        'mana_cost': 'none',
    },
    'dungeon_item_use': lambda s: {
        'narration': 'The trinket flares once.',
        'effect': s._pick({'none': 0.6, 'heal_light': 0.2, 'heal_major': 0.1, 'reveal': 0.1}),
    },
    'evolution_form': lambda s: {
        'species': f"Greater {s.random.choice(NOUNS).title()}kin",
        'evolved_name': s._name(),
        'family': 'Uncharted',
        'genus': 'Newshape',
        'race_label': 'evolved',
        'size_class': 'large',
        'form_theme': s._phrase(),
    },
    'evolution_persona': lambda s: {'memory_note': 'Changed, and remembers changing.'},
    'evolution_prose': lambda s: {
        'description': 'Its new shape carries the old one inside it.',
        'backstory_addendum': '',
        'visual_description': 'Larger now, lit from within.',
        'primary_colors': ['pearl'],
        'distinguishing_features': ['the old notched ear'],
    },
    'evolution_abilities': lambda s: {'new_ability': 'no', 'ability_theme': ''},
    'player_options': lambda s: {'options': [s._phrase() for _ in range(4)]},
    'player_blueprint': lambda s: {
        'domain': 'Beast',
        'kingdom': 'Human',
        'family': 'Wayfarer',
        'genus': 'Adventurer',
        'species': 'Human Adventurer',
        'race_label': 'human',
        'size_class': 'medium',
        'lifecycle_stage': 'adult',
        'creation_mechanism': 'born',
    },
    'player_persona': lambda s: {
        'personality_traits': ['stubborn', 'kind'],
        'speech_style': 'plain and warm',
        'battle_line': 'Together, now!',
    },
    'player_story': lambda s: {
        'description': 'A traveler with road-worn boots and steady eyes.',
        'backstory': 'Left home chasing a rumor of monsters that talk.',
        'primary_colors': ['russet'],
        'distinguishing_features': ['a crooked smile'],
    },
}
