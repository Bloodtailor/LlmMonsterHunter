from typing import Iterable

def require_keys(ctx: dict, keys: Iterable[str]) -> None:
  missing = [k for k in keys if k not in ctx]
  if missing:
    raise KeyError(f"Missing required context keys: {', '.join(missing)}")