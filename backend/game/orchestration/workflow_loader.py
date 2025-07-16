# workflow_loader.py
print("🔍 Loading workflow loader")
import importlib.util
from pathlib import Path

def _import_module_from_path(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if not spec or not spec.loader:
        raise ImportError(f"Failed to import module {module_name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

def load_all_workflows():
    """Import every registered_workflows.py under backend/game/* to trigger registration decorators."""
    game_dir = Path(__file__).parent.parent  # backend/game/

    for module_dir in game_dir.iterdir():
        if not module_dir.is_dir() or module_dir.name == "orchestration":
            continue
        wf_file = module_dir / "registered_workflows.py"
        if wf_file.is_file():
            _import_module_from_path(
                module_name=f"{module_dir.name}_registered_workflows",
                path=wf_file
            )
