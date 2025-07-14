# setup/dry_run_utils.py

from setup.ux_utils import print_dry_run, print_dry_run_header

DRY_RUN_SCENARIOS = {
    'check_nvidia_gpu': [
        (True, "NVIDIA GeForce RTX 3070"),
        (True, "NVIDIA GeForce GTX 1060 6GB"),
        (False, "nvidia-smi not found (NVIDIA drivers not installed)"),
        (False, "nvidia-smi failed (GPU or driver issues)")
    ],
    'check_nvidia_driver_version': [
        (True, "NVIDIA driver 535.98 (CUDA 12.x compatible)"),
        (False, "NVIDIA driver 472.84 is too old (need 530+ for CUDA 12.x)"),
        (False, "Could not parse NVIDIA driver version"),
        (False, "nvidia-smi not found (cannot check driver version)")
    ],
    'check_cuda_directories': [
        (True, "CUDA Toolkit found: C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.2"),
        (False, "CUDA Toolkit directories not found"),
        (False, "Partial CUDA installation detected")
    ],
    'check_nvcc_compiler': [
        (True, "CUDA compiler (nvcc) available, version 12.2"),
        (False, "CUDA compiler (nvcc) not found in PATH"),
        (False, "CUDA compiler (nvcc) failed to run")
    ],
    'check_cuda_path_env': [
        (True, "CUDA_PATH environment variable: C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.2"),
        (False, "CUDA_PATH environment variable not set or invalid")
    ],
    'check_gpu_compute_capability': [
        (True, "GPU compute capability 8.6 (excellent for AI)"),
        (True, "GPU compute capability 6.1 (good for AI)"),
        (False, "GPU compute capability 3.5 (limited AI support)"),
        (False, "Could not determine GPU compute capability")
    ]
}

def set_dry_run(check_name):
    """Interactive dry run scenario selection"""
    scenarios = DRY_RUN_SCENARIOS.get(check_name, [(True, "Default success scenario")])
    
    print_dry_run(f"\nDry run options for: {check_name}")
    for i, (success, message) in enumerate(scenarios, 1):
        status = "✅" if success else "❌"
        print_dry_run(f"{i}. {status} {message}")
    
    while True:
        choice = input("Please enter your choice: ").strip()
        try:
            index = int(choice) - 1
            if 0 <= index < len(scenarios):
                selected = scenarios[index]
                print_dry_run(f"Selected: {'✅' if selected[0] else '❌'} {selected[1]}")
                return selected
            else:
                print_dry_run("Invalid choice, please try again.")
        except ValueError:
            print_dry_run("Please enter a number.")