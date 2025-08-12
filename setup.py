#!/usr/bin/env python3
"""
Setup script for Image Processing and Logo Placement Automation System
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_windows_os():
    """Check if running on Windows (required for Photoshop COM)"""
    if platform.system() != "Windows":
        print("⚠️  Warning: This project requires Windows for Photoshop COM automation")
        print(f"Current OS: {platform.system()}")
        return False
    print(f"✅ Operating System: {platform.system()}")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    directories = ["output", "temp"]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def check_photoshop():
    """Check if Photoshop is accessible"""
    print("\n🎨 Checking Photoshop availability...")
    
    try:
        import win32com.client
        import pythoncom
        
        pythoncom.CoInitialize()
        
        # Try to connect to Photoshop
        try:
            app = win32com.client.GetActiveObject("Photoshop.Application")
            version = app.Version
            print(f"✅ Connected to existing Photoshop instance: Version {version}")
            return True
        except:
            try:
                app = win32com.client.Dispatch("Photoshop.Application")
                version = app.Version
                print(f"✅ Photoshop launched successfully: Version {version}")
                app.Quit()
                return True
            except Exception as e:
                print(f"❌ Failed to connect to Photoshop: {e}")
                print("   Make sure Photoshop 2020 is installed and registered")
                return False
    except ImportError:
        print("❌ pywin32 not available - installing dependencies first")
        return False
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass

def create_sample_structure():
    """Create sample folder structure"""
    print("\n📂 Creating sample folder structure...")
    
    # Create sample image folders
    sample_dirs = [
        "sample_data/images/SupplierABC",
        "sample_data/images/SupplierXYZ", 
        "sample_data/images/SupplierDEF",
        "sample_data/logos"
    ]
    
    for directory in sample_dirs:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created: {directory}")
        except Exception as e:
            print(f"❌ Failed to create {directory}: {e}")
    
    # Create README for sample data
    readme_content = """# Sample Data Structure

## Images Folder
Place your product images in supplier subfolders:
- images/SupplierABC/ABC123Red.png
- images/SupplierABC/ABC124Blue.png
- etc.

## Logos Folder  
Place your logo PDF files:
- logos/LOGO001.pdf
- logos/LOGO002.pdf
- etc.

## Usage
1. Replace sample folders with your actual data
2. Update example_data.xlsx with your product information
3. Run: python main.py example_data.xlsx sample_data/images sample_data/logos
"""
    
    try:
        with open("sample_data/README.md", "w") as f:
            f.write(readme_content)
        print("✅ Created sample data README")
    except Exception as e:
        print(f"❌ Failed to create README: {e}")

def run_setup():
    """Main setup function"""
    print("🚀 Image Processing and Logo Placement Automation Setup")
    print("=" * 60)
    
    success = True
    
    # Check requirements
    if not check_python_version():
        success = False
    
    if not check_windows_os():
        print("   You can still use the image processing features")
        print("   But Photoshop automation will not work")
    
    # Install dependencies
    if not install_dependencies():
        success = False
    
    # Setup directories
    if not setup_directories():
        success = False
    
    # Create sample structure
    create_sample_structure()
    
    # Check Photoshop (optional)
    if platform.system() == "Windows":
        photoshop_ok = check_photoshop()
        if not photoshop_ok:
            print("\n⚠️  Photoshop check failed - you can still use other features")
    
    print("\n" + "=" * 60)
    
    if success:
        print("✅ Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Place your images in sample_data/images/ subfolders")
        print("2. Place your logo PDFs in sample_data/logos/")
        print("3. Update example_data.xlsx with your data")
        print("4. Run: python main.py example_data.xlsx sample_data/images sample_data/logos")
    else:
        print("❌ Setup completed with errors")
        print("   Please fix the issues above before proceeding")
    
    return success

if __name__ == "__main__":
    run_setup()