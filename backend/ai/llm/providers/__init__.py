# LLM Providers - the dispatch seam between the processor and whichever
# engine actually generates text. Every provider module exposes the same
# contract: generate_streaming(prompt, callback, **params) returning
# {success, error, text, tokens, prompt_tokens, model_name, duration,
#  tokens_per_second}. The processor dispatches on the provider name
# STAMPED into llm_logs at request time by the gateway - never on live
# settings - so queued work finishes on the provider it was requested
# under (locked decision, docs/plans/game-settings.md).

from backend.ai.llm.provider_settings import PROVIDER_DEEPSEEK
from backend.core.utils import print_warning


def get_provider(provider_name):
    """
    Provider module for a stamped llm_logs.provider value.

    None (rows from before the seam existed) and unknown names resolve to
    local - pre-initiative behavior is the floor, and an old log row must
    never strand the queue.
    """
    if provider_name == PROVIDER_DEEPSEEK:
        try:
            from backend.ai.llm.providers import deepseek

            return deepseek
        except ImportError:
            # The DeepSeek module lands in Set-M3; a deepseek-stamped row
            # before then falls back rather than failing the generation
            print_warning('DeepSeek provider unavailable - falling back to local')

    from backend.ai.llm.providers import local

    return local
