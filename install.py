#!/usr/bin/env python3
"""
Manual installation script for Weather CLI Tool
Author: Aidid Muhaimin Bin Mahadi
Email: aidid.muhaimin011@gmail.com
"""

import os
import sys
import subprocess

def install_package():
    """Install the weather CLI tool manually"""
    
    # Install dependencies
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "click", "requests"])
    
    # Create a simple launcher script
    launcher_content = '''#!/usr/bin/env python3
import sys
import os

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from weather_cli.cli import run_cli

if __name__ == "__main__":
    run_cli()
'''
    
    # Write launcher script
    with open("weather-cli", "w") as f:
        f.write(launcher_content)
    
    # Make it executable
    os.chmod("weather-cli", 0o755)
    
    print("✅ Weather CLI Tool installed successfully!")
    print("📝 Usage: ./weather-cli --city 'Puchong' --country 'MY'")
    print("📝 Or: python -m weather_cli.cli --city 'Puchong' --country 'MY'")

if __name__ == "__main__":
    install_package()