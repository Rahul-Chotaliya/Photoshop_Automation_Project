#!/usr/bin/env python3
"""
Setup script for Photoshop Automation Project
"""

import os
import sys
import subprocess
import json

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    if os.path.exists('.venv'):
        print("✅ Virtual environment already exists")
        return True
    
    try:
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', '.venv'], check=True)
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        print("Please install python3-venv package:")
        print("  Ubuntu/Debian: sudo apt install python3-venv")
        return False

def install_dependencies():
    """Install Python dependencies"""
    try:
        print("📦 Installing dependencies...")
        pip_cmd = ['.venv/bin/pip'] if os.name != 'nt' else ['.venv\\Scripts\\pip']
        subprocess.run(pip_cmd + ['install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        'input/excel_files',
        'input/assets/logos',
        'output',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✅ Directories created successfully")

def update_settings():
    """Update settings.json to enable Photoshop export"""
    settings_path = 'config/settings.json'
    
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            # Enable Photoshop export
            settings['enable_photoshop_export'] = True
            
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
            
            print("✅ Settings updated successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to update settings: {e}")
            return False
    else:
        print("❌ Settings file not found")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Photoshop Automation Project")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create virtual environment
    if not create_virtual_environment():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create directories
    create_directories()
    
    # Update settings
    update_settings()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    print("   Linux/Mac: source .venv/bin/activate")
    print("   Windows: .venv\\Scripts\\activate")
    print("2. Prepare your files (see SETUP_GUIDE.md)")
    print("3. Run the application:")
    print("   python -m gui.interface")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)