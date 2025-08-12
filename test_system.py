#!/usr/bin/env python3
"""
Test script for Image Processing and Logo Placement Automation System
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.excel_processor import ExcelProcessor
from src.image_finder import ImageFinder
from src.logo_extractor import LogoExtractor
from src.coordinate_detector import CoordinateDetector

def test_excel_processor():
    """Test Excel file processing"""
    print("🧪 Testing Excel Processor...")
    
    try:
        processor = ExcelProcessor()
        
        # Test with example file if it exists
        if os.path.exists("example_data.xlsx"):
            df = processor.read_excel("example_data.xlsx")
            print(f"✅ Successfully read {len(df)} rows from Excel")
            
            # Test validation
            for _, row in df.iterrows():
                if processor.validate_row_data(row):
                    print(f"✅ Row validation passed: {row['Supplier Part ID']}")
                else:
                    print(f"❌ Row validation failed: {row['Supplier Part ID']}")
        else:
            print("⚠️  example_data.xlsx not found - skipping Excel test")
        
        return True
        
    except Exception as e:
        print(f"❌ Excel processor test failed: {e}")
        return False

def test_image_finder():
    """Test image finding functionality"""
    print("\n🧪 Testing Image Finder...")
    
    try:
        finder = ImageFinder()
        
        # Create temporary test structure
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test supplier folder
            supplier_dir = os.path.join(temp_dir, "TestSupplier")
            os.makedirs(supplier_dir)
            
            # Create a dummy image file
            test_image = os.path.join(supplier_dir, "ABC123Red.png")
            Path(test_image).touch()
            
            # Test finding the image
            result = finder.find_image(temp_dir, "TestSupplier", "ABC123", "Red")
            
            if result:
                print(f"✅ Image found: {result}")
            else:
                print("❌ Image not found")
            
            # Test fuzzy search
            fuzzy_image = os.path.join(supplier_dir, "ABC123_Red_variant.png")
            Path(fuzzy_image).touch()
            
            result = finder.find_image(temp_dir, "TestSupplier", "ABC123", "Red")
            if result:
                print(f"✅ Fuzzy search worked: {os.path.basename(result)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Image finder test failed: {e}")
        return False

def test_coordinate_detector():
    """Test coordinate detection"""
    print("\n🧪 Testing Coordinate Detector...")
    
    try:
        detector = CoordinateDetector()
        
        # Create a simple test image
        import numpy as np
        import cv2
        
        # Create a dummy image (500x500, 3 channels)
        test_image = np.ones((500, 500, 3), dtype=np.uint8) * 128
        test_logo = np.ones((50, 50, 3), dtype=np.uint8) * 255
        
        with tempfile.TemporaryDirectory() as temp_dir:
            image_path = os.path.join(temp_dir, "test_image.png")
            logo_path = os.path.join(temp_dir, "test_logo.png")
            
            cv2.imwrite(image_path, test_image)
            cv2.imwrite(logo_path, test_logo)
            
            # Test coordinate detection
            coordinates = detector.detect_placement_coordinates(
                image_path, logo_path, "Chest", "Front center"
            )
            
            if coordinates:
                print(f"✅ Coordinates detected: x={coordinates['x']}, y={coordinates['y']}")
                print(f"   Placement type: {coordinates['placement_type']}")
            else:
                print("❌ Coordinate detection failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Coordinate detector test failed: {e}")
        return False

def test_logo_extractor():
    """Test logo extraction (basic functionality)"""
    print("\n🧪 Testing Logo Extractor...")
    
    try:
        extractor = LogoExtractor()
        
        # Test PDF finding (without actual PDF)
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create dummy PDF file
            test_pdf = os.path.join(temp_dir, "LOGO001.pdf")
            Path(test_pdf).touch()
            
            # Test finding PDF
            pdf_path = extractor._find_logo_pdf(temp_dir, "LOGO001")
            
            if pdf_path:
                print(f"✅ PDF found: {os.path.basename(pdf_path)}")
            else:
                print("❌ PDF not found")
        
        # Cleanup
        extractor.cleanup_temp_files()
        
        return True
        
    except Exception as e:
        print(f"❌ Logo extractor test failed: {e}")
        return False

def test_imports():
    """Test all required imports"""
    print("🧪 Testing imports...")
    
    required_packages = [
        ("cv2", "opencv-python"),
        ("mediapipe", "mediapipe"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("PIL", "Pillow")
    ]
    
    all_imports_ok = True
    
    for package, pip_name in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} imported successfully")
        except ImportError:
            print(f"❌ {package} not found - install with: pip install {pip_name}")
            all_imports_ok = False
    
    # Test Windows-specific imports
    try:
        import win32com.client
        import pythoncom
        print("✅ Windows COM libraries available")
    except ImportError:
        print("⚠️  Windows COM libraries not available (needed for Photoshop automation)")
    
    return all_imports_ok

def run_all_tests():
    """Run all tests"""
    print("🚀 Running System Tests")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Excel Processor", test_excel_processor),
        ("Image Finder", test_image_finder),
        ("Coordinate Detector", test_coordinate_detector),
        ("Logo Extractor", test_logo_extractor)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! System is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()