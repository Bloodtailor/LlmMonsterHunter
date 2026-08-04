# Scripted control on top of the stub seam - the difference between
# random coverage and DIRECTED coverage. The crash driver's StubLLM
# rolls plausible answers; scenarios (battle gauntlet, forced dungeon
# events) need the referee to say exactly what the scenario is testing:
# "the sneak fails", "the enemies yield", "every path holds a battle".
#
# Two tools live here:
#   ScriptedStub  - a StubLLM whose per-template answers can be pinned,
#                   and whose PASSTHROUGH set spends real calls on just
#                   the templates under study
#   ForcedEvents  - a context manager pinning the dungeon's random
#                   event/exit/monster rolls (the Python-side dice)
#
# Both are consumers of existing seams - no game code changes.

from tools.playtest.stub_llm import StubLLM


class ScriptedStub(StubLLM):
    """A StubLLM with a script: {template_name: answer} overrides.

    An answer may be:
      - a dict: returned (copied) on every call
      - a callable(stub) -> dict: evaluated per call - callables run
        inside the workflow worker, so they can read live battle or
        dungeon state to name real combatants
      - a list of the above: consumed one per call, falling back to the
        catalog when exhausted (perfect for "yield on the 3rd exchange")
    Unscripted templates fall through to the normal happy-mode catalog.

    PASSTHROUGH is the corpus trick: name a template (or a few) and only
    THOSE reach the real provider, while the rest of the run stays free.
    A chronicle corpus then costs one real call per run instead of the
    ~40 a fully-live run would spend - the same measure-by-counting
    method, at a fraction of the latency that is the real budget.
    """

    def __init__(self, seed: int = 0, mode: str = 'happy', script: dict = None, passthrough=None):
        super().__init__(seed=seed, mode=mode)
        self.script = dict(script or {})
        self.passthrough = set(passthrough or ())
        self.passthrough_calls = 0

    def set(self, template: str, answer) -> None:
        self.script[template] = answer

    def _fake_text_generation_request(self, prompt: str, prompt_type=None, prompt_name=None, **kw):
        """Real provider for passthrough templates, stub for everything
        else. The real call goes through the ORIGINAL seam, so prompt
        rendering, parsing, logging and token accounting are untouched."""
        if prompt_name in self.passthrough and self._real_request is not None:
            self.passthrough_calls += 1
            return self._real_request(
                prompt, prompt_type=prompt_type, prompt_name=prompt_name, **kw
            )
        return super()._fake_text_generation_request(
            prompt, prompt_type=prompt_type, prompt_name=prompt_name, **kw
        )

    def _fake_wait_for_streamed_text(self, generation_id: int, timeout: int = 0) -> str:
        """Streamed passthrough generations are not in the stub's parked
        texts - they are real queue entries, so wait on them for real"""
        if generation_id not in self._stream_texts and self._real_wait is not None:
            return self._real_wait(generation_id, timeout)
        return super()._fake_wait_for_streamed_text(generation_id, timeout)

    def _fabricate(self, template: str) -> dict:
        pinned = self.script.get(template)
        if isinstance(pinned, list):
            if not pinned:
                return super()._fabricate(template)
            pinned = pinned.pop(0)
        if pinned is None:
            return super()._fabricate(template)
        return dict(pinned(self)) if callable(pinned) else dict(pinned)


class ForcedEvents:
    """Pin the dungeon's Python-side dice while a scenario runs.

    generator.py binds assign_random_event / roll_include_exit at import
    time, so those are patched ON the generator module; explore.py
    resolves its rolls at call time, so those are patched on events.
    Restores everything on exit, even when the scenario raises.
    """

    def __init__(self, event: str = None, monsters_present: bool = None, include_exit: bool = None):
        self.event = event
        self.monsters_present = monsters_present
        self.include_exit = include_exit
        self._saved = {}

    def __enter__(self):
        from backend.game.dungeon import events as events_module
        from backend.game.dungeon import generator as generator_module

        if self.event is not None:
            self._saved['assign'] = generator_module.assign_random_event
            generator_module.assign_random_event = lambda include_returning=False: self.event
        if self.include_exit is not None:
            self._saved['exit'] = generator_module.roll_include_exit
            generator_module.roll_include_exit = lambda: self.include_exit
        if self.monsters_present is not None:
            self._saved['monsters'] = events_module.roll_monsters_present
            events_module.roll_monsters_present = lambda: self.monsters_present
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        from backend.game.dungeon import events as events_module
        from backend.game.dungeon import generator as generator_module

        if 'assign' in self._saved:
            generator_module.assign_random_event = self._saved['assign']
        if 'exit' in self._saved:
            generator_module.roll_include_exit = self._saved['exit']
        if 'monsters' in self._saved:
            events_module.roll_monsters_present = self._saved['monsters']
        return False
