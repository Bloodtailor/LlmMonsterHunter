# Image Outputs - where generated art and player uploads live on disk
# Card-art paths in the DB are RELATIVE to this root, so relocating the
# root (out of the removed ComfyUI package) is invisible to every
# consumer as long as the files move with it - which outputs_root() does
# once, lazily, the first time anything asks.

import shutil
from pathlib import Path

IMAGE_OUTPUTS_DIR = Path(__file__).parent / 'outputs'

# The pre-cloud-generation tree (docs/plans/cloud-generation.md): art the
# removed ComfyUI pipeline generated, plus player uploads filed beside it
_LEGACY_OUTPUTS_DIR = Path(__file__).parent.parent / 'comfyui' / 'outputs'


def outputs_root() -> Path:
    """THE outputs root. Migrates the legacy ComfyUI tree on first touch;
    idempotent and near-free afterwards."""
    _migrate_legacy_outputs()
    IMAGE_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    return IMAGE_OUTPUTS_DIR


def _migrate_legacy_outputs() -> None:
    """Move everything under the old ComfyUI outputs tree into the new
    root, entry by entry (never overwriting), then drop the husk. A
    leftover means a name collision - it stays put and says so."""
    if not _LEGACY_OUTPUTS_DIR.exists():
        return

    IMAGE_OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    for entry in _LEGACY_OUTPUTS_DIR.iterdir():
        target = IMAGE_OUTPUTS_DIR / entry.name
        if entry.name == '.gitkeep':
            entry.unlink(missing_ok=True)
            continue
        if target.exists():
            print(f"⚠️ Legacy image folder not merged (already exists): {entry}")
            continue
        shutil.move(str(entry), str(target))
        print(f"Moved legacy image outputs: {entry.name} -> {target}")

    leftovers = list(_LEGACY_OUTPUTS_DIR.iterdir())
    if not leftovers:
        shutil.rmtree(_LEGACY_OUTPUTS_DIR, ignore_errors=True)
