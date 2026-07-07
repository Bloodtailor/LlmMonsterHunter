# WorkflowStep - the step pointer a workflow shares with its handlers.
#
# Registered workflows report progress as (step_name, progress_data) pairs
# over SSE, and their error responses must name the exact step that died
# ('failed_at'). Once a workflow's logic spreads across handler modules,
# a plain local `step` variable can't do that job - this tiny object can:
# handlers advance it, the workflow's except block reads it.
#
# Step names and progress_data keys are a FRONTEND CONTRACT (the event
# hooks key off them) - handlers must emit the same names the monolithic
# workflows did. See docs/architecture.md.

from typing import Any, Callable


class WorkflowStep:
    """Mutable step pointer shared between a workflow and its handlers"""

    def __init__(self, on_update: Callable[[str, dict[str, Any]], None]):
        self.name = 'initialize_workflow'
        self.data: dict[str, Any] = {}
        self._on_update = on_update

    def emit(self, name: str) -> None:
        """Advance to a step and report it (with the data gathered so far)"""
        self.name = name
        self._on_update(name, self.data)

    def emit_again(self) -> None:
        """Re-report the current step (used after updating data mid-step)"""
        self._on_update(self.name, self.data)
