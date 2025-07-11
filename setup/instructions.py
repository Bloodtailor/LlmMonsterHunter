# Installation Instructions
# Centralized repository of all verbose installation instructions
# Used by setup modules to keep code clean and instructions consistent

INSTRUCTIONS = {
    'nodejs_installation': [
        "📋 INSTALLATION REQUIRED:",
        "1. Go to https://nodejs.org/",
        "2. Download Node.js 18+ (LTS recommended)",
        "3. Run the installer with default settings",
        "4. npm is included automatically",
        "",
        "💡 This usually takes 2-3 minutes to download and install."
    ],

    'nodejs_restart_prompt': [
        "⚠️  Node.js installation may require command prompt restart.",
        "After installing Node.js:",
        "1. Close this command prompt window",
        "2. Open a new command prompt",
        "3. Run the game launcher again",
        "",
        "💡 This ensures PATH environment variable is updated"
    ],

    'mysql_installation': [
        "📋 INSTALLATION REQUIRED:",
        "1. Go to https://dev.mysql.com/downloads/mysql/",
        "2. Choose 'MySQL Community Server'",
        "3. Download the installer for Windows",
        "4. During installation:",
        "   - Choose 'Server only' or 'Developer Default'",
        "   - Set a root password (you'll need this!)",
        "   - Keep default port 3306",
        "5. The installer will also install MySQL Workbench (useful)",
        "",
        "💡 Installation size: ~200MB",
        "💡 This usually takes 5-10 minutes",
        "",
        "Write down your root password - you'll need it next!"
    ],

    'mysql_service_start': [
        "📋 STARTING MYSQL SERVICE:",
        "MySQL is installed but not running. To start it:",
        "1. Press Win+R, type 'services.msc', press Enter",
        "2. Find 'MySQL' or 'MySQL80' in the service list",
        "3. Right-click → Start",
        "4. Set startup type to 'Automatic' if desired",
        "",
        "Or try: Right-click Start menu → Run as Administrator → Command Prompt",
        "Then type: net start mysql"
    ],

    'mysql_cli_path': [
        "📋 ADDING MYSQL CLI TO PATH:",
        "MySQL server is working but CLI not in PATH.",
        "1. Press Win+R, type 'sysdm.cpl', press Enter",
        "2. Click 'Environment Variables'",
        "3. Edit 'Path' in System Variables",
        "4. Add your MySQL bin directory (typically:",
        "   C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin",
        "5. Click OK, restart command prompt",
        "6. Test: mysql --version"
    ],

    'nvidia_driver_installation': [
        "📋 NVIDIA DRIVER INSTALLATION:",
        "Download and install the latest drivers:",
        "1. Go to https://www.nvidia.com/drivers/",
        "2. Select your GPU model (or use 'Auto-detect')",
        "3. Download and run the installer",
        "4. Choose 'Express installation'",
        "5. Restart your computer after installation",
        "",
        "💡 Download size: ~500MB-1GB",
        "💡 Installation time: ~5-10 minutes + restart"
    ],

    'cuda_installation': [
        "📋 CUDA TOOLKIT INSTALLATION:",
        "CUDA allows AI models to run on your GPU:",
        "1. Go to https://developer.nvidia.com/cuda-toolkit",
        "2. Download CUDA Toolkit 12.3 (latest stable)",
        "3. Choose your system: Windows > x86_64 > Version > exe (local)",
        "4. Run the installer:",
        "   - Choose 'Express' installation",
        "   - Keep all default options",
        "   - This installs to: C:\\Program Files\\NVIDIA GPU Computing Toolkit\\",
        "",
        "💡 Download size: ~3GB", 
        "💡 Installation time: ~10-15 minutes",
        "",
        "Important: You may need to restart after CUDA installation."
    ],

    'visual_studio_buildtools': [
        "📋 VISUAL STUDIO BUILD TOOLS INSTALLATION:",
        "You need Visual Studio Build Tools to compile Python packages:",
        "1. Go to https://visualstudio.microsoft.com/downloads/",
        "2. Scroll down to 'All Downloads'",
        "3. Download 'Build Tools for Visual Studio 2022'",
        "4. Run the installer and select:",
        "   - 'C++ build tools' workload",
        "   - Include: MSVC v143 compiler toolset",
        "   - Include: Windows 10/11 SDK (latest)",
        "   - Include: CMake tools for Visual Studio",
        "5. Complete the installation (may take 30+ minutes)",
        "6. Restart your computer",
        "",
        "💡 This is required for compiling llama-cpp-python with CUDA support"
    ],

    'visual_studio_modify': [
        "📋 ADDING C++ BUILD TOOLS TO EXISTING VISUAL STUDIO:",
        "Visual Studio found but C++ build tools not detected:",
        "1. Open Visual Studio Installer",
        "2. Click 'Modify' on your Visual Studio installation", 
        "3. Go to 'Workloads' tab",
        "4. Check 'C++ build tools' or 'Desktop development with C++'",
        "5. In 'Individual components', ensure you have:",
        "   - MSVC v143 - VS 2022 C++ x64/x86 build tools",
        "   - Windows 10/11 SDK",
        "   - CMake tools for Visual Studio",
        "6. Click 'Modify' to install"
    ],

    'gpu_detection_check': [
        "📋 CHECK IF YOU HAVE AN NVIDIA GPU:",
        "First, let's verify you have a compatible GPU:",
        "1. Press Win+R, type 'dxdiag', press Enter",
        "2. Click 'Display' tab",
        "3. Look for 'Chip Type' - it should say 'NVIDIA GeForce...'",
        "",
        "If you don't see NVIDIA GPU:",
        "- You may have integrated graphics only",
        "- GPU may be disabled in BIOS",
        "- This is fine - the game works on CPU (just slower)"
    ],

    'model_lmstudio': [
        "📋 LM STUDIO MODEL SETUP (Recommended):",
        "LM Studio makes model management easy:",
        "1. Download and install LM Studio from https://lmstudio.ai/",
        "2. Open LM Studio",
        "3. Go to 'Discover' tab", 
        "4. Search for 'Kunoichi' and download 'Kunoichi-7B'",
        "5. After download, go to 'My Models'",
        "6. Right-click the model → 'Show in Folder'",
        "7. Copy the full file path",
        "",
        "💡 Model files are typically 3-8GB in size"
    ],

    'model_manual': [
        "📋 MANUAL MODEL DOWNLOAD:",
        "If you prefer to download manually:",
        "1. Go to https://huggingface.co/models",
        "2. Search for GGUF format models",
        "3. Good starting models:",
        "   - TheBloke/Kunoichi-7B-GGUF",
        "   - microsoft/DialoGPT-medium-GGUF", 
        "   - Any 7B parameter model in GGUF format",
        "4. Download the .gguf file",
        "5. Place it anywhere on your computer",
        "6. Note the full file path",
        "",
        "💡 Larger models are smarter but need more RAM/VRAM"
    ],

    'comfyui_installation': [
        "📋 COMFYUI INSTALLATION:",
        "ComfyUI generates images for monsters and abilities:",
        "1. Go to https://github.com/comfyanonymous/ComfyUI",
        "2. Click 'Code' → 'Download ZIP'",
        "3. Extract to any folder (e.g., C:\\ComfyUI)",
        "4. Download a Stable Diffusion model:",
        "   - Go to https://civitai.com/",
        "   - Download any SDXL model (.safetensors)",
        "   - Place in ComfyUI/models/checkpoints/",
        "5. Run ComfyUI:",
        "   - Double-click run_nvidia_gpu.bat (or run_cpu.bat)",
        "   - Wait for 'Starting server' message",
        "",
        "💡 ComfyUI models are 2-8GB each",
        "💡 First startup takes 2-3 minutes"
    ],

    'comfyui_model_setup': [
        "📋 COMFYUI MODEL CONFIGURATION:",
        "Tell us about your ComfyUI model:",
        "1. Make sure ComfyUI is running (server at http://127.0.0.1:8188)",
        "2. Look in your ComfyUI/models/checkpoints/ folder",
        "3. Find your model file name (e.g., 'dreamshaper_xl.safetensors')",
        "4. Note if it's in a subfolder (e.g., 'XL/dreamshaper_xl.safetensors')",
        "",
        "💡 We'll configure the game to use your specific model",
        "💡 You can change this later in the .env file"
    ]
}

def get_instructions(key):
    """
    Get installation instructions by key
    
    Args:
        key (str): Instruction key from INSTRUCTIONS dict
        
    Returns:
        list: List of instruction lines, or empty list if key not found
    """
    return INSTRUCTIONS.get(key, [])

def get_available_instructions():
    """
    Get list of all available instruction keys
    
    Returns:
        list: All instruction keys
    """
    return list(INSTRUCTIONS.keys())