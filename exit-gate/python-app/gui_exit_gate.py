#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exit Gate GUI Application
Simple Tkinter GUI untuk Exit Gate System
Compatible dengan Python 2.7
"""

from __future__ import print_function
try:
    # Python 2.7
    import Tkinter as tk
    import tkFont
except ImportError:
    # Python 3.x
    import tkinter as tk
    import tkinter.font as tkFont
import threading
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='exit_gate_gui.log'
)
logger = logging.getLogger(__name__)

class ExitGateGUI(object):
    """Main GUI Application for Exit Gate"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Exit Gate System")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # State variables
        self.gate_status = "CLOSED"
        self.last_barcode = ""
        self.transaction_count = 0
        
        # Services
        self.gate_service = None
        self.scanner = None
        self.db_service = None
        
        # GUI Components
        self.status_label = None
        self.barcode_label = None
        self.transaction_label = None
        self.log_text = None
        
        self.setup_gui()
        self.initialize_services()
        self.start_auto_listener()
        
        logger.info("Exit Gate GUI initialized")
    
    def setup_gui(self):
        """Setup GUI components"""
        # Title
        title_font = tkFont.Font(family="Arial", size=24, weight="bold")
        title_label = tk.Label(self.root, text="EXIT GATE SYSTEM", 
                              font=title_font, bg='#2c3e50', fg='white')
        title_label.pack(pady=20)
        
        # Status Frame
        status_frame = tk.Frame(self.root, bg='#34495e', relief=tk.RAISED, bd=2)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Gate Status
        status_font = tkFont.Font(family="Arial", size=16, weight="bold")
        tk.Label(status_frame, text="Gate Status:", font=status_font, 
                bg='#34495e', fg='white').grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, text="CLOSED", font=status_font,
                                    bg='#34495e', fg='#e74c3c')
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Last Barcode
        tk.Label(status_frame, text="Last Barcode:", font=status_font,
                bg='#34495e', fg='white').grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.barcode_label = tk.Label(status_frame, text="None", font=status_font,
                                     bg='#34495e', fg='#f39c12')
        self.barcode_label.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Transaction Count
        tk.Label(status_frame, text="Transactions:", font=status_font,
                bg='#34495e', fg='white').grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.transaction_label = tk.Label(status_frame, text="0", font=status_font,
                                         bg='#34495e', fg='#27ae60')
        self.transaction_label.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Control Buttons
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(pady=20)
        
        button_font = tkFont.Font(family="Arial", size=12, weight="bold")
        
        open_btn = tk.Button(button_frame, text="OPEN GATE", font=button_font,
                            bg='#27ae60', fg='white', width=12, height=2,
                            command=self.manual_open_gate)
        open_btn.grid(row=0, column=0, padx=10)
        
        close_btn = tk.Button(button_frame, text="CLOSE GATE", font=button_font,
                             bg='#e74c3c', fg='white', width=12, height=2,
                             command=self.manual_close_gate)
        close_btn.grid(row=0, column=1, padx=10)
        
        test_btn = tk.Button(button_frame, text="TEST SCAN", font=button_font,
                            bg='#3498db', fg='white', width=12, height=2,
                            command=self.test_barcode_scan)
        test_btn.grid(row=0, column=2, padx=10)
        
        # Log Display
        log_frame = tk.Frame(self.root, bg='#2c3e50')
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(log_frame, text="System Log:", font=status_font,
                bg='#2c3e50', fg='white').pack(anchor=tk.W)
        
        # Text widget with scrollbar
        text_frame = tk.Frame(log_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(text_frame, bg='#1a1a1a', fg='#00ff00',
                               font=('Courier', 10), wrap=tk.WORD)
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Initializing...", 
                                  relief=tk.SUNKEN, anchor=tk.W,
                                  bg='#34495e', fg='white')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.log("GUI Setup completed")
    
    def initialize_services(self):
        """Initialize gate services"""
        try:
            # Import services
            from gate_service import gate_service
            from usb_barcode_scanner import usb_barcode_scanner
            from database_service import db_service
            
            self.gate_service = gate_service
            self.scanner = usb_barcode_scanner
            self.db_service = db_service
            
            # Add barcode listener
            self.scanner.add_listener(self.on_barcode_scan)
            
            # Add gate status listener
            self.gate_service.add_status_listener(self.on_gate_status_change)
            
            self.log("Services initialized successfully")
            self.update_status_bar("Ready - Listening for barcode scans...")
            
        except Exception as e:
            error_msg = "Failed to initialize services: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            self.update_status_bar("ERROR: " + error_msg)
            logger.error(error_msg)
    
    def start_auto_listener(self):
        """Start automatic barcode listening in background"""
        def auto_listen():
            self.log("Auto-listener started")
            while True:
                try:
                    # Keep the scanner active
                    if self.scanner and hasattr(self.scanner, 'is_enabled'):
                        if not self.scanner.is_enabled():
                            self.scanner.enable()
                    
                    time.sleep(1)  # Check every second
                    
                except Exception as e:
                    self.log("Auto-listener error: {}".format(str(e)))
                    time.sleep(5)  # Wait 5 seconds before retry
        
        # Start in background thread
        listener_thread = threading.Thread(target=auto_listen)
        listener_thread.daemon = True
        listener_thread.start()
    
    def on_barcode_scan(self, result):
        """Handle barcode scan events"""
        try:
            barcode = result.code
            is_valid = result.is_valid
            
            self.log("BARCODE SCANNED: {} (valid: {})".format(barcode, is_valid))
            
            # Update UI
            self.root.after(0, self.update_barcode_display, barcode)
            
            if is_valid:
                # Process the barcode
                self.root.after(0, self.process_vehicle_exit, barcode)
            else:
                self.log("Invalid barcode - ignoring")
                
        except Exception as e:
            error_msg = "Barcode scan error: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            logger.error(error_msg)
    
    def process_vehicle_exit(self, barcode):
        """Process vehicle exit"""
        try:
            self.log("Processing vehicle exit for: {}".format(barcode))
            
            # Check database for transaction
            if self.db_service:
                result = self.db_service.process_vehicle_exit(barcode, "SYSTEM", "EXIT_GATE_01")
                
                if result.get('success'):
                    self.log("Transaction found - opening gate")
                    
                    # Open gate
                    if self.gate_service:
                        gate_result = self.gate_service.open_gate(10)  # Auto close in 10 seconds
                        
                        if gate_result:
                            self.transaction_count += 1
                            self.update_transaction_count()
                            self.log("Gate opened successfully")
                        else:
                            self.log("ERROR: Failed to open gate")
                    else:
                        self.log("ERROR: Gate service not available")
                else:
                    self.log("No valid transaction found for: {}".format(barcode))
            else:
                # If no database, just open gate for testing
                self.log("No database - opening gate for test")
                if self.gate_service:
                    self.gate_service.open_gate(5)
                    self.transaction_count += 1
                    self.update_transaction_count()
                
        except Exception as e:
            error_msg = "Exit processing error: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            logger.error(error_msg)
    
    def on_gate_status_change(self, status):
        """Handle gate status changes"""
        self.gate_status = status
        self.root.after(0, self.update_gate_status)
        self.log("Gate status: {}".format(status))
    
    def update_gate_status(self):
        """Update gate status display"""
        if self.gate_status == "OPEN":
            self.status_label.config(text="OPEN", fg='#27ae60')
        elif self.gate_status == "CLOSED":
            self.status_label.config(text="CLOSED", fg='#e74c3c')
        elif self.gate_status == "OPENING":
            self.status_label.config(text="OPENING", fg='#f39c12')
        elif self.gate_status == "CLOSING":
            self.status_label.config(text="CLOSING", fg='#f39c12')
        else:
            self.status_label.config(text=self.gate_status, fg='#95a5a6')
    
    def update_barcode_display(self, barcode):
        """Update barcode display"""
        self.last_barcode = barcode
        self.barcode_label.config(text=barcode)
    
    def update_transaction_count(self):
        """Update transaction counter"""
        self.transaction_label.config(text=str(self.transaction_count))
    
    def manual_open_gate(self):
        """Manual gate open"""
        try:
            if self.gate_service:
                result = self.gate_service.open_gate()
                self.log("Manual gate open: {}".format("Success" if result else "Failed"))
            else:
                self.log("ERROR: Gate service not available")
        except Exception as e:
            self.log("ERROR: Manual open failed: {}".format(str(e)))
    
    def manual_close_gate(self):
        """Manual gate close"""
        try:
            if self.gate_service:
                result = self.gate_service.close_gate()
                self.log("Manual gate close: {}".format("Success" if result else "Failed"))
            else:
                self.log("ERROR: Gate service not available")
        except Exception as e:
            self.log("ERROR: Manual close failed: {}".format(str(e)))
    
    def test_barcode_scan(self):
        """Test barcode scan"""
        try:
            test_barcode = "TEST{}".format(int(time.time()) % 10000)
            self.log("Testing barcode scan: {}".format(test_barcode))
            
            if self.scanner:
                self.scanner.simulate_scan(test_barcode)
            else:
                self.log("ERROR: Scanner not available")
                
        except Exception as e:
            self.log("ERROR: Test scan failed: {}".format(str(e)))
    
    def log(self, message):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = "[{}] {}\n".format(timestamp, message)
        
        # Add to text widget
        if self.log_text:
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)  # Scroll to bottom
            
            # Keep only last 100 lines
            lines = self.log_text.get("1.0", tk.END).split('\n')
            if len(lines) > 100:
                self.log_text.delete("1.0", "{}".format(len(lines) - 100) + ".0")
        
        # Also log to file
        logger.info(message)
        print(log_message.strip())
    
    def update_status_bar(self, message):
        """Update status bar"""
        if self.status_bar:
            self.status_bar.config(text=message)
    
    def run(self):
        """Start the GUI application"""
        self.log("Exit Gate GUI started")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        try:
            self.log("Shutting down...")
            
            # Cleanup services
            if self.scanner:
                self.scanner.cleanup()
            
            if self.gate_service:
                self.gate_service.cleanup()
            
            self.root.destroy()
            
        except Exception as e:
            logger.error("Shutdown error: {}".format(str(e)))
            self.root.destroy()

def main():
    """Main function"""
    try:
        app = ExitGateGUI()
        app.run()
    except Exception as e:
        print("Application error: {}".format(str(e)))
        logger.error("Application error: {}".format(str(e)))

if __name__ == "__main__":
    main()
