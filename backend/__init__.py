print(f"🔍 Loading {__file__.split('LlmMonsterHunter', 1)[-1]}")

from dotenv import load_dotenv
load_dotenv()

from . import core
from . import models
from . import ai
from . import workflow
from . import game
from . import services
from . import routes
