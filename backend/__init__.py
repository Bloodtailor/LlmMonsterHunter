print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from dotenv import load_dotenv

load_dotenv()

from . import ai, core, game, models, routes, services, workflow
