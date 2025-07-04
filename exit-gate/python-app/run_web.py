#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launcher script for Exit Gate Web Application
"""

import sys
import os

# Add app directory to Python path
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

# Change to app directory
os.chdir(app_dir)

# Import and run the web application
try:
    from main import app, initialize_services, cleanup
    
    if __name__ == '__main__':
        try:
            # Initialize services
            initialize_services()
            
            # Run the Flask app
            app.run(host='0.0.0.0', port=5001, debug=False)
            
        except KeyboardInterrupt:
            print("Received shutdown signal")
        except Exception as e:
            print("Application error: {}".format(str(e)))
        finally:
            cleanup()
            
except Exception as e:
    print("Error starting web application: {}".format(str(e)))
    sys.exit(1)
