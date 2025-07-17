#!/usr/bin/env python3
"""
Entry Gate GUI Application
GUI interface for entry gate control and simulation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import asyncio
import sys
import os
import logging
from datetime import datetime
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import Config
from shared.database import DatabaseService
from shared.camera import CameraService
from shared.gpio import GPIOService
from shared.audio import AudioService
from shared.printer import PrinterService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EntryGateGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Entry Gate Controller")
        self.root.geometry("800x600")
        
        # Initialize services
        self.config = Config()
        self.db = DatabaseService(self.config)
        self.camera = CameraService(self.config)
        self.gpio = GPIOService(self.config)
        self.audio = AudioService(self.config)
        self.printer = PrinterService(self.config)
        
        # State variables
        self.running = False
        self.processing = False
        self.alpr_mode = tk.BooleanVar(value=True)
        
        self.setup_ui()
        self.setup_logging()
        
    def setup_ui(self):
        """Setup the GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Entry Gate Controller", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Control panel
        control_frame = ttk.LabelFrame(main_frame, text="Control Panel", padding="10")
        control_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # ALPR mode checkbox
        ttk.Checkbutton(control_frame, text="ALPR Mode Active", 
                       variable=self.alpr_mode).grid(row=0, column=0, sticky=tk.W)
        
        # Buttons
        self.start_btn = ttk.Button(control_frame, text="Start Entry Gate", 
                                   command=self.start_gate)
        self.start_btn.grid(row=0, column=1, padx=(20, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="Stop Entry Gate", 
                                  command=self.stop_gate, state="disabled")
        self.stop_btn.grid(row=0, column=2, padx=5)
        
        self.simulate_btn = ttk.Button(control_frame, text="Simulate Vehicle", 
                                      command=self.simulate_vehicle)
        self.simulate_btn.grid(row=0, column=3, padx=5)
        
        self.test_printer_btn = ttk.Button(control_frame, text="Test Printer", 
                                          command=self.test_printer)
        self.test_printer_btn.grid(row=0, column=4, padx=5)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Status indicators
        self.status_labels = {}
        statuses = [
            ("Gate Status", "Closed"),
            ("Processing", "Idle"),
            ("Server", "Disconnected"),
            ("Camera", "Ready"),
            ("GPIO", "Simulation"),
            ("Printer", "Ready")
        ]
        
        for i, (label, initial) in enumerate(statuses):
            ttk.Label(status_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W)
            self.status_labels[label.lower().replace(" ", "_")] = ttk.Label(
                status_frame, text=initial, foreground="blue")
            self.status_labels[label.lower().replace(" ", "_")].grid(row=i, column=1, sticky=tk.W, padx=(10, 0))
        
        # Simulation frame
        sim_frame = ttk.LabelFrame(main_frame, text="Vehicle Simulation", padding="10")
        sim_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        sim_frame.columnconfigure(0, weight=1)
        
        # Simulation controls
        ttk.Label(sim_frame, text="License Plate:").grid(row=0, column=0, sticky=tk.W)
        self.plate_entry = ttk.Entry(sim_frame, width=15)
        self.plate_entry.grid(row=0, column=1, padx=(5, 0))
        self.plate_entry.insert(0, "B1234XYZ")
        
        ttk.Label(sim_frame, text="Vehicle Type:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.vehicle_type = ttk.Combobox(sim_frame, values=["Car", "Motorcycle", "Truck"], width=12)
        self.vehicle_type.grid(row=1, column=1, padx=(5, 0), pady=(5, 0))
        self.vehicle_type.set("Car")
        
        # Member simulation
        ttk.Label(sim_frame, text="Member Card:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.member_entry = ttk.Entry(sim_frame, width=15)
        self.member_entry.grid(row=2, column=1, padx=(5, 0), pady=(5, 0))
        
        ttk.Button(sim_frame, text="Loop 1 Triggered", 
                  command=lambda: self.trigger_loop(1)).grid(row=3, column=0, pady=(10, 0))
        ttk.Button(sim_frame, text="Loop 2 Triggered", 
                  command=lambda: self.trigger_loop(2)).grid(row=3, column=1, pady=(10, 0))
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), 
                      padx=(10, 0), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Log text area
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=50)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear log button
        ttk.Button(log_frame, text="Clear Log", 
                  command=self.clear_log).grid(row=1, column=0, pady=(5, 0))
        
    def setup_logging(self):
        """Setup logging to GUI"""
        class GUILogHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget
                
            def emit(self, record):
                msg = self.format(record)
                timestamp = datetime.now().strftime("%H:%M:%S")
                formatted_msg = f"[{timestamp}] {msg}\\n"
                
                # Thread-safe GUI update
                def update_gui():
                    self.text_widget.insert(tk.END, formatted_msg)
                    self.text_widget.see(tk.END)
                
                if hasattr(self.text_widget, 'after'):
                    self.text_widget.after(0, update_gui)
        
        # Add GUI handler
        gui_handler = GUILogHandler(self.log_text)
        gui_handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(gui_handler)
        
    def log_message(self, message, level="INFO"):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {level}: {message}\\n"
        self.log_text.insert(tk.END, formatted_msg)
        self.log_text.see(tk.END)
        
    def update_status(self, key, value, color="blue"):
        """Update status indicator"""
        if key in self.status_labels:
            self.status_labels[key].config(text=value, foreground=color)
            
    def start_gate(self):
        """Start the entry gate"""
        if not self.running:
            self.running = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            
            # Start gate thread
            threading.Thread(target=self.run_gate_thread, daemon=True).start()
            
            self.log_message("Entry gate started")
            self.update_status("gate_status", "Open", "green")
            
    def stop_gate(self):
        """Stop the entry gate"""
        if self.running:
            self.running = False
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            
            self.log_message("Entry gate stopped")
            self.update_status("gate_status", "Closed", "red")
            self.update_status("processing", "Idle", "blue")
            
    def run_gate_thread(self):
        """Main gate thread"""
        try:
            # Initialize services
            self.log_message("Initializing services...")
            
            # Test database connection
            try:
                self.db.test_connection()
                self.update_status("server", "Connected", "green")
                self.log_message("Database connected successfully")
            except Exception as e:
                self.update_status("server", "Error", "red")
                self.log_message(f"Database connection failed: {e}", "WARNING")
            
            # Test camera
            try:
                self.camera.capture_snapshot()
                self.update_status("camera", "Ready", "green")
                self.log_message("Camera ready")
            except Exception as e:
                self.update_status("camera", "Error", "red")
                self.log_message(f"Camera error: {e}", "WARNING")
            
            self.log_message("Entry gate is running and ready for vehicles")
            
            # Keep thread alive
            while self.running:
                threading.Event().wait(1)
                
        except Exception as e:
            self.log_message(f"Gate thread error: {e}", "ERROR")
            
    def simulate_vehicle(self):
        """Simulate a vehicle approaching"""
        if not self.running:
            messagebox.showwarning("Warning", "Please start the entry gate first")
            return
            
        # Simulate complete vehicle flow
        threading.Thread(target=self.vehicle_simulation_thread, daemon=True).start()
        
    def vehicle_simulation_thread(self):
        """Vehicle simulation thread"""
        try:
            plate = self.plate_entry.get() or "UNKNOWN"
            vehicle_type = self.vehicle_type.get()
            member_card = self.member_entry.get()
            
            self.log_message(f"Vehicle detected: {plate} ({vehicle_type})")
            self.update_status("processing", "Active", "orange")
            
            # Simulate loop 1
            self.log_message("Loop 1 triggered - vehicle approaching")
            threading.Event().wait(1)
            
            # Simulate loop 2
            self.log_message("Loop 2 triggered - vehicle positioned")
            self.log_message("Playing welcome message...")
            
            # Simulate camera capture
            self.log_message("Capturing vehicle image...")
            threading.Event().wait(2)
            
            # Simulate ALPR processing
            if self.alpr_mode.get():
                self.log_message("Processing license plate with ALPR...")
                threading.Event().wait(3)
                
                # Check if member
                is_member = bool(member_card) or plate in ["B1234XYZ", "D5678ABC"]
                
                if is_member:
                    self.log_message(f"Member detected: {plate}")
                    transaction_type = "member_entry"
                else:
                    self.log_message(f"Non-member detected: {plate}")
                    transaction_type = "non_member_entry"
            else:
                self.log_message("ALPR mode disabled - treating as non-member")
                transaction_type = "non_member_entry"
                is_member = False
            
            # Save transaction
            transaction_data = {
                "license_plate": plate if self.alpr_mode.get() else "",
                "vehicle_type": vehicle_type,
                "is_member": is_member,
                "member_card": member_card if member_card else None,
                "transaction_type": "entry",
                "gate_id": "ENTRY_GATE_01",
                "operator_id": "SYSTEM",
                "shift_id": "S1",
                "entry_fee": 0 if is_member else 2000,
                "system_type": "PREPAID"
            }
            
            try:
                # Capture entry image (simulate)
                entry_image = None
                try:
                    entry_image = self.camera.capture_snapshot()
                    if entry_image:
                        self.log_message("Entry image captured")
                    else:
                        self.log_message("Using dummy image for simulation")
                        # Create a simple dummy image
                        import io
                        try:
                            from PIL import Image
                            dummy_img = Image.new('RGB', (640, 480), color='blue')
                            img_buffer = io.BytesIO()
                            dummy_img.save(img_buffer, format='JPEG')
                            entry_image = img_buffer.getvalue()
                        except ImportError:
                            # Fallback to basic dummy data if PIL not available
                            entry_image = b"dummy_image_data"
                except Exception as e:
                    self.log_message(f"Image capture failed: {e}", "WARNING")
                
                doc_id = self.db.save_transaction(transaction_data, entry_image=entry_image)
                self.log_message(f"Transaction saved: {doc_id}")
            except Exception as e:
                self.log_message(f"Failed to save transaction: {e}", "ERROR")
            
            # Print ticket for non-members
            if not is_member:
                self.log_message("Printing parking ticket...")
                try:
                    # Get the saved transaction for printing
                    saved_transaction = self.db.get_transaction(doc_id)
                    if saved_transaction:
                        success = self.printer.print_ticket(saved_transaction)
                        if success:
                            self.log_message("Ticket printed successfully")
                        else:
                            self.log_message("Ticket print failed - using simulation", "WARNING")
                    else:
                        self.log_message("Could not retrieve transaction for printing", "WARNING")
                except Exception as e:
                    self.log_message(f"Printer error: {e}", "ERROR")
                threading.Event().wait(1)
            
            # Open gate
            self.log_message("Opening gate...")
            self.update_status("gate_status", "Opening", "orange")
            threading.Event().wait(2)
            
            self.log_message("Vehicle entered - gate closing")
            self.update_status("gate_status", "Open", "green")
            threading.Event().wait(2)
            
            self.log_message("Gate closed - ready for next vehicle")
            self.update_status("processing", "Idle", "blue")
            
        except Exception as e:
            self.log_message(f"Simulation error: {e}", "ERROR")
            self.update_status("processing", "Error", "red")
            
    def trigger_loop(self, loop_num):
        """Trigger loop sensor"""
        if not self.running:
            messagebox.showwarning("Warning", "Please start the entry gate first")
            return
            
        self.log_message(f"Manual trigger: Loop {loop_num}")
        
        if loop_num == 1:
            self.log_message("Vehicle approaching entry gate")
        elif loop_num == 2:
            self.log_message("Vehicle positioned at entry gate")
            # Start processing
            threading.Thread(target=self.vehicle_simulation_thread, daemon=True).start()
            
    def clear_log(self):
        """Clear the log"""
        self.log_text.delete(1.0, tk.END)
        
    def test_printer(self):
        """Test printer connectivity and print test page"""
        self.log_message("Testing printer...")
        
        def test_printer_thread():
            try:
                success = self.printer.test_printer()
                if success:
                    self.log_message("Printer test successful!")
                    self.update_status("printer", "OK", "green")
                else:
                    self.log_message("Printer test failed", "WARNING")
                    self.update_status("printer", "Error", "red")
            except Exception as e:
                self.log_message(f"Printer test error: {e}", "ERROR")
                self.update_status("printer", "Error", "red")
        
        threading.Thread(target=test_printer_thread, daemon=True).start()
        
    def on_closing(self):
        """Handle window closing"""
        if self.running:
            self.stop_gate()
        
        # Cleanup services
        try:
            self.audio.cleanup()
            self.gpio.cleanup()
        except:
            pass
            
        self.root.destroy()

def main():
    """Main function"""
    root = tk.Tk()
    app = EntryGateGUI(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Start GUI
    root.mainloop()

if __name__ == "__main__":
    main()
