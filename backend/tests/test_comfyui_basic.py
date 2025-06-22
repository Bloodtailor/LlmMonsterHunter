# ComfyUI Basic Test
# Tests the NEW MODULAR ComfyUI integration step by step
# Handles missing directories and import errors gracefully

import os
from pathlib import Path

def test_basic_comfyui():
    """Test basic ComfyUI functionality with new modular structure"""
    
    print("🧪 Testing NEW MODULAR ComfyUI Integration")
    print("=" * 60)
    
    # Step 0: Check if ComfyUI directory structure exists
    print("🔍 Step 0: Checking directory structure...")
    backend_dir = Path(__file__).parent.parent
    comfyui_dir = backend_dir / 'comfyui'
    
    if not comfyui_dir.exists():
        print("❌ ComfyUI directory not found!")
        print(f"   Expected: {comfyui_dir}")
        print("\n💡 Setup Instructions:")
        print("   1. Create the ComfyUI directory structure:")
        print(f"      mkdir {comfyui_dir}")
        print(f"      mkdir {comfyui_dir}/workflows")
        print(f"      mkdir {comfyui_dir}/outputs")
        print(f"      touch {comfyui_dir}/__init__.py")
        print("   2. Copy the ComfyUI Python files to the comfyui directory")
        print("   3. Move your monster_generation.json to comfyui/workflows/")
        print("   4. Run this test again")
        return
    
    print("✅ ComfyUI directory structure exists")
    
    # Check for required files
    required_files = ['__init__.py', 'client.py', 'workflow.py', 'models.py', 'generation.py']
    missing_files = []
    
    for file in required_files:
        if not (comfyui_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing ComfyUI files: {missing_files}")
        print("💡 Copy all the ComfyUI Python files to the comfyui directory")
        return
    
    print("✅ All ComfyUI files present")
    
    # Step 1: Check if image generation is enabled
    print("\n🔍 Step 1: Checking configuration...")
    enabled = os.getenv('ENABLE_IMAGE_GENERATION', 'false').lower() == 'true'
    
    if enabled:
        print("✅ Image generation is ENABLED in configuration")
    else:
        print("❌ Image generation is DISABLED in configuration")
        print("💡 To enable: Set ENABLE_IMAGE_GENERATION=true in your .env file")
        print("   Or run: set ENABLE_IMAGE_GENERATION=true")
        print("\n🎯 Continuing with test anyway to show graceful degradation...")
    
    # Step 2: Try importing ComfyUI service
    print("\n🔍 Step 2: Testing ComfyUI service imports...")
    
    try:
        from backend.services.comfyui_service import is_comfyui_available, get_comfyui_status
        print("✅ ComfyUI service imported successfully")
        service_available = True
    except ImportError as e:
        print(f"❌ ComfyUI service import failed: {e}")
        print("💡 Check that comfyui_service.py exists in backend/services/")
        service_available = False
    
    if not service_available:
        return
    
    # Step 3: Get comprehensive status
    print("\n🔍 Step 3: Getting ComfyUI status...")
    try:
        status = get_comfyui_status()
        
        print(f"   Enabled: {status['enabled']}")
        print(f"   Components loaded: {status['components_loaded']}")
        print(f"   Server running: {status['server_running']}")
        print(f"   Available: {status['available']}")
        print(f"   Message: {status['message']}")
        
        if status.get('help'):
            print(f"   Help: {status['help']}")
            
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        status = {'available': False, 'enabled': enabled, 'components_loaded': False}
    
    # Step 4: Test validation if components are available
    if status.get('components_loaded'):
        print("\n📋 Step 4: Running setup validation...")
        
        try:
            from backend.comfyui import validate_comfyui_setup
            validation = validate_comfyui_setup()
            print(f"   Overall success: {validation['overall_success']}")
            
            for check_name, check_result in validation.get('checks', {}).items():
                print(f"   {check_name}: {check_result['message']}")
        
        except ImportError as e:
            print(f"   ❌ Could not import validation: {e}")
        except Exception as e:
            print(f"   ❌ Validation failed: {e}")
    else:
        print("\n📋 Step 4: Skipping validation (components not loaded)")
    
    # Step 5: Test graceful generation (should work whether enabled or not)
    print("\n🎨 Step 5: Testing graceful image generation...")
    test_description = "A majestic fire dragon with golden scales and emerald eyes"
    
    print("   Attempting generation (this will show graceful degradation if disabled)...")
    
    try:
        from backend.services.comfyui_service import generate_monster_image
        
        result = generate_monster_image(
            monster_description=test_description,
            monster_name="Test Dragon",
            monster_species="Fire Dragon",
            callback=lambda msg: print(f"      {msg}")
        )
        
        print(f"\n   Result: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
        
        if result['success']:
            print(f"      Image saved to: {result['image_path']}")
            print(f"      Generation time: {result['execution_time']:.1f} seconds")
            print(f"      Cleanup successful: {result.get('cleanup_success', 'Unknown')}")
        else:
            print(f"      Error: {result['error']}")
            print(f"      Reason: {result.get('reason', 'Unknown')}")
            if result.get('help'):
                print(f"      Help: {result['help']}")
            if result.get('details'):
                print("      Details:")
                for detail in result['details']:
                    print(f"         {detail}")
    
    except Exception as e:
        print(f"   ❌ Generation test failed: {e}")
        result = {'success': False}
    
    # Step 6: Summary
    print("\n🏁 Test Summary:")
    print("=" * 60)
    
    if status.get('available') and result.get('success'):
        print("🎉 FULL SUCCESS: ComfyUI is working perfectly!")
        print("   ✅ Configuration enabled")
        print("   ✅ Server running")
        print("   ✅ Image generation working") 
        print("   ✅ VRAM cleanup working")
    elif status.get('enabled') and not status.get('available'):
        print("⚠️  SETUP NEEDED: ComfyUI enabled but not working")
        print("   ✅ Configuration enabled")
        print("   ❌ Server not running or workflow missing")
        print("   💡 Fix the issues above and test again")
    elif not status.get('enabled'):
        print("🔧 DISABLED: Image generation is disabled (this is fine!)")
        print("   ❌ Configuration disabled")
        print("   💡 The game will work without images")
        print("   💡 Enable if you want monster images")
    else:
        print("🔍 MIXED RESULTS: Check individual steps above")
    
    print(f"\n📊 Final status: {status.get('message', 'Test completed')}")

if __name__ == "__main__":
    test_basic_comfyui()

if __name__ == "__main__":
    test_basic_comfyui()