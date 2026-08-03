# The stubbed LLM seam for headless crash driving - zero cost, zero net.
#
# Patches exactly two public seams and nothing deeper:
#   - backend.game.utils.prompt_helpers.text_generation_request - the one
#     function every build_and_generate / build_and_stream call resolves
#     at call time, so template rendering (build_prompt) still runs for
#     real and only the model's ANSWER is fabricated.
#   - backend.game.chat.generator.wait_for_streamed_text - streamed
#     generations (camp scenes, chronicles, evolutions) poll the AI queue
#     by generation id; the stub answers from its own registry instead.
#
# Three answer modes, per call:
#   happy  - plausible, template-shaped parsed data (the golden path)
#   broken - the generation fails, exercising every deterministic fallback
#   chaos  - garbage that parsed "successfully", exercising normalizers
#
# The 'mixed' driver mode rolls between them so a single run crosses
# golden paths, fallbacks, and hostile shapes the way a bad night would.

import itertools
import random
from typing import Any, Optional

WORDS = [
    'ashen',
    'bright',
    'cold',
    'drowned',
    'echoing',
    'frozen',
    'gilded',
    'hollow',
    'iron',
    'luminous',
    'mossy',
    'quiet',
    'rusted',
    'sunken',
    'twisting',
    'veiled',
    'woven',
]
NOUNS = [
    'archive',
    'belfry',
    'cistern',
    'causeway',
    'gallery',
    'grotto',
    'hall',
    'lantern',
    'orchard',
    'reliquary',
    'spire',
    'stair',
    'sump',
    'vault',
    'warren',
    'well',
]
CREATURES = [
    'Bram',
    'Colm',
    'Doss',
    'Ember',
    'Fenn',
    'Gorse',
    'Hale',
    'Isla',
    'Juniper',
    'Kest',
    'Lorn',
    'Moth',
    'Nettle',
    'Oriel',
    'Pyx',
    'Quill',
    'Rowan',
    'Sorrel',
    'Tarn',
    'Umber',
    'Vesper',
    'Wick',
]

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


def _passes_required_fields(data: dict, parser_config: dict) -> bool:
    """The same missing/null/empty rule ai/llm/parser.py enforces
    (dotted paths cover the nested_parser's door1.name style)"""
    for field_path in parser_config.get('required_fields') or []:
        current = data
        for part in str(field_path).split('.'):
            if not isinstance(current, dict) or part not in current:
                return False
            current = current[part]
        if current is None or current == '':
            return False
    return True


class StubLLM:
    """Install/uninstall the fake seams; fabricate per-template answers"""

    def __init__(self, seed: int = 0, mode: str = 'happy'):
        self.random = random.Random(seed)
        self.mode = mode
        self.calls_by_template: dict[str, int] = {}
        self.unknown_templates: set[str] = set()
        self._stream_texts: dict[int, str] = {}
        self._fake_ids = itertools.count(9_000_000)
        self._real_request = None
        self._real_wait = None

    # ===== install / uninstall =====

    def install(self):
        from backend.game.chat import generator as chat_generator
        from backend.game.utils import prompt_helpers

        self._real_request = prompt_helpers.text_generation_request
        self._real_wait = chat_generator.wait_for_streamed_text
        prompt_helpers.text_generation_request = self._fake_text_generation_request
        chat_generator.wait_for_streamed_text = self._fake_wait_for_streamed_text

    def uninstall(self):
        from backend.game.chat import generator as chat_generator
        from backend.game.utils import prompt_helpers

        if self._real_request:
            prompt_helpers.text_generation_request = self._real_request
        if self._real_wait:
            chat_generator.wait_for_streamed_text = self._real_wait

    # ===== the two fake seams =====

    def _fake_text_generation_request(
        self,
        prompt: str,
        prompt_type: str = None,
        prompt_name: str = None,
        parser_config: Optional[dict[str, Any]] = None,
        return_early: bool = False,
        **inference_overrides,
    ) -> dict[str, Any]:
        template = prompt_name or 'unknown'
        self.calls_by_template[template] = self.calls_by_template.get(template, 0) + 1
        generation_id = next(self._fake_ids)

        roll = self._roll_mode()

        if return_early:
            # A streamed generation: park the final text for the waiter.
            # A broken stream registers NOTHING - the waiter's "vanished"
            # path is exactly what a dead stream looks like in production.
            if roll != 'broken':
                self._stream_texts[generation_id] = self._fabricate_text(template)
            return {'generation_id': generation_id}

        if roll == 'broken':
            return {
                'generation_id': generation_id,
                'success': False,
                'error': 'stubbed generation failure',
                'text': '',
                'parsing_success': False,
                'parsing_error': 'stubbed generation failure',
                'parsed_data': None,
            }

        wants_json = bool(parser_config) and parser_config.get('type') == 'json'
        if roll == 'chaos' and wants_json:
            parsed = dict(self.random.choice(GARBAGE_SHAPES))
            # Honor the REAL parser's contract: garbage missing a required
            # field could never reach game code as a successful parse -
            # it becomes a parse failure (still hostile, still cheap)
            if not _passes_required_fields(parsed, parser_config):
                return {
                    'generation_id': generation_id,
                    'success': True,
                    'error': None,
                    'text': self._fabricate_text(template),
                    'parsing_success': False,
                    'parsing_error': 'stub chaos: missing required field',
                    'parsed_data': None,
                }
        elif wants_json:
            parsed = self._fabricate(template)
        else:
            parsed = None

        text = self._fabricate_text(template)
        return {
            'generation_id': generation_id,
            'success': True,
            'error': None,
            'text': text,
            'parsing_success': True,
            'parsing_error': None,
            'parsed_data': parsed if wants_json else text,
        }

    def _fake_wait_for_streamed_text(self, generation_id: int, timeout: int = 0) -> str:
        text = self._stream_texts.get(generation_id)
        if text is None:
            raise Exception(f"Generation {generation_id} vanished from the AI queue")
        return text

    # ===== fabrication =====

    def _roll_mode(self) -> str:
        if self.mode in ('happy', 'broken'):
            return self.mode
        if self.mode == 'chaos':
            return self.random.choices(['happy', 'broken', 'chaos'], [0.5, 0.25, 0.25])[0]
        return 'happy'

    def _pick(self, weights: dict[str, float]) -> str:
        return self.random.choices(list(weights), list(weights.values()))[0]

    def _phrase(self) -> str:
        return f"the {self.random.choice(WORDS)} {self.random.choice(NOUNS)}"

    def _title(self) -> str:
        return f"The {self.random.choice(WORDS).title()} {self.random.choice(NOUNS).title()}"

    def _name(self) -> str:
        return self.random.choice(CREATURES)

    def _fabricate_text(self, template: str) -> str:
        return (
            f"[stub:{template}] The party pressed on through {self._phrase()}, "
            f"and the moment passed as such moments do."
        )

    def _fabricate(self, template: str) -> dict[str, Any]:
        maker = _FABRICATORS.get(template)
        if maker is None:
            self.unknown_templates.add(template)
            return {'name': self._title(), 'description': self._fabricate_text(template)}
        return maker(self)


# ===== per-template answer shapes (parser catalog: ai/llm/prompts/*.json) =====


def _location(stub: StubLLM) -> dict[str, Any]:
    return {'name': stub._title(), 'description': f"A place of {stub._phrase()}."}


def _item(stub: StubLLM) -> dict[str, Any]:
    return {
        'name': f"{stub.random.choice(WORDS).title()} Charm",
        'emoji': '🗝️',
        'description': f"A trinket humming with {stub._phrase()}.",
        'uses': stub.random.randint(1, 3),
    }


def _ability(stub: StubLLM) -> dict[str, Any]:
    return {
        'name': f"{stub.random.choice(WORDS).title()} {stub.random.choice(NOUNS).title()}",
        'description': f"Calls on {stub._phrase()} to turn the moment.",
        'type': stub.random.choice(['attack', 'defense', 'support', 'special', 'utility']),
    }


_FABRICATORS = {
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
