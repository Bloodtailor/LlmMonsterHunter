# Image Generation Configuration
# Code-owned knobs for cloud card art (the Gemini "Nano Banana" family).
# The PLAYER-owned knobs (API key, model pick, enabled switch) live in a
# game_settings row - backend/ai/image/image_settings.py resolves them.

import os

# The model the game reaches for when the settings row names none
DEFAULT_IMAGE_MODEL = 'gemini-3.1-flash-image'  # "Nano Banana 2"

# Card geometry: the old ComfyUI cards were 896x1254 (~5:7); 2:3 at 1K
# is the closest supported shape and keeps the portrait card look
DEFAULT_ASPECT_RATIO = '2:3'
DEFAULT_RESOLUTION = '1K'  # '512px' | '1K' | '2K' | '4K'

# The house style, spoken as natural language - the SD tag-soup and the
# negative-prompt channel died with ComfyUI. Appended to every image
# prompt after the subject, in the GATEWAY, before logging, so the dev
# table shows the byte-exact prompt the model received.
HOUSE_STYLE_PROMPT = (
    'Whimsical fantasy creature card art: painterly, vibrant, warm and a '
    'little playful, like a collectible card game illustration.'
)

# What must never appear - modern image APIs take this as an instruction
# inside the prompt, not as a separate negative prompt
AVOID_INSTRUCTION = (
    'Do not include any humans, text, letters, numbers, watermarks, '
    'logos, signatures, borders, or frames.'
)

# One blocking HTTP call per image - generous, but images are a bonus
# and the queue is serial, so a hung call must eventually let go
DEFAULT_TIMEOUT = 120


def get_timeout() -> int:
    """Seconds allowed for one image generation call"""
    return int(os.getenv('IMAGE_TIMEOUT', DEFAULT_TIMEOUT))


def compose_image_prompt(subject: str) -> str:
    """Subject + house style + avoid instruction, one string - THE image
    prompt recipe, applied before logging (byte-exact dev table)"""
    parts = (str(subject or '').strip(), HOUSE_STYLE_PROMPT, AVOID_INSTRUCTION)
    return ' '.join(part for part in parts if part)
