#!/usr/bin/env python3
"""
Quick launcher for JADE Arm Control Game
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    required = ['pygame', 'cv2', 'serial', 'numpy']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("❌ Missing dependencies:", ', '.join(missing))
        print("\nInstall with:")
        print("  pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed")
    return True

def main():
    print("=" * 60)
    print("  JADE Robotic Arm - Game Controller")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("\n🚀 Launching control interface...")
    print("   Press ESC to exit\n")
    
    # Run the game
    script_dir = os.path.dirname(os.path.abspath(__file__))
    game_script = os.path.join(script_dir, 'arm_control_game.py')
    
    try:
        subprocess.run([sys.executable, game_script])
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
