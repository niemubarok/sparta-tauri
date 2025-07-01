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
        
        # Set fullscreen mode
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#2c3e50')
        
        # Bind Escape key to exit fullscreen (for emergency exit)
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F11>', self.toggle_fullscreen)
        
        # State variables
        self.gate_status = "CLOSED"
        self.last_barcode = ""
        self.transaction_count = 0
        self.debug_mode = True  # Set to True for debug mode
        self.is_fullscreen = True
        
        # Services
        self.gate_service = None
        self.scanner = None
        self.db_service = None
        self.audio_service = None
        self.camera_service = None
        
        # GUI Components
        self.status_label = None
        self.barcode_label = None
        self.transaction_label = None
        self.log_text = None
        self.camera_preview_label = None
        self.camera_status_label = None
        
        self.setup_gui()
        self.initialize_services()
        self.start_auto_listener()
        
        logger.info("Exit Gate GUI initialized")
    
    def setup_gui(self):
        """Setup GUI components"""
        # Title - larger for fullscreen
        title_font = tkFont.Font(family="Arial", size=32, weight="bold")
        title_label = tk.Label(self.root, text="EXIT GATE SYSTEM", 
                              font=title_font, bg='#2c3e50', fg='white')
        title_label.pack(pady=30)
        
        # Status Frame
        status_frame = tk.Frame(self.root, bg='#34495e', relief=tk.RAISED, bd=2)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Gate Status - larger fonts for fullscreen
        status_font = tkFont.Font(family="Arial", size=20, weight="bold")
        tk.Label(status_frame, text="Gate Status:", font=status_font, 
                bg='#34495e', fg='white').grid(row=0, column=0, sticky=tk.W, padx=15, pady=8)
        
        self.status_label = tk.Label(status_frame, text="CLOSED", font=status_font,
                                    bg='#34495e', fg='#e74c3c')
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=15, pady=8)
        
        # Last Barcode
        tk.Label(status_frame, text="Last Barcode:", font=status_font,
                bg='#34495e', fg='white').grid(row=1, column=0, sticky=tk.W, padx=15, pady=8)
        
        self.barcode_label = tk.Label(status_frame, text="None", font=status_font,
                                     bg='#34495e', fg='#f39c12')
        self.barcode_label.grid(row=1, column=1, sticky=tk.W, padx=15, pady=8)
        
        # Transaction Count
        tk.Label(status_frame, text="Transactions:", font=status_font,
                bg='#34495e', fg='white').grid(row=2, column=0, sticky=tk.W, padx=15, pady=8)
        
        self.transaction_label = tk.Label(status_frame, text="0", font=status_font,
                                         bg='#34495e', fg='#27ae60')
        self.transaction_label.grid(row=2, column=1, sticky=tk.W, padx=15, pady=8)
        
        # Barcode Input Field - larger for fullscreen
        input_frame = tk.Frame(self.root, bg='#2c3e50')
        input_frame.pack(fill=tk.X, padx=30, pady=15)
        
        input_font = tkFont.Font(family="Arial", size=18, weight="bold")
        tk.Label(input_frame, text="Barcode Input (Auto-Focus):", font=input_font,
                bg='#2c3e50', fg='white').pack(anchor=tk.W)
        
        # Entry field for barcode input - larger
        self.barcode_entry = tk.Entry(input_frame, font=input_font, width=30,
                                     bg='#ecf0f1', fg='#2c3e50', relief=tk.RAISED, bd=3)
        self.barcode_entry.pack(fill=tk.X, pady=8)
        
        # Bind Enter key to process barcode
        self.barcode_entry.bind('<Return>', self.on_barcode_entry)
        self.barcode_entry.bind('<KeyRelease>', self.on_key_release)
        
        # Auto-focus on entry field
        self.barcode_entry.focus_set()
        
        # Camera Preview Section
        camera_frame = tk.Frame(self.root, bg='#34495e', relief=tk.RAISED, bd=2)
        camera_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Camera title
        tk.Label(camera_frame, text="Camera Preview:", font=status_font, 
                bg='#34495e', fg='white').pack(anchor=tk.W, padx=15, pady=5)
        
        # Camera preview and controls container
        camera_container = tk.Frame(camera_frame, bg='#34495e')
        camera_container.pack(fill=tk.X, padx=15, pady=5)
        
        # Camera preview (left side)
        preview_frame = tk.Frame(camera_container, bg='#2c3e50', relief=tk.SUNKEN, bd=2)
        preview_frame.pack(side=tk.LEFT, padx=5)
        
        self.camera_preview_label = tk.Label(preview_frame, text="Camera Preview\n(No Image)", 
                                           font=('Arial', 12), bg='#2c3e50', fg='#bdc3c7',
                                           width=40, height=15, justify=tk.CENTER)
        self.camera_preview_label.pack(padx=10, pady=10)
        
        # Camera controls (right side)
        camera_controls_frame = tk.Frame(camera_container, bg='#34495e')
        camera_controls_frame.pack(side=tk.RIGHT, padx=15, fill=tk.Y)
        
        # Camera status
        self.camera_status_label = tk.Label(camera_controls_frame, text="Camera: Unknown", 
                                           font=('Arial', 12, 'bold'), bg='#34495e', fg='#f39c12')
        self.camera_status_label.pack(pady=5)
        
        # Camera control buttons
        camera_btn_font = tkFont.Font(family="Arial", size=10, weight="bold")
        
        capture_plate_btn = tk.Button(camera_controls_frame, text="Capture Plate", font=camera_btn_font,
                                     bg='#3498db', fg='white', width=15, height=2,
                                     command=lambda: self.capture_camera_image('plate'))
        capture_plate_btn.pack(pady=3)
        
        capture_driver_btn = tk.Button(camera_controls_frame, text="Capture Driver", font=camera_btn_font,
                                      bg='#9b59b6', fg='white', width=15, height=2,
                                      command=lambda: self.capture_camera_image('driver'))
        capture_driver_btn.pack(pady=3)
        
        capture_both_btn = tk.Button(camera_controls_frame, text="Capture Both", font=camera_btn_font,
                                    bg='#e67e22', fg='white', width=15, height=2,
                                    command=self.capture_exit_images)
        capture_both_btn.pack(pady=3)
        
        test_cameras_btn = tk.Button(camera_controls_frame, text="Test Cameras", font=camera_btn_font,
                                    bg='#16a085', fg='white', width=15, height=2,
                                    command=self.test_all_cameras)
        test_cameras_btn.pack(pady=3)
        
        # Control Buttons - larger for fullscreen
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.pack(pady=30)
        
        button_font = tkFont.Font(family="Arial", size=14, weight="bold")
        
        open_btn = tk.Button(button_frame, text="OPEN GATE", font=button_font,
                            bg='#27ae60', fg='white', width=12, height=3,
                            command=self.manual_open_gate)
        open_btn.grid(row=0, column=0, padx=15)
        
        close_btn = tk.Button(button_frame, text="CLOSE GATE", font=button_font,
                             bg='#e74c3c', fg='white', width=12, height=3,
                             command=self.manual_close_gate)
        close_btn.grid(row=0, column=1, padx=15)
        
        test_btn = tk.Button(button_frame, text="TEST SCAN", font=button_font,
                            bg='#3498db', fg='white', width=12, height=3,
                            command=self.test_barcode_scan)
        test_btn.grid(row=0, column=2, padx=15)
        
        # Debug Toggle Button
        self.debug_btn = tk.Button(button_frame, text="DEBUG: ON" if self.debug_mode else "DEBUG: OFF", 
                                  font=button_font,
                                  bg='#f39c12' if self.debug_mode else '#95a5a6', 
                                  fg='white', width=12, height=3,
                                  command=self.toggle_debug_mode)
        self.debug_btn.grid(row=0, column=3, padx=15)
        
        # Fullscreen Toggle Button
        fullscreen_btn = tk.Button(button_frame, text="EXIT FULL", font=button_font,
                                  bg='#9b59b6', fg='white', width=12, height=3,
                                  command=self.toggle_fullscreen)
        fullscreen_btn.grid(row=0, column=4, padx=15)
        
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
        
        # Status bar with keyboard shortcuts info
        status_text = "Ready - [ESC/F11: Toggle Fullscreen] [Enter: Process Barcode]"
        self.status_bar = tk.Label(self.root, text=status_text, 
                                  relief=tk.SUNKEN, anchor=tk.W,
                                  bg='#34495e', fg='white')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.log("GUI Setup completed")
    
    def initialize_services(self):
        """Initialize gate services"""
        try:
            self.log("Initializing services...")
            
            # Import services with fallback handling
            try:
                from gate_service import gate_service
                self.gate_service = gate_service
                self.log("Gate service imported successfully")
            except Exception as gate_error:
                self.log("WARNING: Gate service import failed: {}".format(str(gate_error)))
                self.gate_service = None
            
            try:
                from usb_barcode_scanner import usb_barcode_scanner
                self.scanner = usb_barcode_scanner
                self.log("USB barcode scanner imported successfully")
            except Exception as scanner_error:
                self.log("WARNING: USB scanner import failed: {}".format(str(scanner_error)))
                self.scanner = None
            
            try:
                from database_service import db_service
                self.db_service = db_service
                self.log("Database service imported successfully")
            except Exception as db_error:
                self.log("WARNING: Database service import failed: {}".format(str(db_error)))
                self.db_service = None
            
            try:
                from audio_service import audio_service
                self.audio_service = audio_service
                self.log("Audio service imported successfully")
                
                # Test audio service and create sounds directory if needed
                if self.audio_service.is_enabled():
                    self.log("Audio service is enabled")
                    self.audio_service.test_audio()
                else:
                    self.log("Audio service is disabled or not available")
            except Exception as audio_error:
                self.log("WARNING: Audio service import failed: {}".format(str(audio_error)))
                self.audio_service = None
            
            try:
                from camera_service import camera_service
                self.camera_service = camera_service
                self.log("Camera service imported successfully")
                
                # Test camera service
                if self.camera_service:
                    self.log("Testing camera connectivity...")
                    camera_results = self.camera_service.test_all_cameras()
                    for camera_name, success in camera_results.items():
                        status = "OK" if success else "FAILED"
                        self.log("Camera '{}': {}".format(camera_name, status))
                    
                    # Update camera status in GUI
                    self.root.after(0, self.update_camera_status)
                else:
                    self.log("Camera service is not available")
            except Exception as camera_error:
                self.log("WARNING: Camera service import failed: {}".format(str(camera_error)))
                self.camera_service = None
            
            # Add barcode listener if available
            if self.scanner:
                try:
                    self.log("Adding barcode listener...")
                    self.scanner.add_listener(self.on_barcode_scan)
                    self.log("Barcode listener added. Total listeners: {}".format(len(self.scanner.listeners)))
                except Exception as listener_error:
                    self.log("ERROR: Failed to add barcode listener: {}".format(str(listener_error)))
            else:
                self.log("Scanner not available - manual input only")
            
            # Add gate status listener if available
            if self.gate_service:
                try:
                    self.log("Adding gate status listener...")
                    self.gate_service.add_status_listener(self.on_gate_status_change)
                    self.log("Gate status listener added")
                except Exception as status_error:
                    self.log("ERROR: Failed to add gate status listener: {}".format(str(status_error)))
            else:
                self.log("Gate service not available - manual control only")
            
            # Update status based on available services
            services_status = []
            if self.gate_service:
                services_status.append("Gate")
            if self.scanner:
                services_status.append("Scanner")
            if self.db_service:
                services_status.append("Database")
            if self.audio_service and self.audio_service.is_enabled():
                services_status.append("Audio")
            if self.camera_service:
                services_status.append("Camera")
            
            if services_status:
                status_msg = "Ready - Services: {}".format(", ".join(services_status))
            else:
                status_msg = "Ready - Manual mode (no services available)"
            
            self.log("Services initialization completed")
            self.update_status_bar(status_msg)
            self.log("System ready - waiting for barcode input...")
            
        except Exception as e:
            error_msg = "Failed to initialize services: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            self.update_status_bar("ERROR: " + error_msg)
            logger.error(error_msg)
            
            # Print full traceback for debugging
            import traceback
            self.log("Full error traceback:")
            for line in traceback.format_exc().splitlines():
                self.log(line)
    
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
                    
                    # Keep focus on barcode entry field (every 5 seconds)
                    if hasattr(self, 'barcode_entry'):
                        self.root.after(0, self.ensure_entry_focus)
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    self.log("Auto-listener error: {}".format(str(e)))
                    time.sleep(5)  # Wait 5 seconds before retry
        
        # Start in background thread
        listener_thread = threading.Thread(target=auto_listen)
        listener_thread.daemon = True
        listener_thread.start()
    
    def ensure_entry_focus(self):
        """Ensure barcode entry field has focus"""
        try:
            if hasattr(self, 'barcode_entry') and self.barcode_entry:
                if self.root.focus_get() != self.barcode_entry:
                    self.barcode_entry.focus_set()
        except Exception as e:
            pass  # Ignore focus errors
    
    def on_barcode_scan(self, result):
        """Handle barcode scan events"""
        try:
            barcode = result.code
            is_valid = result.is_valid
            
            self.log("BARCODE SCANNED: {} (valid: {})".format(barcode, is_valid))
            
            # Play scan sound
            if self.audio_service:
                self.audio_service.play_scan_sound()
            
            # Update UI
            self.root.after(0, self.update_barcode_display, barcode)
            
            if is_valid:
                # Process the barcode
                self.root.after(0, self.process_vehicle_exit, barcode)
            else:
                self.log("Invalid barcode - ignoring")
                # Play error sound for invalid barcode
                if self.audio_service:
                    self.audio_service.play_error_sound()
                
        except Exception as e:
            error_msg = "Barcode scan error: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            logger.error(error_msg)
    
    def process_vehicle_exit(self, barcode):
        """Process vehicle exit"""
        try:
            self.log("=== PROCESSING VEHICLE EXIT ===")
            self.log("Barcode: {}".format(barcode))
            self.log("Debug mode: {}".format("ENABLED" if self.debug_mode else "DISABLED"))
            
            # Automatically capture exit images
            if self.camera_service:
                self.log("Capturing exit images...")
                self.root.after(0, self.capture_exit_images_async, barcode)
            
            gate_opened = False
            
            # Check database for transaction
            transaction_found = False
            if self.db_service:
                try:
                    result = self.db_service.process_vehicle_exit(barcode, "SYSTEM", "EXIT_GATE_01")
                    if result.get('success'):
                        self.log("✅ Valid transaction found in database")
                        transaction_found = True
                    else:
                        self.log("❌ No transaction found in database")
                        transaction_found = False
                except Exception as db_error:
                    self.log("Database error: {}".format(str(db_error)))
                    transaction_found = False
            else:
                self.log("No database service available")
                transaction_found = False
            
            # Decision logic based on debug mode
            if transaction_found:
                # Always open gate for valid transactions
                self.log("Opening gate - Valid transaction")
                gate_opened = True
            elif self.debug_mode:
                # Debug mode: open gate even without valid transaction
                self.log("DEBUG MODE: Opening gate despite no transaction found")
                gate_opened = True
            else:
                # Normal mode: deny access for unknown barcode
                self.log("ACCESS DENIED: No transaction found and debug mode disabled")
                gate_opened = False
            
            # Open gate if decision was made to open
            if gate_opened:
                if self.gate_service:
                    self.log("Gate service available - triggering open")
                    gate_result = self.gate_service.open_gate()  # No auto close - gate will handle it
                    
                    if gate_result:
                        self.transaction_count += 1
                        self.update_transaction_count()
                        self.log("✅ GATE OPENED SUCCESSFULLY by barcode scan!")
                        
                        # Play gate open sound
                        if self.audio_service:
                            self.audio_service.play_gate_open_sound()
                        
                        # Auto close gate after 1 second
                        self.root.after(1000, self.auto_close_gate)
                    else:
                        self.log("❌ FAILED to open gate")
                        # Play error sound for gate failure
                        if self.audio_service:
                            self.audio_service.play_error_sound()
                else:
                    # Simulate gate operation when service not available
                    self.log("SIMULATION: Gate opened by barcode scan (no gate service)")
                    self.transaction_count += 1
                    self.update_transaction_count()
                    self.gate_status = "OPEN"
                    self.update_gate_status()
                    self.log("✅ GATE OPENED SUCCESSFULLY (simulated)")
                    
                    # Play gate open sound for simulation
                    if self.audio_service:
                        self.audio_service.play_gate_open_sound()
                    
                    # Auto close gate after 1 second (simulation)
                    self.root.after(1000, self.auto_close_gate_simulation)
            elif not gate_opened:
                self.log("Gate NOT opened - access denied")
                # Play error sound for access denied
                if self.audio_service:
                    self.audio_service.play_error_sound()
            else:
                self.log("❌ ERROR: Unexpected condition")
                
        except Exception as e:
            error_msg = "Exit processing error: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            logger.error(error_msg)
            
            # In debug mode, open gate even on error
            if self.debug_mode:
                if self.gate_service:
                    self.log("DEBUG MODE: Opening gate despite processing error")
                    gate_result = self.gate_service.open_gate()  # No auto close
                    if gate_result:
                        # Play gate open sound in debug mode
                        if self.audio_service:
                            self.audio_service.play_gate_open_sound()
                        # Auto close gate after 1 second in debug mode too
                        self.root.after(1000, self.auto_close_gate)
                else:
                    self.log("DEBUG MODE: Simulating gate open despite processing error")
                    self.gate_status = "OPEN"
                    self.update_gate_status()
                    self.transaction_count += 1
                    self.update_transaction_count()
                    # Play gate open sound for debug simulation
                    if self.audio_service:
                        self.audio_service.play_gate_open_sound()
                    # Auto close gate after 1 second (simulation)
                    self.root.after(1000, self.auto_close_gate_simulation)
    
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
    
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen mode"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        
        if not self.is_fullscreen:
            # If exiting fullscreen, set a reasonable window size
            self.root.geometry("800x600")
        
        self.log("Fullscreen mode: {}".format("ON" if self.is_fullscreen else "OFF"))
    
    def toggle_debug_mode(self):
        """Toggle debug mode on/off"""
        self.debug_mode = not self.debug_mode
        
        # Update button appearance
        if self.debug_mode:
            self.debug_btn.config(text="DEBUG: ON", bg='#f39c12')
        else:
            self.debug_btn.config(text="DEBUG: OFF", bg='#95a5a6')
        
        # Log the change
        debug_status = "ENABLED" if self.debug_mode else "DISABLED"
        self.log("DEBUG MODE: {}".format(debug_status))
        print("Debug mode {}".format("enabled" if self.debug_mode else "disabled"))
    
    def manual_open_gate(self):
        """Manual gate open"""
        try:
            if self.gate_service:
                result = self.gate_service.open_gate()
                self.log("Manual gate open: {}".format("Success" if result else "Failed"))
                if result:
                    self.transaction_count += 1
                    self.update_transaction_count()
                    # Play gate open sound for manual operation
                    if self.audio_service:
                        self.audio_service.play_gate_open_sound()
                else:
                    # Play error sound for failed manual operation
                    if self.audio_service:
                        self.audio_service.play_error_sound()
            else:
                self.log("SIMULATION: Gate opened manually (no gate service)")
                # Simulate gate operation for testing
                self.transaction_count += 1
                self.update_transaction_count()
                self.gate_status = "OPEN"
                self.update_gate_status()
                # Play gate open sound for manual simulation
                if self.audio_service:
                    self.audio_service.play_gate_open_sound()
        except Exception as e:
            self.log("ERROR: Manual open failed: {}".format(str(e)))
            # Play error sound for exception
            if self.audio_service:
                self.audio_service.play_error_sound()
    
    def manual_close_gate(self):
        """Manual gate close"""
        try:
            if self.gate_service:
                result = self.gate_service.close_gate()
                self.log("Manual gate close: {}".format("Success" if result else "Failed"))
                if result:
                    # Play gate close sound for successful manual close
                    if self.audio_service:
                        self.audio_service.play_gate_close_sound()
                else:
                    # Play error sound for failed manual close
                    if self.audio_service:
                        self.audio_service.play_error_sound()
            else:
                self.log("SIMULATION: Gate closed manually (no gate service)")
                # Simulate gate operation for testing
                self.gate_status = "CLOSED"
                self.update_gate_status()
                # Play gate close sound for manual simulation
                if self.audio_service:
                    self.audio_service.play_gate_close_sound()
        except Exception as e:
            self.log("ERROR: Manual close failed: {}".format(str(e)))
            # Play error sound for exception
            if self.audio_service:
                self.audio_service.play_error_sound()
    
    def test_barcode_scan(self):
        """Test barcode scan"""
        try:
            test_barcode = "TEST{}".format(int(time.time()) % 10000)
            self.log("=== TESTING BARCODE SCAN ===")
            self.log("Test barcode: {}".format(test_barcode))
            
            # Test both methods: scanner simulation and direct input processing
            if self.scanner:
                self.log("Method 1: Scanner simulation")
                self.scanner.simulate_scan(test_barcode)
            
            # Also test direct input processing
            self.log("Method 2: Direct input processing")
            self.process_barcode_input(test_barcode)
                
        except Exception as e:
            self.log("ERROR: Test scan failed: {}".format(str(e)))
    
    def on_barcode_entry(self, event):
        """Handle barcode entry from text field"""
        try:
            barcode = self.barcode_entry.get().strip().upper()
            if barcode:
                self.log("Manual barcode entry: {}".format(barcode))
                
                # Clear the entry field
                self.barcode_entry.delete(0, tk.END)
                
                # Process the barcode directly
                self.process_barcode_input(barcode)
                
                # Keep focus on entry field
                self.barcode_entry.focus_set()
                
        except Exception as e:
            self.log("ERROR: Barcode entry failed: {}".format(str(e)))
    
    def on_key_release(self, event):
        """Handle key release for auto-processing rapid input (barcode scanner)"""
        try:
            # Check if input looks like rapid barcode scanner input
            current_text = self.barcode_entry.get().strip()
            
            # If Enter was pressed, it's handled by on_barcode_entry
            if event.keysym == 'Return':
                return
            
            # Auto-process if text is long enough and looks like barcode
            if len(current_text) >= 8:  # Typical barcode length
                # Schedule auto-processing after short delay
                self.root.after(100, self.auto_process_barcode)
                
        except Exception as e:
            self.log("ERROR: Key release handler failed: {}".format(str(e)))
    
    def auto_process_barcode(self):
        """Auto-process barcode if entry field has content"""
        try:
            barcode = self.barcode_entry.get().strip().upper()
            if len(barcode) >= 8:  # Process if long enough
                self.log("Auto-processing barcode: {}".format(barcode))
                
                # Clear the entry field
                self.barcode_entry.delete(0, tk.END)
                
                # Process the barcode
                self.process_barcode_input(barcode)
                
                # Keep focus on entry field
                self.barcode_entry.focus_set()
                
        except Exception as e:
            self.log("ERROR: Auto-process failed: {}".format(str(e)))
    
    def process_barcode_input(self, barcode):
        """Process barcode input from text field"""
        try:
            self.log("=== BARCODE INPUT RECEIVED ===")
            self.log("Raw barcode: '{}'".format(barcode))
            self.log("Barcode length: {}".format(len(barcode)))
            
            # Play scan sound for manual input
            if self.audio_service:
                self.audio_service.play_scan_sound()
            
            # Update barcode display
            self.update_barcode_display(barcode)
            
            # Validate barcode length
            if len(barcode) >= 6:  # Minimum length
                self.log("Barcode valid - calling process_vehicle_exit")
                # Process vehicle exit directly
                self.process_vehicle_exit(barcode)
            else:
                self.log("❌ Barcode too short: {} (minimum 6 characters)".format(len(barcode)))
                # Play error sound for invalid length
                if self.audio_service:
                    self.audio_service.play_error_sound()
                
        except Exception as e:
            error_msg = "Barcode input processing error: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            logger.error(error_msg)
            # Play error sound for processing error
            if self.audio_service:
                self.audio_service.play_error_sound()
    
    def auto_close_gate(self):
        """Auto close gate after delay (with gate service)"""
        try:
            if self.gate_service:
                result = self.gate_service.close_gate()
                self.log("Auto-close gate: {}".format("Success" if result else "Failed"))
                if result:
                    # Play gate close sound for successful auto-close
                    if self.audio_service:
                        self.audio_service.play_gate_close_sound()
            else:
                self.log("ERROR: Gate service not available for auto-close")
        except Exception as e:
            self.log("ERROR: Auto-close failed: {}".format(str(e)))
    
    def auto_close_gate_simulation(self):
        """Auto close gate after delay (simulation mode)"""
        try:
            self.gate_status = "CLOSED"
            self.update_gate_status()
            self.log("Auto-close gate: Success (simulated)")
            # Play gate close sound for simulation auto-close
            if self.audio_service:
                self.audio_service.play_gate_close_sound()
        except Exception as e:
            self.log("ERROR: Auto-close simulation failed: {}".format(str(e)))
    
    def update_camera_status(self):
        """Update camera status display"""
        try:
            if self.camera_service:
                camera_status = self.camera_service.get_cameras_status()
                status_texts = []
                
                for camera_name, status in camera_status.items():
                    if status['enabled']:
                        status_texts.append("{}:ON".format(camera_name.upper()))
                    else:
                        status_texts.append("{}:OFF".format(camera_name.upper()))
                
                if status_texts:
                    status_text = "Camera: {}".format(" | ".join(status_texts))
                    self.camera_status_label.config(text=status_text, fg='#27ae60')
                else:
                    self.camera_status_label.config(text="Camera: No cameras", fg='#e74c3c')
            else:
                self.camera_status_label.config(text="Camera: Service unavailable", fg='#e74c3c')
        except Exception as e:
            self.log("ERROR: Camera status update failed: {}".format(str(e)))
            if self.camera_status_label:
                self.camera_status_label.config(text="Camera: Error", fg='#e74c3c')
    
    def capture_camera_image(self, camera_name):
        """Capture image from specific camera"""
        try:
            if not self.camera_service:
                self.log("Camera service not available")
                return
            
            self.log("Capturing image from {} camera...".format(camera_name))
            
            # Capture image
            result = self.camera_service.capture_image(camera_name)
            
            if result.success:
                self.log("✅ {} camera capture successful".format(camera_name.upper()))
                
                # Update preview if we have image data
                if result.image_data:
                    self.root.after(0, self.update_camera_preview, result.image_data)
                
                # Play scan sound for successful capture
                if self.audio_service:
                    self.audio_service.play_scan_sound()
                    
            else:
                self.log("❌ {} camera capture failed: {}".format(camera_name.upper(), result.error_message))
                
                # Play error sound for failed capture
                if self.audio_service:
                    self.audio_service.play_error_sound()
                    
        except Exception as e:
            error_msg = "Camera capture error: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            if self.audio_service:
                self.audio_service.play_error_sound()
    
    def capture_exit_images(self):
        """Capture images from both cameras for exit processing"""
        try:
            if not self.camera_service:
                self.log("Camera service not available")
                return
            
            self.log("Capturing exit images from all cameras...")
            
            # Capture from both cameras
            result = self.camera_service.capture_exit_images()
            
            if result.success:
                self.log("✅ Exit images capture successful")
                
                # Update preview with captured image
                if result.image_data:
                    self.root.after(0, self.update_camera_preview, result.image_data)
                
                # Play scan sound for successful capture
                if self.audio_service:
                    self.audio_service.play_scan_sound()
                    
            else:
                self.log("❌ Exit images capture failed: {}".format(result.error_message))
                
                # Play error sound for failed capture
                if self.audio_service:
                    self.audio_service.play_error_sound()
                    
        except Exception as e:
            error_msg = "Exit images capture error: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            if self.audio_service:
                self.audio_service.play_error_sound()
    
    def capture_exit_images_async(self, barcode):
        """Capture exit images asynchronously with barcode context"""
        try:
            if not self.camera_service:
                return
            
            self.log("Auto-capturing exit images for barcode: {}".format(barcode))
            
            # Capture from both cameras
            result = self.camera_service.capture_exit_images()
            
            if result.success:
                self.log("✅ Auto-capture successful for barcode: {}".format(barcode))
                
                # Update preview with captured image
                if result.image_data:
                    self.root.after(0, self.update_camera_preview, result.image_data)
                
                # TODO: Save image with barcode reference for audit trail
                # This could be enhanced to save images to disk with timestamp and barcode
                    
            else:
                self.log("❌ Auto-capture failed for barcode {}: {}".format(barcode, result.error_message))
                
        except Exception as e:
            self.log("ERROR: Auto-capture failed for barcode {}: {}".format(barcode, str(e)))
    
    def test_all_cameras(self):
        """Test all cameras connectivity"""
        try:
            if not self.camera_service:
                self.log("Camera service not available")
                return
            
            self.log("=== TESTING ALL CAMERAS ===")
            
            # Test all cameras
            results = self.camera_service.test_all_cameras()
            
            success_count = 0
            for camera_name, success in results.items():
                if success:
                    self.log("✅ Camera '{}': OK".format(camera_name.upper()))
                    success_count += 1
                else:
                    self.log("❌ Camera '{}': FAILED".format(camera_name.upper()))
            
            # Update camera status display
            self.root.after(0, self.update_camera_status)
            
            # Play appropriate sound
            if success_count > 0:
                self.log("Camera test completed - {}/{} cameras working".format(success_count, len(results)))
                if self.audio_service:
                    self.audio_service.play_scan_sound()
            else:
                self.log("Camera test completed - No cameras working")
                if self.audio_service:
                    self.audio_service.play_error_sound()
                    
        except Exception as e:
            error_msg = "Camera test error: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            if self.audio_service:
                self.audio_service.play_error_sound()
    
    def update_camera_preview(self, image_data):
        """Update camera preview with base64 image data"""
        try:
            if not image_data or not self.camera_preview_label:
                return
            
            # Try to use PIL for image preview
            try:
                # Decode base64 image
                import base64
                import io
                from PIL import Image, ImageTk
                
                # Decode and resize image for preview
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Resize image to fit preview area (maintain aspect ratio)
                preview_width = 320
                preview_height = 240
                image.thumbnail((preview_width, preview_height), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)
                
                # Convert to PhotoImage for Tkinter
                photo = ImageTk.PhotoImage(image)
                
                # Update preview label
                self.camera_preview_label.config(image=photo, text="")
                self.camera_preview_label.image = photo  # Keep a reference
                
                self.log("Camera preview updated")
                
            except ImportError:
                # PIL not available - show text preview
                self.camera_preview_label.config(text="Camera Preview\n(Image captured)\n\nPIL/Pillow not available\nfor image display", 
                                                bg='#27ae60', fg='white')
                self.log("Camera image captured (PIL not available for preview)")
                
        except Exception as e:
            self.log("ERROR: Camera preview update failed: {}".format(str(e)))
            if self.camera_preview_label:
                self.camera_preview_label.config(text="Camera Preview\n(Update Error)", bg='#e74c3c', fg='white')

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
            
            if self.audio_service:
                self.audio_service.cleanup()
            
            if self.camera_service:
                # Camera service doesn't need explicit cleanup, but log it
                self.log("Camera service shutdown")
            
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
