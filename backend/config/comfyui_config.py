# ComfyUI Configuration
# User-customizable settings for different ComfyUI setups
# These settings accommodate different user machines and model configurations

import os

# === Model and Checkpoint Settings ===
DEFAULT_CHECKPOINT = "XL\\dreamshaperXL_v21TurboDPMSDE.safetensors"
DEFAULT_SAMPLER = "dpmpp_sde_gpu"
DEFAULT_SCHEDULER = "karras"

# === Generation Parameters ===
DEFAULT_STEPS = 8
DEFAULT_CFG = 2.0
DEFAULT_DENOISE = 1.0

# === Image Dimensions ===
DEFAULT_WIDTH = 896
DEFAULT_HEIGHT = 1254 
DEFAULT_BATCH_SIZE = 1

# === Negative Prompt (Universal) ===
DEFAULT_NEGATIVE_PROMPT = (
    "worst quality, low quality, "
    "watermark, logo, text, signature, "
    "anime, woman, man, girl, lady, human"
)

# === Base Positive Prompt (Universal Styling) ===
DEFAULT_BASE_POSITIVE_PROMPT = (
    "card art, fantasy, whimsical, cute, creative, fun, hearthstone, "
#    "Norse mythology art"
#    "digital art, magic fantasy, vibrant colors, high contrast, "
#    "highly detailed, trending on artstation, 4k"
)

# === Server Settings ===
DEFAULT_SERVER_URL = "http://127.0.0.1:8188"
DEFAULT_TIMEOUT = 300  # 5 minutes

def get_checkpoint():
    """Get checkpoint name (customizable per user setup)"""
    return os.getenv('COMFYUI_CHECKPOINT', DEFAULT_CHECKPOINT)

def get_sampler():
    """Get sampler name"""
    return os.getenv('COMFYUI_SAMPLER', DEFAULT_SAMPLER)

def get_scheduler():
    """Get scheduler name"""
    return os.getenv('COMFYUI_SCHEDULER', DEFAULT_SCHEDULER)

def get_steps():
    """Get number of generation steps"""
    return int(os.getenv('COMFYUI_STEPS', DEFAULT_STEPS))

def get_cfg():
    """Get CFG scale"""
    return float(os.getenv('COMFYUI_CFG', DEFAULT_CFG))

def get_denoise():
    """Get denoise strength"""
    return float(os.getenv('COMFYUI_DENOISE', DEFAULT_DENOISE))

def get_width():
    """Get image width"""
    return int(os.getenv('COMFYUI_WIDTH', DEFAULT_WIDTH))

def get_height():
    """Get image height"""
    return int(os.getenv('COMFYUI_HEIGHT', DEFAULT_HEIGHT))

def get_batch_size():
    """Get batch size"""
    return int(os.getenv('COMFYUI_BATCH_SIZE', DEFAULT_BATCH_SIZE))

def get_negative_prompt():
    """Get default negative prompt"""
    return os.getenv('COMFYUI_NEGATIVE_PROMPT', DEFAULT_NEGATIVE_PROMPT)

def get_base_positive_prompt():
    """Get base positive prompt (styling)"""
    return os.getenv('COMFYUI_BASE_POSITIVE_PROMPT', DEFAULT_BASE_POSITIVE_PROMPT)

def get_server_url():
    """Get ComfyUI server URL"""
    return os.getenv('COMFYUI_SERVER_URL', DEFAULT_SERVER_URL)

def get_timeout():
    """Get generation timeout in seconds"""
    return int(os.getenv('COMFYUI_TIMEOUT', DEFAULT_TIMEOUT))

def get_all_generation_defaults():
    """
    Get all generation parameters as a dictionary
    Perfect for passing to workflow modification functions
    
    Returns:
        dict: All generation parameters with current defaults
    """
    return {
        'checkpoint': get_checkpoint(),
        'sampler': get_sampler(),
        'scheduler': get_scheduler(),
        'steps': get_steps(),
        'cfg': get_cfg(),
        'denoise': get_denoise(),
        'width': get_width(),
        'height': get_height(),
        'batch_size': get_batch_size(),
        'negative_prompt': get_negative_prompt(),
        'base_positive_prompt': get_base_positive_prompt(),
        'server_url': get_server_url(),
        'timeout': get_timeout()
    }