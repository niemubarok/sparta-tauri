#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced GUI with Verbose Debug Logging
Adds extensive logging to diagnose button click issues
"""

import sys
import os

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

import time
import threading
from datetime import datetime

def verbose_log(message):
    """Enhanced logging function"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    return full_message

class DebugGUI:
    """Enhanced debug GUI with verbose logging"""
    
    def __init__(self):
        verbose_log("🚀 Initializing Debug GUI...")
        
        self.root = tk.Tk()
        self.root.title("Enhanced Debug Gate Test")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        self.gate_service = None
        self.button_click_count = 0
        self.log_text = None
        
        self.setup_gui()
        self.init_gate_service()
        verbose_log("✅ Debug GUI initialized")
    
    def setup_gui(self):
        """Setup GUI with enhanced debugging"""
        verbose_log("Setting up GUI components...")
        
        # Title
        title_font = tkFont.Font(family="Arial", size=18, weight="bold")
        title = tk.Label(self.root, text="ENHANCED DEBUG GATE TEST", 
                        font=title_font, bg='#2c3e50', fg='white')
        title.pack(pady=10)
        
        # Status display
        self.status_frame = tk.Frame(self.root, bg='#34495e', relief=tk.RAISED, bd=2)
        self.status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.status_label = tk.Label(self.status_frame, text="Status: Initializing...", 
                                   font=('Arial', 12, 'bold'), bg='#34495e', fg='white')
        self.status_label.pack(pady=5)
        
        self.click_count_label = tk.Label(self.status_frame, text="Button Clicks: 0", 
                                        font=('Arial', 12), bg='#34495e', fg='#f39c12')
        self.click_count_label.pack(pady=5)
        
        # Test buttons with enhanced event handling
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(pady=20)
        
        button_font = tkFont.Font(family="Arial", size=12, weight="bold")
        
        # Enhanced button creation with verbose event binding
        self.open_btn = tk.Button(button_frame, text="OPEN GATE", font=button_font,
                                bg='#27ae60', fg='white', width=15, height=2)
        self.open_btn.bind('<Button-1>', self.enhanced_open_gate)
        self.open_btn.grid(row=0, column=0, padx=10)
        
        self.close_btn = tk.Button(button_frame, text="CLOSE GATE", font=button_font,
                                 bg='#e74c3c', fg='white', width=15, height=2)
        self.close_btn.bind('<Button-1>', self.enhanced_close_gate)
        self.close_btn.grid(row=0, column=1, padx=10)
        
        self.test_btn = tk.Button(button_frame, text="QUICK TEST", font=button_font,
                                bg='#3498db', fg='white', width=15, height=2)
        self.test_btn.bind('<Button-1>', self.enhanced_quick_test)
        self.test_btn.grid(row=0, column=2, padx=10)
        
        # Also add command-based handlers for comparison
        self.cmd_open_btn = tk.Button(button_frame, text="CMD OPEN", font=button_font,
                                    bg='#9b59b6', fg='white', width=15, height=2,
                                    command=self.command_open_gate)
        self.cmd_open_btn.grid(row=1, column=0, padx=10, pady=10)
        
        self.cmd_close_btn = tk.Button(button_frame, text="CMD CLOSE", font=button_font,
                                     bg='#8e44ad', fg='white', width=15, height=2,
                                     command=self.command_close_gate)
        self.cmd_close_btn.grid(row=1, column=1, padx=10, pady=10)
        
        # Log display
        log_frame = tk.Frame(self.root, bg='#2c3e50')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(log_frame, text="Verbose Debug Log:", font=('Arial', 12, 'bold'),
                bg='#2c3e50', fg='white').pack(anchor=tk.W)
        
        # Text widget with scrollbar
        text_frame = tk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(text_frame, bg='#1a1a1a', fg='#00ff00',
                              font=('Courier', 9), wrap=tk.WORD)
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        verbose_log("✅ GUI components setup completed")
    
    def log_to_gui(self, message):
        """Log message to GUI text widget"""
        if self.log_text:
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
    
    def init_gate_service(self):
        """Initialize gate service with verbose logging"""
        verbose_log("🔧 Initializing gate service...")
        try:
            from app.gate_service import gate_service
            self.gate_service = gate_service
            
            if self.gate_service:
                verbose_log("✅ Gate service imported successfully")
                self.log_to_gui("✅ Gate service available")
                
                # Get diagnostic info
                diag = self.gate_service.get_diagnostic_info()
                verbose_log(f"Control Mode: {diag.get('control_mode')}")
                verbose_log(f"Current Status: {diag.get('current_status')}")
                
                self.update_status("Ready - Gate service available")
                
                # Add status listener
                self.gate_service.add_status_listener(self.on_gate_status_change)
                verbose_log("✅ Status listener added")
                
            else:
                verbose_log("❌ Gate service is None")
                self.update_status("ERROR - Gate service is None")
                
        except Exception as e:
            verbose_log(f"❌ Gate service initialization failed: {e}")
            self.update_status(f"ERROR - {e}")
            import traceback
            traceback.print_exc()
    
    def update_status(self, status):
        """Update status display"""
        if self.status_label:
            self.status_label.config(text=f"Status: {status}")
        verbose_log(f"Status updated: {status}")
    
    def update_click_count(self):
        """Update button click counter"""
        self.button_click_count += 1
        if self.click_count_label:
            self.click_count_label.config(text=f"Button Clicks: {self.button_click_count}")
        verbose_log(f"Click count updated: {self.button_click_count}")
    
    def on_gate_status_change(self, status):
        """Handle gate status changes"""
        verbose_log(f"🔄 Gate status changed: {status}")
        self.log_to_gui(f"🔄 Gate status: {status}")
    
    # Enhanced event handlers with verbose logging
    def enhanced_open_gate(self, event):
        """Enhanced open gate with detailed event logging"""
        verbose_log("🖱️ OPEN GATE button clicked (event-based)")
        verbose_log(f"Event details: {event}")
        verbose_log(f"Widget: {event.widget}")
        verbose_log(f"Coordinates: ({event.x}, {event.y})")
        
        self.update_click_count()
        self.log_to_gui("🔴 OPEN GATE button clicked (event)")
        
        try:
            verbose_log("Calling gate open logic...")
            self.execute_gate_open("EVENT-BASED")
        except Exception as e:
            verbose_log(f"❌ Enhanced open gate failed: {e}")
            import traceback
            traceback.print_exc()
    
    def enhanced_close_gate(self, event):
        """Enhanced close gate with detailed event logging"""
        verbose_log("🖱️ CLOSE GATE button clicked (event-based)")
        verbose_log(f"Event details: {event}")
        
        self.update_click_count()
        self.log_to_gui("🔵 CLOSE GATE button clicked (event)")
        
        try:
            verbose_log("Calling gate close logic...")
            self.execute_gate_close("EVENT-BASED")
        except Exception as e:
            verbose_log(f"❌ Enhanced close gate failed: {e}")
            import traceback
            traceback.print_exc()
    
    def enhanced_quick_test(self, event):
        """Enhanced quick test"""
        verbose_log("🖱️ QUICK TEST button clicked")
        
        self.update_click_count()
        self.log_to_gui("🟡 QUICK TEST started")
        
        try:
            verbose_log("Running quick test sequence...")
            
            # Test open
            verbose_log("Step 1: Testing open...")
            result1 = self.execute_gate_open("QUICK-TEST")
            
            # Wait
            verbose_log("Step 2: Waiting 2 seconds...")
            time.sleep(2)
            
            # Test close
            verbose_log("Step 3: Testing close...")
            result2 = self.execute_gate_close("QUICK-TEST")
            
            if result1 and result2:
                verbose_log("✅ Quick test completed successfully")
                self.log_to_gui("✅ Quick test: SUCCESS")
            else:
                verbose_log("❌ Quick test failed")
                self.log_to_gui("❌ Quick test: FAILED")
                
        except Exception as e:
            verbose_log(f"❌ Quick test failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Command-based handlers for comparison
    def command_open_gate(self):
        """Command-based open gate"""
        verbose_log("🖱️ CMD OPEN button clicked (command-based)")
        
        self.update_click_count()
        self.log_to_gui("🔴 CMD OPEN button clicked (command)")
        
        try:
            self.execute_gate_open("COMMAND-BASED")
        except Exception as e:
            verbose_log(f"❌ Command open gate failed: {e}")
            import traceback
            traceback.print_exc()
    
    def command_close_gate(self):
        """Command-based close gate"""
        verbose_log("🖱️ CMD CLOSE button clicked (command-based)")
        
        self.update_click_count()
        self.log_to_gui("🔵 CMD CLOSE button clicked (command)")
        
        try:
            self.execute_gate_close("COMMAND-BASED")
        except Exception as e:
            verbose_log(f"❌ Command close gate failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Core gate operation methods
    def execute_gate_open(self, method_type):
        """Execute gate open with detailed logging"""
        verbose_log(f"🔓 Executing gate open ({method_type})...")
        
        if not self.gate_service:
            verbose_log("❌ Gate service not available")
            self.log_to_gui("❌ Gate service not available")
            return False
        
        verbose_log("Gate service is available, calling open_gate()...")
        
        try:
            result = self.gate_service.open_gate()
            verbose_log(f"Gate open result: {result}")
            
            if result:
                verbose_log(f"✅ Gate opened successfully ({method_type})")
                self.log_to_gui(f"✅ Gate OPENED ({method_type})")
                self.update_status("Gate: OPEN")
                return True
            else:
                verbose_log(f"❌ Gate open failed ({method_type})")
                self.log_to_gui(f"❌ Gate open FAILED ({method_type})")
                self.update_status("Gate: OPEN FAILED")
                return False
                
        except Exception as e:
            verbose_log(f"❌ Exception during gate open ({method_type}): {e}")
            self.log_to_gui(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def execute_gate_close(self, method_type):
        """Execute gate close with detailed logging"""
        verbose_log(f"🔒 Executing gate close ({method_type})...")
        
        if not self.gate_service:
            verbose_log("❌ Gate service not available")
            self.log_to_gui("❌ Gate service not available")
            return False
        
        verbose_log("Gate service is available, calling close_gate()...")
        
        try:
            result = self.gate_service.close_gate()
            verbose_log(f"Gate close result: {result}")
            
            if result:
                verbose_log(f"✅ Gate closed successfully ({method_type})")
                self.log_to_gui(f"✅ Gate CLOSED ({method_type})")
                self.update_status("Gate: CLOSED")
                return True
            else:
                verbose_log(f"❌ Gate close failed ({method_type})")
                self.log_to_gui(f"❌ Gate close FAILED ({method_type})")
                self.update_status("Gate: CLOSE FAILED")
                return False
                
        except Exception as e:
            verbose_log(f"❌ Exception during gate close ({method_type}): {e}")
            self.log_to_gui(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self):
        """Start the debug GUI"""
        verbose_log("🚀 Starting Enhanced Debug GUI...")
        self.log_to_gui("🚀 Enhanced Debug GUI started")
        self.log_to_gui("Click buttons to test gate functionality")
        self.log_to_gui("Watch console and this log for detailed debugging")
        self.root.mainloop()

def main():
    """Main function"""
    print("=" * 60)
    print("ENHANCED GUI DEBUG TEST")
    print("=" * 60)
    print("This GUI provides verbose logging for every button click")
    print("Use this to diagnose why GUI buttons aren't working")
    print("Watch both console and GUI log for detailed output")
    print("=" * 60)
    
    try:
        app = DebugGUI()
        app.run()
    except Exception as e:
        verbose_log(f"❌ GUI failed to start: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
