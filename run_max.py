#!/usr/bin/env python3
"""
Max AI Assistant Launcher
Simple script to run the Max AI Assistant from the project root
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main assistant
from max_ai_assistant import main

if __name__ == "__main__":
    main()
