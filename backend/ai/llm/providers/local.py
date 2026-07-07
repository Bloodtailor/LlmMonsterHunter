# Local Provider - llama-cpp-python behind the provider seam
# A thin adapter over inference.generate_streaming that adds the two
# observability fields the seam contract carries: model_name (the GGUF
# filename) and prompt_tokens (exact, from the model's own tokenizer).
# The inference module itself is untouched - it still owns the model
# lock, the streaming loop, and the lazy load.

import os
from pathlib import Path
from typing import Any, Callable, Optional

from backend.ai.llm import inference


def generate_streaming(
    prompt: str,
    callback: Optional[Callable[[str], None]] = None,
    model_name: Optional[str] = None,
    **params,
) -> dict[str, Any]:
    """The provider contract, spoken by the local model. model_name is
    part of the seam signature (the processor passes the stamped value)
    but the local engine has exactly one model - the loaded GGUF - so the
    stamp is ignored and must never reach llama-cpp's params."""
    result = inference.generate_streaming(prompt=prompt, callback=callback, **params)

    result['model_name'] = model_file_name()
    result['prompt_tokens'] = count_prompt_tokens(prompt)
    return result


def count_prompt_tokens(prompt: str) -> Optional[int]:
    """Exact prompt token count from the loaded model's own tokenizer.
    None when the model isn't available - bookkeeping must never fail a
    generation."""
    try:
        from backend.ai.llm.core import get_model_instance

        model = get_model_instance()
        if model is None:
            return None

        return len(model.tokenize(prompt.encode('utf-8')))
    except Exception:
        return None


def model_file_name() -> Optional[str]:
    """The GGUF filename - the local model's display name everywhere
    (streaming panel, developer log table)"""
    model_path = os.getenv('LLM_MODEL_PATH')
    return Path(model_path).name if model_path else None
