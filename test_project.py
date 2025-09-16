#!/usr/bin/env python3
"""
Test script to validate the Photoshop Automation Project setup
"""

import os
import sys
import json
from pathlib import Path

def test_project_structure():
    """Test if the project structure is correct"""
    print("🔍 Testing Project Structure...")
    
    required_dirs = [
        "input/excel_files",
        "input/assets/logos", 
        "output",
        "output/thumbnails",
        "logs",
        "src",
        "config",
        "gui"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
            print(f"❌ Missing directory: {dir_path}")
        else:
            print(f"✅ Found directory: {dir_path}")
    
    if missing_dirs:
        print(f"\n⚠️  Creating missing directories: {missing_dirs}")
        for dir_path in missing_dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    return len(missing_dirs) == 0

def test_excel_file():
    """Test if sample Excel file exists"""
    print("\n📊 Testing Excel File...")
    
    excel_path = "input/excel_files/sample.xlsx"
    if os.path.exists(excel_path):
        print(f"✅ Found sample Excel file: {excel_path}")
        return True
    else:
        print(f"❌ Missing sample Excel file: {excel_path}")
        return False

def test_config_file():
    """Test if configuration file exists and is valid"""
    print("\n⚙️  Testing Configuration...")
    
    config_path = "config/settings.json"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            print(f"✅ Found valid config file: {config_path}")
            print(f"   - Default logo width: {config.get('default_logo_width', 'N/A')}")
            print(f"   - Photoshop export: {config.get('enable_photoshop_export', 'N/A')}")
            return True
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in config file: {config_path}")
            return False
    else:
        print(f"❌ Missing config file: {config_path}")
        return False

def test_dependencies():
    """Test if required Python packages are available"""
    print("\n📦 Testing Dependencies...")
    
    required_packages = [
        'pandas',
        'openpyxl', 
        'cv2',
        'mediapipe',
        'PIL',
        'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            elif package == 'PIL':
                from PIL import Image
            else:
                __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {missing_packages}")
        print("Install with: pip3 install " + " ".join(missing_packages))
    
    return len(missing_packages) == 0

def test_source_files():
    """Test if main source files exist"""
    print("\n🔧 Testing Source Files...")
    
    required_files = [
        "src/main.py",
        "src/excel_parser.py", 
        "src/logo_positioner.py",
        "src/exporter.py",
        "src/utils.py",
        "gui/interface.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def create_sample_folders():
    """Create sample supplier folders for testing"""
    print("\n📁 Creating Sample Folders...")
    
    suppliers = ["SupplierA", "SupplierB", "SupplierC", "SupplierD"]
    for supplier in suppliers:
        folder_path = f"input/assets/{supplier}"
        os.makedirs(folder_path, exist_ok=True)
        print(f"✅ Created: {folder_path}")
    
    # Create a sample logo folder
    logo_folder = "input/assets/logos"
    os.makedirs(logo_folder, exist_ok=True)
    print(f"✅ Created: {logo_folder}")

def main():
    """Run all tests"""
    print("🚀 Photoshop Automation Project - Setup Test")
    print("=" * 50)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Excel File", test_excel_file),
        ("Configuration", test_config_file),
        ("Dependencies", test_dependencies),
        ("Source Files", test_source_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error in {test_name}: {e}")
            results.append((test_name, False))
    
    # Create sample folders
    create_sample_folders()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your project is ready to use.")
        print("\n📖 Next steps:")
        print("1. Add your Excel file to input/excel_files/")
        print("2. Add product images to input/assets/{SupplierName}/")
        print("3. Add logo files to input/assets/logos/")
        print("4. Run: python3 -m gui.interface")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)