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
#   happy  - plausible, template-shaped parsed data (stub_answers.py)
#   broken - the generation fails, exercising every deterministic fallback
#   chaos  - garbage that parsed "successfully", exercising normalizers
#
# The 'mixed' driver mode rolls between them so a single run crosses
# golden paths, fallbacks, and hostile shapes the way a bad night would.

import itertools
import random
from typing import Any, Optional

from tools.playtest.stub_answers import CREATURES, FABRICATORS, GARBAGE_SHAPES, NOUNS, WORDS


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
        maker = FABRICATORS.get(template)
        if maker is None:
            self.unknown_templates.add(template)
            return {'name': self._title(), 'description': self._fabricate_text(template)}
        return maker(self)
