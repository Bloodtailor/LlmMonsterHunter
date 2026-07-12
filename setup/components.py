"""
Component Registry - the single source of truth for what setup manages.

WHY this file exists: the API-first game (DeepSeek text + Gemini art,
keys pasted in-game) needs only four components. The other four serve
the UNSUPPORTED local-LLM escape hatch (docs/plans/cloud-generation.md).
Before this registry, required-vs-optional lived as a hardcoded tuple in
the flows package and the requirements checker gated on ALL components -
so a fresh API-first machine was told "game likely won't work" because
it lacked CUDA it never needed. Required-ness is a property of the
component definition, declared once, here.

Ordering matters: setup runs components top to bottom, and later
components assume earlier ones (Database Connection needs the .env that
Basic Backend creates and the server that MySQL Server checks).
"""

# (name, is_required_for_the_api_first_game)
_COMPONENT_DEFINITIONS = (
    ('Basic Backend', True),
    ('Node.js & npm', True),
    ('MySQL Server', True),
    ('Database Connection', True),
    ('NVIDIA GPU & CUDA', False),
    ('Visual Studio Build Tools', False),
    ('Model Directory', False),
    ('LLM Integration', False),
)

ALL_COMPONENTS = tuple(name for name, _ in _COMPONENT_DEFINITIONS)

REQUIRED_COMPONENTS = tuple(name for name, required in _COMPONENT_DEFINITIONS if required)

# The local-LLM escape hatch chain: only reachable via --local-extras.
LOCAL_EXTRA_COMPONENTS = tuple(name for name, required in _COMPONENT_DEFINITIONS if not required)


def components_for(include_local_extras=False):
    """The ordered component list for one setup/check run."""
    return ALL_COMPONENTS if include_local_extras else REQUIRED_COMPONENTS
