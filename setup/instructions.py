# Installation Instructions
# Centralized repository of all verbose installation instructions
# Used by setup modules to keep code clean and instructions consistent

INSTRUCTIONS = {
    'nodejs_installation': [
        "📋 INSTALLATION REQUIRED:",
        "   1. Go to https://nodejs.org/",
        "   2. Download the LTS version (version 18 or later)",
        "   3. Run the downloaded installer",
        "      - Accept all default settings unless you know what you're doing",
        "",
        "   4. After installation, open a terminal and run the following commands to verify:",
        "      - `node -v` (should return a version like v18.x.x or higher)",
        "      - `npm -v` (should return a version number)",
        "",
        "   5. Once installed, please re-run start_game.bat",
        "",
        "💡 This usually takes 2–3 minutes to download and install.",
        "💡 You'll need to restart your command prompt after installation."
        "",
        "",
        "You have the following options to continue:",
        "   1. Skip and move on to next component (recommended)",
        "   2. Try to install frontend dependencies anyways (if nodejs is installed, but undetected)",
        "   3. Exit the setup and restart when nodejs is installed",
        ""
    ],


    'mysql_installation': [
        "📋 MYSQL INSTALLATION REQUIRED:",
        "",
        "1. Go to https://dev.mysql.com/downloads/mysql/",
        "2. Click 'MySQL Community Server'",
        "3. Select your Windows version (Windows 10/11)",
        "4. Download the MSI Installer (mysql-installer-community-x.x.xx.msi)",
        "",
        "5. Run the installer as Administrator:",
        "   - Choose 'Developer Default' or 'Server only'",
        "   - Keep default port 3306",
        "   - Set a root password (WRITE THIS DOWN!)",
        "   - Choose 'Configure MySQL Server as a Windows Service'",
        "   - Service name: MySQL80 (or MySQL84)",
        "   - Start the MySQL Server at System Startup: YES",
        "",
        "6. Complete the installation (may take 5-10 minutes)",
        "7. Test installation: Open Command Prompt and run 'mysql --version'",
        "",
        "💡 Installation size: ~200MB",
        "💡 You'll need the root password for database setup later!",
        "",
        "If the installer fails, try:",
        "- Running as Administrator",
        "- Temporarily disabling antivirus",
        "- Using the ZIP archive instead of MSI installer"
    ],

    'mysql_service_start': [
        "📋 STARTING MYSQL SERVICE MANUALLY:",
        "",
        "Method 1 - Services Manager (Recommended):",
        "1. Press Win+R, type 'services.msc', press Enter",
        "2. Scroll down and find 'MySQL80' or 'MySQL84' or 'MySQL'",
        "3. Right-click the service → 'Start'",
        "4. If you want it to start automatically:",
        "   - Right-click → 'Properties'",
        "   - Change 'Startup type' to 'Automatic'",
        "   - Click 'OK'",
        "",
        "Method 2 - Command Line (Run as Administrator):",
        "1. Right-click Start menu → 'Windows Terminal (Admin)'",
        "2. Type: net start MySQL80",
        "3. Or try: net start MySQL84",
        "4. Or try: net start MySQL",
        "",
        "Method 3 - MySQL Workbench:",
        "1. Open MySQL Workbench (if installed)",
        "2. Click 'Server Status' in the sidebar",
        "3. Click 'Start Server'",
        "",
        "If all methods fail:",
        "- Check Windows Event Viewer for MySQL errors",
        "- MySQL may have configuration issues",
        "- Consider reinstalling MySQL"
    ],

    'mysql_troubleshooting': [
        "📋 MYSQL TROUBLESHOOTING:",
        "",
        "Common issues and solutions:",
        "",
        "Issue 1 - Port 3306 in use:",
        "1. Open Command Prompt as Administrator",
        "2. Run: netstat -ano | findstr :3306",
        "3. If another process is using port 3306:",
        "   - Stop that process, or",
        "   - Reconfigure MySQL to use a different port",
        "",
        "Issue 2 - MySQL won't start:",
        "1. Check Windows Event Viewer:",
        "   - Press Win+R → eventvwr.msc",
        "   - Go to Windows Logs → Application",
        "   - Look for MySQL errors",
        "2. Common fixes:",
        "   - Delete ib_logfile0 and ib_logfile1 from MySQL data directory",
        "   - Run MySQL as Administrator",
        "   - Check disk space (MySQL needs space for logs)",
        "",
        "Issue 3 - Permission errors:",
        "1. Run Command Prompt as Administrator",
        "2. Navigate to MySQL bin directory",
        "3. Try: mysqld --install",
        "4. Then: net start mysql",
        "",
        "Issue 4 - Configuration problems:",
        "1. Locate my.ini file (usually in MySQL installation folder)",
        "2. Check for syntax errors",
        "3. Reset to default configuration if needed",
        "",
        "Last resort:",
        "- Completely uninstall MySQL",
        "- Delete all MySQL folders",
        "- Reinstall with default settings"
    ],

    'mysql_cli_path': [
        "📋 ADDING MYSQL CLI TO SYSTEM PATH:",
        "",
        "Your MySQL installation was detected. Follow these steps:",
        "",
        "1. Copy the MySQL bin path shown above",
        "2. Press Win+R, type 'sysdm.cpl', press Enter",
        "3. Click 'Environment Variables' button",
        "4. In 'System Variables' section (bottom), find 'Path'",
        "5. Select 'Path' and click 'Edit'",
        "6. Click 'New' button",
        "7. Paste the MySQL bin path",
        "8. Click 'OK' on all dialogs",
        "",
        "9. IMPORTANT: Close all Command Prompt windows",
        "10. Open a new Command Prompt",
        "11. Test by running: mysql --version",
        "",
        "Alternative method (Windows 10/11):",
        "1. Right-click 'This PC' → Properties",
        "2. Click 'Advanced system settings'",
        "3. Follow steps 3-11 above",
        "",
        "If it still doesn't work:",
        "- Make sure you closed ALL command prompt windows",
        "- Try restarting your computer",
        "- Verify the path exists and contains mysql.exe"
    ],

    'mysql_cli_path_generic': [
        "📋 ADDING MYSQL CLI TO SYSTEM PATH:",
        "",
        "MySQL CLI not found in PATH. To fix this:",
        "",
        "1. Find your MySQL installation:",
        "   - Check: C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin",
        "   - Check: C:\\Program Files\\MySQL\\MySQL Server 8.4\\bin", 
        "   - Check: C:\\xampp\\mysql\\bin",
        "   - Check: C:\\wamp64\\bin\\mysql\\mysql8.x.x\\bin",
        "",
        "2. Once you find the folder containing mysql.exe:",
        "   - Copy the full path to that folder",
        "",
        "3. Add to System PATH:",
        "   - Press Win+R, type 'sysdm.cpl', press Enter",
        "   - Click 'Environment Variables'",
        "   - In 'System Variables', find 'Path' and click 'Edit'",
        "   - Click 'New' and paste the MySQL bin path",
        "   - Click 'OK' on all dialogs",
        "",
        "4. Test the fix:",
        "   - Close all Command Prompt windows",
        "   - Open new Command Prompt",
        "   - Run: mysql --version",
        "",
        "If you can't find MySQL installation:",
        "- MySQL may not be properly installed",
        "- Try reinstalling MySQL with default settings",
        "- Make sure to include 'MySQL Command Line Client' during installation"
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