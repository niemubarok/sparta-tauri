#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launcher script for Exit Gate GUI Application
"""

import sys
import os

# Add app directory to Python path
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

# Change to app directoryd
os.chdir(app_dir)

# Import and run the GUI application
try:
    import gui_exit_gate
    
    if __name__ == '__main__':
        gui_exit_gate.main()
        
except Exception as e:
    print("Error starting GUI application: {}".format(str(e)))
    sys.exit(1)
