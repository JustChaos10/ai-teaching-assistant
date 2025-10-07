#!/usr/bin/env python3
"""
Launcher script for the Teacher Interface
This script provides an easy way to launch the teaching module creator.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available"""
    required_modules = [
        'PyQt6',
        'cv2',
        'numpy',
        'pygame'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    return missing_modules

def install_dependencies(missing_modules):
    """Install missing dependencies"""
    if not missing_modules:
        return True
    
    print("Missing dependencies detected:")
    for module in missing_modules:
        print(f"  - {module}")
    
    response = input("\nWould you like to install them automatically? (y/n): ").lower()
    
    if response == 'y':
        pip_mapping = {
            'PyQt6': 'PyQt6',
            'cv2': 'opencv-python',
            'numpy': 'numpy',
            'pygame': 'pygame'
        }
        
        for module in missing_modules:
            pip_name = pip_mapping.get(module, module)
            print(f"Installing {pip_name}...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', pip_name])
            except subprocess.CalledProcessError:
                print(f"Failed to install {pip_name}. Please install manually.")
                return False
        
        print("Dependencies installed successfully!")
        return True
    else:
        print("Please install the missing dependencies manually and try again.")
        return False

def launch_teacher_interface():
    """Launch the teacher interface"""
    try:
        from teacher_interface import main
        print("Launching Teacher Interface...")
        return main()
    except ImportError as e:
        print(f"Error importing teacher interface: {e}")
        return 1
    except Exception as e:
        print(f"Error launching teacher interface: {e}")
        return 1

def main():
    """Main launcher function"""
    print("=" * 60)
    print("  HUMANOID TEACHING ASSISTANT - TEACHER INTERFACE")
    print("=" * 60)
    print()
    print("This interface allows you to:")
    print("• Create custom learning modules for children")
    print("• Upload images and educational resources")
    print("• Configure interaction methods (voice, placard, fingers)")
    print("• Deploy modules to the teaching assistant")
    print()
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    expected_files = ['teacher_interface.py', 'chatbot_logic.py', 'py_app.py']
    
    missing_files = [f for f in expected_files if not (current_dir / f).exists()]
    
    if missing_files:
        print("Error: Some required files are missing:")
        for file in missing_files:
            print(f"  - {file}")
        print()
        print("Please make sure you're running this script from the correct directory.")
        print("Expected directory structure:")
        print("  Capstone/")
        print("  ├── teacher_interface.py")
        print("  ├── chatbot_logic.py")
        print("  ├── py_app.py")
        print("  ├── game_manager.py")
        print("  └── image detector/")
        return 1
    
    # Check dependencies
    print("Checking dependencies...")
    missing_modules = check_dependencies()
    
    if missing_modules:
        if not install_dependencies(missing_modules):
            return 1
    
    print("All dependencies satisfied!")
    print()
    
    # Create necessary directories
    directories = [
        'teaching_modules',
        'teaching_modules/resources',
        'active_modules',
        'temp_images'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("Directory structure created.")
    print()
    
    # Launch the interface
    return launch_teacher_interface()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nLauncher interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)