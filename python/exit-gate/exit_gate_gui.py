#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exit Gate GUI Application
Simple Tkinter GUI that auto-starts and listens for barcode scans
Compatible with Python 2.7
"""

from __future__ import absolute_import, print_function, unicode_literals

import sys
import os
import time
import logging
import threading
from datetime import datetime

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

# Python 2.7 compatible imports
try:
    import Tkinter as tk
    from Tkinter import ttk, messagebox
except ImportError:
    import tkinter as tk
    from tkinter import ttk, messagebox

# Try to import printer service
try:
    from printer import PrinterService
    from config import Config
    PRINTER_AVAILABLE = True
except ImportError as e:
    print("Warning: Printer service not available:", e)
    PRINTER_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExitGateGUI(object):
    """Exit Gate GUI Application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Exit Gate Control System")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # State variables
        self.gate_status = "CLOSED"
        self.last_scan = None
        self.transaction_count = 0
        self.auto_listen = True
        
        # Services (will be imported when needed)
        self.gate_service = None
        self.barcode_scanner = None
        self.db_service = None
        
        # Initialize printer service
        if PRINTER_AVAILABLE:
            try:
                config = Config()
                self.printer = PrinterService(config)
                logger.info("Printer service initialized")
            except Exception as e:
                logger.error("Failed to initialize printer: %s", e)
                self.printer = None
        else:
            self.printer = None
        
        # Create GUI
        self.create_widgets()
        self.setup_services()
        self.start_auto_listen()
        
        # Auto-maximize on Raspberry Pi
        try:
            self.root.state('zoomed')  # Linux
        except:
            try:
                self.root.state('normal')  # Fallback
            except:
                pass
    
    def create_widgets(self):
        """Create GUI widgets"""
        
        # Title
        title_frame = tk.Frame(self.root, bg='#34495e', height=80)
        title_frame.pack(fill='x', padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="EXIT GATE CONTROL SYSTEM", 
                              font=('Arial', 24, 'bold'), 
                              fg='white', bg='#34495e')
        title_label.pack(expand=True)
        
        # Status Frame
        status_frame = tk.Frame(self.root, bg='#ecf0f1', height=120)
        status_frame.pack(fill='x', padx=10, pady=5)
        status_frame.pack_propagate(False)
        
        # Gate Status
        self.gate_status_label = tk.Label(status_frame, text="Gate Status: CLOSED", 
                                         font=('Arial', 18, 'bold'), 
                                         fg='red', bg='#ecf0f1')
        self.gate_status_label.pack(pady=10)
        
        # Last Scan
        self.last_scan_label = tk.Label(status_frame, text="Last Scan: None", 
                                       font=('Arial', 14), 
                                       fg='#2c3e50', bg='#ecf0f1')
        self.last_scan_label.pack()
        
        # Transaction Count
        self.transaction_label = tk.Label(status_frame, text="Transactions Today: 0", 
                                         font=('Arial', 14), 
                                         fg='#2c3e50', bg='#ecf0f1')
        self.transaction_label.pack()
        
        # Control Buttons Frame
        control_frame = tk.Frame(self.root, bg='#2c3e50')
        control_frame.pack(fill='x', padx=10, pady=10)
        
        # Manual Control Buttons
        self.open_button = tk.Button(control_frame, text="OPEN GATE", 
                                    font=('Arial', 16, 'bold'),
                                    bg='#27ae60', fg='white',
                                    width=15, height=2,
                                    command=self.manual_open_gate)
        self.open_button.pack(side='left', padx=10)
        
        self.close_button = tk.Button(control_frame, text="CLOSE GATE", 
                                     font=('Arial', 16, 'bold'),
                                     bg='#e74c3c', fg='white',
                                     width=15, height=2,
                                     command=self.manual_close_gate)
        self.close_button.pack(side='left', padx=10)
        
        # Test Button
        self.test_button = tk.Button(control_frame, text="TEST SCAN", 
                                    font=('Arial', 16, 'bold'),
                                    bg='#3498db', fg='white',
                    width=15, height=2,
                                    command=self.test_scan)
        self.test_button.pack(side='left', padx=10)
        
        # Test Printer Button
        if PRINTER_AVAILABLE:
            self.test_printer_button = tk.Button(control_frame, text="TEST PRINTER", 
                                                font=('Arial', 16, 'bold'),
                                                bg='#9b59b6', fg='white',
                                                width=15, height=2,
                                                command=self.test_printer)
            self.test_printer_button.pack(side='left', padx=10)
        
        # Auto Listen Toggle
        self.listen_var = tk.BooleanVar(value=True)
        self.listen_checkbox = tk.Checkbutton(control_frame, text="Auto Listen", 
                                             font=('Arial', 14),
                                             fg='white', bg='#2c3e50',
                                             variable=self.listen_var,
                                             command=self.toggle_auto_listen)
        self.listen_checkbox.pack(side='right', padx=10)
        
        # Log Frame
        log_frame = tk.Frame(self.root, bg='#2c3e50')
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        log_label = tk.Label(log_frame, text="System Log", 
                            font=('Arial', 14, 'bold'), 
                            fg='white', bg='#2c3e50')
        log_label.pack(anchor='w')
        
        # Log Text with Scrollbar
        log_text_frame = tk.Frame(log_frame)
        log_text_frame.pack(fill='both', expand=True)
        
        self.log_text = tk.Text(log_text_frame, font=('Courier', 10), 
                               bg='#1a1a1a', fg='#00ff00',
                               wrap='word', height=15)
        
        scrollbar = tk.Scrollbar(log_text_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Footer
        footer_frame = tk.Frame(self.root, bg='#34495e', height=40)
        footer_frame.pack(fill='x', side='bottom')
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(footer_frame, text="Exit Gate System v1.0 - Ready", 
                               font=('Arial', 10), 
                               fg='white', bg='#34495e')
        footer_label.pack(expand=True)
        
    def setup_services(self):
        """Initialize services"""
        try:
            # Import services
            from gate_service import gate_service
            from usb_barcode_scanner import usb_barcode_scanner
            from database_service import db_service
            
            self.gate_service = gate_service
            self.barcode_scanner = usb_barcode_scanner
            self.db_service = db_service
            
            # Add barcode listener
            self.barcode_scanner.add_listener(self.handle_barcode_scan)
            
            self.log_message("✅ Services initialized successfully")
            self.log_message("🔧 Gate control mode: {}".format(self.gate_service.get_control_mode()))
            
            # Update initial status
            self.update_gate_status(self.gate_service.get_status())
            
        except Exception as e:
            self.log_message("❌ Error initializing services: {}".format(str(e)))
            messagebox.showerror("Error", "Failed to initialize services: {}".format(str(e)))
    
    def handle_barcode_scan(self, barcode_result):
        """Handle barcode scan events"""
        self.log_message("📱 Barcode scanned: {} (valid: {})".format(
            barcode_result.code, barcode_result.is_valid))
        
        self.last_scan = barcode_result.code
        self.update_last_scan_display()
        
        if barcode_result.is_valid and self.auto_listen:
            # Process barcode in background thread
            threading.Thread(target=self.process_barcode, args=(barcode_result.code,)).start()
        else:
            self.log_message("⚠️ Barcode ignored (invalid or auto-listen disabled)")
    
    def process_barcode(self, barcode):
        """Process barcode and trigger gate"""
        try:
            self.log_message("🔄 Processing barcode: {}".format(barcode))
            
            # Try to process with database first
            if self.db_service:
                result = self.db_service.process_vehicle_exit(barcode, "GUI_OPERATOR", "EXIT_GATE_01")
                
                if result.get('success'):
                    self.log_message("✅ Transaction processed: fee = {}".format(result.get('fee', 0)))
                    self.transaction_count += 1
                    self.update_transaction_count()
                    
                    # Print exit receipt if printer available
                    if self.printer:
                        try:
                            transaction_data = result.get('transaction', {})
                            # Add exit time to transaction data
                            transaction_data['exit_time'] = datetime.now().isoformat()
                            self.printer.print_exit_receipt(transaction_data)
                            self.log_message("🖨️ Exit receipt printed successfully")
                        except Exception as print_error:
                            self.log_message("⚠️ Failed to print receipt: {}".format(print_error))
                else:
                    self.log_message("⚠️ Transaction failed: {}".format(result.get('message', 'Unknown error')))
            
            # Open gate regardless of transaction status
            self.log_message("🚪 Opening gate...")
            if self.gate_service:
                gate_result = self.gate_service.open_gate(10)  # Auto-close after 10 seconds
                if gate_result:
                    self.log_message("✅ Gate opened successfully")
                else:
                    self.log_message("❌ Failed to open gate")
            
        except Exception as e:
            self.log_message("❌ Error processing barcode: {}".format(str(e)))
    
    def manual_open_gate(self):
        """Manually open gate"""
        try:
            self.log_message("🔧 Manual gate open requested")
            if self.gate_service:
                result = self.gate_service.open_gate()
                if result:
                    self.log_message("✅ Gate opened manually")
                else:
                    self.log_message("❌ Failed to open gate manually")
        except Exception as e:
            self.log_message("❌ Error opening gate: {}".format(str(e)))
    
    def manual_close_gate(self):
        """Manually close gate"""
        try:
            self.log_message("🔧 Manual gate close requested")
            if self.gate_service:
                result = self.gate_service.close_gate()
                if result:
                    self.log_message("✅ Gate closed manually")
                else:
                    self.log_message("❌ Failed to close gate manually")
        except Exception as e:
            self.log_message("❌ Error closing gate: {}".format(str(e)))
    
    def test_scan(self):
        """Test barcode scan"""
        test_barcode = "TEST{}".format(int(time.time()) % 10000)
        self.log_message("🧪 Testing with barcode: {}".format(test_barcode))
        
        if self.barcode_scanner:
            self.barcode_scanner.simulate_scan(test_barcode)
        else:
            self.log_message("❌ Barcode scanner not available")
    
    def test_printer(self):
        """Test printer functionality"""
        if self.printer:
            try:
                self.log_message("🖨️ Testing printer...")
                test_transaction = {
                    'no_pol': 'TEST123',
                    'entry_time': '2024-01-01T10:00:00',
                    'exit_time': datetime.now().isoformat(),
                    'duration': '2 hours',
                    'fee': 5000
                }
                self.printer.print_exit_receipt(test_transaction)
                self.log_message("✅ Test receipt printed successfully")
            except Exception as e:
                self.log_message("❌ Printer test failed: {}".format(e))
        else:
            self.log_message("❌ Printer not available")
    
    def toggle_auto_listen(self):
        """Toggle auto listen mode"""
        self.auto_listen = self.listen_var.get()
        status = "enabled" if self.auto_listen else "disabled"
        self.log_message("🔊 Auto listen {}".format(status))
    
    def start_auto_listen(self):
        """Start auto listen in background"""
        def listen_loop():
            while True:
                try:
                    if self.auto_listen:
                        # Check for gate status updates
                        if self.gate_service:
                            current_status = self.gate_service.get_status()
                            if current_status != self.gate_status:
                                self.update_gate_status(current_status)
                    
                    time.sleep(1)  # Check every second
                    
                except Exception as e:
                    self.log_message("❌ Auto listen error: {}".format(str(e)))
                    time.sleep(5)  # Wait longer on error
        
        # Start background thread
        listen_thread = threading.Thread(target=listen_loop)
        listen_thread.daemon = True
        listen_thread.start()
        
        self.log_message("🔊 Auto listen started")
    
    def update_gate_status(self, status):
        """Update gate status display"""
        self.gate_status = status
        
        # Update color based on status
        if status == "OPEN":
            color = "#27ae60"  # Green
            text = "Gate Status: OPEN"
        elif status == "CLOSED":
            color = "#e74c3c"  # Red
            text = "Gate Status: CLOSED"
        elif status == "OPENING":
            color = "#f39c12"  # Orange
            text = "Gate Status: OPENING..."
        elif status == "CLOSING":
            color = "#f39c12"  # Orange
            text = "Gate Status: CLOSING..."
        else:
            color = "#95a5a6"  # Gray
            text = "Gate Status: {}".format(status)
        
        # Update in GUI thread
        self.root.after(0, lambda: self.gate_status_label.configure(text=text, fg=color))
    
    def update_last_scan_display(self):
        """Update last scan display"""
        if self.last_scan:
            text = "Last Scan: {} at {}".format(self.last_scan, datetime.now().strftime("%H:%M:%S"))
            self.root.after(0, lambda: self.last_scan_label.configure(text=text))
    
    def update_transaction_count(self):
        """Update transaction count display"""
        text = "Transactions Today: {}".format(self.transaction_count)
        self.root.after(0, lambda: self.transaction_label.configure(text=text))
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = "[{}] {}\n".format(timestamp, message)
        
        # Add to GUI log in GUI thread
        def add_to_log():
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)  # Auto-scroll to bottom
            
            # Keep only last 1000 lines
            lines = self.log_text.get("1.0", tk.END).split('\n')
            if len(lines) > 1000:
                self.log_text.delete("1.0", "{}".format(len(lines) - 1000) + ".0")
        
        self.root.after(0, add_to_log)
        
        # Also log to console
        logger.info(message)
    
    def run(self):
        """Start the GUI application"""
        try:
            self.log_message("🚀 Exit Gate GUI started")
            self.log_message("📱 Waiting for barcode scans...")
            
            # Handle window close
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Start main loop
            self.root.mainloop()
            
        except KeyboardInterrupt:
            self.log_message("🛑 Application interrupted")
        except Exception as e:
            self.log_message("❌ Application error: {}".format(str(e)))
            messagebox.showerror("Error", "Application error: {}".format(str(e)))
    
    def on_closing(self):
        """Handle application closing"""
        try:
            self.log_message("🛑 Shutting down...")
            
            # Cleanup services
            if self.gate_service:
                self.gate_service.cleanup()
            
            if self.barcode_scanner:
                self.barcode_scanner.cleanup()
            
            self.root.destroy()
            
        except Exception as e:
            logger.error("Error during shutdown: {}".format(str(e)))

def main():
    """Main entry point"""
    try:
        # Create and run GUI
        app = ExitGateGUI()
        app.run()
        
    except Exception as e:
        logger.error("Failed to start GUI: {}".format(str(e)))
        print("Error: {}".format(str(e)))
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
