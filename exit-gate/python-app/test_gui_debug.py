#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI Debug Test - Specifically test GUI button clicks and events
"""

import sys
import os
import time
import threading

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    # Python 2.7
    import Tkinter as tk
    import tkFont
except ImportError:
    # Python 3.x
    import tkinter as tk
    import tkinter.font as tkFont

def create_debug_gui():
    """Create a minimal debug GUI to test gate operations"""
    root = tk.Tk()
    root.title("Gate Debug Test")
    root.geometry("800x600")
    root.configure(bg='#2c3e50')
    
    # Initialize gate service
    gate_service = None
    log_text = None
    
    def log(message):
        """Log message to text widget and console"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        print(log_message.strip())
        
        if log_text:
            log_text.insert(tk.END, log_message)
            log_text.see(tk.END)
    
    def init_gate_service():
        """Initialize gate service"""
        nonlocal gate_service
        try:
            log("Initializing gate service...")
            from app.gate_service import gate_service as gs
            gate_service = gs
            
            if gate_service:
                log("✅ Gate service initialized successfully")
                
                # Add status listener
                def status_listener(status):
                    log(f"Gate status changed: {status}")
                
                gate_service.add_status_listener(status_listener)
                log("✅ Status listener added")
                
                # Get diagnostic info
                diag = gate_service.get_diagnostic_info()
                log(f"Control Mode: {diag.get('control_mode')}")
                log(f"GPIO Available: {diag.get('gpio_available')}")
                
                return True
            else:
                log("❌ Gate service is None")
                return False
                
        except Exception as e:
            log(f"❌ Failed to initialize gate service: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_open_gate():
        """Test open gate button"""
        log("🔴 OPEN GATE BUTTON CLICKED")
        try:
            if not gate_service:
                log("❌ Gate service not available")
                return
            
            log("Calling gate_service.open_gate()...")
            result = gate_service.open_gate()
            
            if result:
                log("✅ Gate opened successfully!")
                status = gate_service.get_current_status()
                log(f"Current status: {status}")
            else:
                log("❌ Failed to open gate")
                
        except Exception as e:
            log(f"❌ Open gate error: {e}")
            import traceback
            traceback.print_exc()
    
    def test_close_gate():
        """Test close gate button"""
        log("🔵 CLOSE GATE BUTTON CLICKED")
        try:
            if not gate_service:
                log("❌ Gate service not available")
                return
            
            log("Calling gate_service.close_gate()...")
            result = gate_service.close_gate()
            
            if result:
                log("✅ Gate closed successfully!")
                status = gate_service.get_current_status()
                log(f"Current status: {status}")
            else:
                log("❌ Failed to close gate")
                
        except Exception as e:
            log(f"❌ Close gate error: {e}")
            import traceback
            traceback.print_exc()
    
    def test_barcode_process():
        """Test barcode processing"""
        test_barcode = f"DEBUG{int(time.time()) % 1000}"
        log(f"🟡 TESTING BARCODE: {test_barcode}")
        
        try:
            if not gate_service:
                log("❌ Gate service not available")
                return
            
            # Simulate the barcode processing that happens in GUI
            log("Step 1: Processing barcode...")
            log(f"Barcode: {test_barcode}")
            log("Step 2: Debug mode check (assuming ON)...")
            log("Step 3: Opening gate for barcode...")
            
            result = gate_service.open_gate()
            
            if result:
                log("✅ Gate opened for barcode!")
                status = gate_service.get_current_status()
                log(f"Status after barcode: {status}")
                
                # Auto-close after 2 seconds
                def auto_close():
                    time.sleep(2)
                    log("Auto-closing gate...")
                    close_result = gate_service.close_gate()
                    if close_result:
                        log("✅ Gate auto-closed")
                    else:
                        log("❌ Auto-close failed")
                
                # Start auto-close in background
                thread = threading.Thread(target=auto_close)
                thread.daemon = True
                thread.start()
                
            else:
                log("❌ Failed to open gate for barcode")
                
        except Exception as e:
            log(f"❌ Barcode processing error: {e}")
            import traceback
            traceback.print_exc()
    
    def test_gate_diagnostics():
        """Test gate diagnostics"""
        log("🟣 TESTING GATE DIAGNOSTICS")
        try:
            if not gate_service:
                log("❌ Gate service not available")
                return
            
            # Get diagnostic info
            diag = gate_service.get_diagnostic_info()
            log("Gate Service Diagnostics:")
            for key, value in diag.items():
                log(f"  {key}: {value}")
            
            # Test hardware
            log("Testing hardware...")
            hw_test = gate_service.test_hardware()
            log(f"Hardware test: {'✅ PASSED' if hw_test.get('overall_success') else '❌ FAILED'}")
            
            # Get current status
            status = gate_service.get_current_status()
            log(f"Current gate status: {status}")
            
        except Exception as e:
            log(f"❌ Diagnostics error: {e}")
            import traceback
            traceback.print_exc()
    
    # Create UI
    # Title
    title_font = tkFont.Font(family="Arial", size=20, weight="bold")
    title_label = tk.Label(root, text="GATE DEBUG TEST", 
                          font=title_font, bg='#2c3e50', fg='white')
    title_label.pack(pady=20)
    
    # Button frame
    button_frame = tk.Frame(root, bg='#2c3e50')
    button_frame.pack(pady=20)
    
    button_font = tkFont.Font(family="Arial", size=12, weight="bold")
    
    # Gate control buttons
    open_btn = tk.Button(button_frame, text="OPEN GATE", font=button_font,
                        bg='#27ae60', fg='white', width=15, height=2,
                        command=test_open_gate)
    open_btn.grid(row=0, column=0, padx=10)
    
    close_btn = tk.Button(button_frame, text="CLOSE GATE", font=button_font,
                         bg='#e74c3c', fg='white', width=15, height=2,
                         command=test_close_gate)
    close_btn.grid(row=0, column=1, padx=10)
    
    barcode_btn = tk.Button(button_frame, text="TEST BARCODE", font=button_font,
                           bg='#3498db', fg='white', width=15, height=2,
                           command=test_barcode_process)
    barcode_btn.grid(row=0, column=2, padx=10)
    
    diag_btn = tk.Button(button_frame, text="DIAGNOSTICS", font=button_font,
                        bg='#9b59b6', fg='white', width=15, height=2,
                        command=test_gate_diagnostics)
    diag_btn.grid(row=0, column=3, padx=10)
    
    # Log display
    log_frame = tk.Frame(root, bg='#2c3e50')
    log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    tk.Label(log_frame, text="Debug Log:", font=button_font,
            bg='#2c3e50', fg='white').pack(anchor=tk.W)
    
    # Text widget with scrollbar
    text_frame = tk.Frame(log_frame)
    text_frame.pack(fill=tk.BOTH, expand=True)
    
    log_text = tk.Text(text_frame, bg='#1a1a1a', fg='#00ff00',
                      font=('Courier', 10), wrap=tk.WORD)
    scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=log_text.yview)
    log_text.configure(yscrollcommand=scrollbar.set)
    
    log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Initialize gate service
    log("🚀 Starting Gate Debug Test")
    log("Initializing gate service...")
    init_success = init_gate_service()
    
    if init_success:
        log("✅ Gate service ready for testing")
        log("Click buttons to test gate functionality")
    else:
        log("❌ Gate service initialization failed")
    
    # Start GUI
    log("GUI ready - click buttons to test")
    root.mainloop()

if __name__ == "__main__":
    print("Starting GUI Debug Test...")
    create_debug_gui()
