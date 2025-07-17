#!/usr/bin/env python3

# Test script untuk melihat mode configuration
import os
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from src.core.config import get_settings
    
    settings = get_settings()
    print(f"Current SYSTEM_MODE: {settings.system_mode}")
    print(f"UI_AUTO_START: {settings.ui_auto_start}")
    
    if settings.system_mode == "entry_manual":
        print("🚪 Mode: Manual Entry Gate (dengan operator)")
        print("   - Operator dapat mengontrol gate secara manual")
        print("   - Interface command line untuk operator")
        
    elif settings.system_mode == "entry_manless":
        print("🤖 Mode: Manless Entry Gate (otomatis tanpa operator)")
        print("   - Gate bekerja otomatis")
        print("   - Monitoring 24/7 tanpa input operator")
        
    elif settings.system_mode == "exit_manual":
        print("🚪 Mode: Manual Exit Gate (dengan operator)")  
        print("   - Operator dapat mengontrol gate keluar secara manual")
        print("   - Interface command line untuk operator")
        
    elif settings.system_mode == "exit_manless":
        print("🤖 Mode: Manless Exit Gate (otomatis tanpa operator)")
        print("   - Gate keluar bekerja otomatis")
        print("   - Validasi pembayaran otomatis")
        
    else:
        print(f"❌ Unknown mode: {settings.system_mode}")
        
except Exception as e:
    print(f"Error: {e}")
