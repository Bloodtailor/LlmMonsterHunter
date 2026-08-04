# Scripted control on top of the stub seam - the difference between
# random coverage and DIRECTED coverage. The crash driver's StubLLM
# rolls plausible answers; scenarios (battle gauntlet, forced dungeon
# events) need the referee to say exactly what the scenario is testing:
# "the sneak fails", "the enemies yield", "every path holds a battle".
#
# Two tools live here:
#   ScriptedStub  - a StubLLM whose per-template answers can be pinned
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
    """

    def __init__(self, seed: int = 0, mode: str = 'happy', script: dict = None):
        super().__init__(seed=seed, mode=mode)
        self.script = dict(script or {})

    def set(self, template: str, answer) -> None:
        self.script[template] = answer

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
