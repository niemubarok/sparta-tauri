#!/usr/bin/env python3
"""Script to fix await issues in main.py"""

import re

def fix_main_file():
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace all instances of await self.primary_gate.initialize() with synchronous calls
    content = re.sub(
        r'await self\.primary_gate\.initialize\(\)',
        '''try:
                    # Initialize gate (synchronous method)
                    if hasattr(self.primary_gate, 'initialize'):
                        self.primary_gate.initialize()
                except Exception as e:
                    logger.warning(f"Gate initialization failed: {e}")''',
        content
    )
    
    # Fix start_monitoring calls
    content = re.sub(
        r'await self\.primary_gate\.start_monitoring\(\)',
        '''try:
                    # Start monitoring (synchronous method)
                    if hasattr(self.primary_gate, 'start_monitoring'):
                        self.primary_gate.start_monitoring()
                except Exception as e:
                    logger.warning(f"Gate monitoring start failed: {e}")''',
        content
    )
    
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed main.py file")

if __name__ == "__main__":
    fix_main_file()
