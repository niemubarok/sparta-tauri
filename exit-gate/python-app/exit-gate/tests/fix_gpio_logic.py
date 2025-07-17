#!/usr/bin/env python
# Fix GPIO Logic - Set active_high = False
from config import config
config.set('gpio', 'active_high', 'False')
config.save_config()
print("GPIO config updated: active_high = False")
print("Restart the GUI to apply changes")
