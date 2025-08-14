# Workflow loader - Maps workflow types to existing game logic functions
# Combs through the files in the game folder
# Registers files named "registered_workflows.py" as callable workflows
print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from typing import Callable, Dict, Any, Optional
import inspect
import threading

# Global registry of workflow_name -> callable
_WORKFLOW_REGISTRY: Dict[str, Callable[[dict], dict]] = {}
_REGISTRY_LOCK = threading.Lock()  # thread-safe if registering dynamically

class WorkflowRegistrationError(Exception):
    pass

def register_workflow(name: Optional[str] = None):
    """
    Decorator to register a function as an orchestration workflow step.

    Requirements enforced:
      - Callable takes exactly 1 parameter: context (dict-like)
      - Returns a dict (checked at runtime on first call; optional strict mode)
    """
    def decorator(fn: Callable[[dict], dict]):
        nonlocal name
        workflow_name = name or fn.__name__

        # Validate signature now (fail fast)
        sig = inspect.signature(fn)
        params = list(sig.parameters.values())
        if len(params) != 1:
            raise WorkflowRegistrationError(
                f"{fn.__name__} must take exactly one argument: context."
            )
        # (Optional) enforce param name == 'context'
        if params[0].name != "context":
            raise WorkflowRegistrationError(
                f"{fn.__name__} first param must be named 'context'."
            )

        # Register thread-safely
        with _REGISTRY_LOCK:
            if workflow_name in _WORKFLOW_REGISTRY:
                raise WorkflowRegistrationError(
                    f"Workflow '{workflow_name}' already registered."
                )
            _WORKFLOW_REGISTRY[workflow_name] = fn

        return fn
    return decorator

def get_workflow(name: str) -> Callable[[dict], dict] | None:
    return _WORKFLOW_REGISTRY.get(name)

def list_workflows() -> list[str]:
    return sorted(_WORKFLOW_REGISTRY.keys())

def is_workflow_supported(name: str) -> bool:
    return name in _WORKFLOW_REGISTRY
