#!/usr/bin/env python3
"""
Test script to verify Photoshop Automation Project setup
"""

import os
import sys
import importlib
import json

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    required_modules = [
        'cv2',
        'numpy',
        'pandas',
        'mediapipe',
        'PIL',
        'openpyxl'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All modules imported successfully")
    return True

def test_project_structure():
    """Test if project structure is correct"""
    print("\n📁 Testing project structure...")
    
    required_dirs = [
        'src',
        'gui',
        'config',
        'input/excel_files',
        'input/assets/logos',
        'output',
        'logs',
        'templates'
    ]
    
    missing_dirs = []
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}")
        else:
            print(f"  ❌ {directory}")
            missing_dirs.append(directory)
    
    if missing_dirs:
        print(f"\n❌ Missing directories: {', '.join(missing_dirs)}")
        return False
    
    print("✅ Project structure is correct")
    return True

def test_configuration():
    """Test if configuration file is valid"""
    print("\n⚙️ Testing configuration...")
    
    config_path = 'config/settings.json'
    
    if not os.path.exists(config_path):
        print(f"  ❌ Configuration file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        required_keys = [
            'enable_photoshop_export',
            'default_logo_width',
            'output_folder'
        ]
        
        missing_keys = []
        
        for key in required_keys:
            if key in config:
                print(f"  ✅ {key}: {config[key]}")
            else:
                print(f"  ❌ {key}: Missing")
                missing_keys.append(key)
        
        if missing_keys:
            print(f"\n❌ Missing configuration keys: {', '.join(missing_keys)}")
            return False
        
        print("✅ Configuration is valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"  ❌ Invalid JSON in configuration: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error reading configuration: {e}")
        return False

def test_sample_files():
    """Test if sample files exist"""
    print("\n📄 Testing sample files...")
    
    sample_files = [
        'input/excel_files/sample_products.csv',
        'PROJECT_GUIDE.md',
        'SETUP_GUIDE.md'
    ]
    
    missing_files = []
    
    for file_path in sample_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Missing sample files: {', '.join(missing_files)}")
        print("   These are optional but helpful for testing")
    
    print("✅ Sample files check completed")
    return True

def main():
    """Main test function"""
    print("🧪 Testing Photoshop Automation Project Setup")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_project_structure,
        test_configuration,
        test_sample_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Prepare your Excel file and assets")
        print("2. Run: python -m gui.interface")
        print("3. Or run: python -m src.main")
    else:
        print("❌ Some tests failed. Please check the setup.")
        print("\nTroubleshooting:")
        print("1. Run: python3 setup.py")
        print("2. Check SETUP_GUIDE.md for detailed instructions")
        print("3. Ensure all dependencies are installed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)