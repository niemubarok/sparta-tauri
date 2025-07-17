#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exit Gate Console Application
Console version tanpa GUI untuk debugging
"""

from __future__ import print_function
import threading
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExitGateConsole(object):
    """Console version of Exit Gate Application"""
    
    def __init__(self):
        # State variables
        self.gate_status = "CLOSED"
        self.last_barcode = ""
        self.transaction_count = 0
        self.running = True
        
        # Services
        self.gate_service = None
        self.scanner = None
        self.db_service = None
        
        self.initialize_services()
        self.start_auto_listener()
        
        self.log("Exit Gate Console initialized")
    
    def initialize_services(self):
        """Initialize gate services"""
        try:
            self.log("Initializing services...")
            
            # Import services
            from gate_service import gate_service
            from usb_barcode_scanner import usb_barcode_scanner
            from database_service import db_service
            
            self.gate_service = gate_service
            self.scanner = usb_barcode_scanner
            self.db_service = db_service
            
            self.log("Services imported successfully")
            
            # Add barcode listener
            if self.scanner:
                self.log("Adding barcode listener...")
                self.scanner.add_listener(self.on_barcode_scan)
                self.log("Barcode listener added. Total listeners: {}".format(len(self.scanner.listeners)))
            else:
                self.log("ERROR: Scanner is None!")
            
            # Add gate status listener
            if self.gate_service:
                self.log("Adding gate status listener...")
                self.gate_service.add_status_listener(self.on_gate_status_change)
                self.log("Gate status listener added")
            else:
                self.log("ERROR: Gate service is None!")
            
            self.log("Services initialized successfully")
            
            # Test scanner immediately
            if self.scanner:
                self.log("Testing scanner with immediate scan...")
                self.scanner.simulate_scan("CONSOLE_INIT_TEST")
            
        except Exception as e:
            error_msg = "Failed to initialize services: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            logger.error(error_msg)
            
            # Print full traceback
            import traceback
            self.log("Full error traceback:")
            for line in traceback.format_exc().splitlines():
                self.log(line)
    
    def start_auto_listener(self):
        """Start automatic barcode listening in background"""
        def auto_listen():
            self.log("Auto-listener started")
            while self.running:
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
            
            self.log("*** BARCODE SCANNED: {} (valid: {}) ***".format(barcode, is_valid))
            
            self.last_barcode = barcode
            
            if is_valid:
                # Process the barcode
                self.process_vehicle_exit(barcode)
            else:
                self.log("Invalid barcode - ignoring")
                
        except Exception as e:
            error_msg = "Barcode scan error: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            logger.error(error_msg)
    
    def process_vehicle_exit(self, barcode):
        """Process vehicle exit"""
        try:
            self.log("*** PROCESSING VEHICLE EXIT: {} ***".format(barcode))
            
            # Always open gate for testing (skip database for now)
            self.log("Opening gate for barcode: {}".format(barcode))
            if self.gate_service:
                gate_result = self.gate_service.open_gate(5)  # Auto close in 5 seconds
                
                if gate_result:
                    self.transaction_count += 1
                    self.log("*** GATE OPENED SUCCESSFULLY! Transaction #{} ***".format(self.transaction_count))
                else:
                    self.log("ERROR: Failed to open gate")
            else:
                self.log("ERROR: Gate service not available")
                
        except Exception as e:
            error_msg = "Exit processing error: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            logger.error(error_msg)
    
    def on_gate_status_change(self, status):
        """Handle gate status changes"""
        self.gate_status = status
        self.log("*** GATE STATUS: {} ***".format(status))
    
    def manual_open_gate(self):
        """Manual gate open"""
        try:
            self.log("Manual gate open requested")
            if self.gate_service:
                result = self.gate_service.open_gate()
                self.log("Manual gate open: {}".format("Success" if result else "Failed"))
                return result
            else:
                self.log("ERROR: Gate service not available")
                return False
        except Exception as e:
            self.log("ERROR: Manual open failed: {}".format(str(e)))
            return False
    
    def manual_close_gate(self):
        """Manual gate close"""
        try:
            self.log("Manual gate close requested")
            if self.gate_service:
                result = self.gate_service.close_gate()
                self.log("Manual gate close: {}".format("Success" if result else "Failed"))
                return result
            else:
                self.log("ERROR: Gate service not available")
                return False
        except Exception as e:
            self.log("ERROR: Manual close failed: {}".format(str(e)))
            return False
    
    def test_barcode_scan(self, barcode=None):
        """Test barcode scan"""
        try:
            if not barcode:
                barcode = "TEST{}".format(int(time.time()) % 10000)
            
            self.log("*** TESTING BARCODE SCAN: {} ***".format(barcode))
            
            if self.scanner:
                self.scanner.simulate_scan(barcode)
                return True
            else:
                self.log("ERROR: Scanner not available")
                return False
                
        except Exception as e:
            self.log("ERROR: Test scan failed: {}".format(str(e)))
            return False
    
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = "[{}] {}".format(timestamp, message)
        print(log_message)
        logger.info(message)
    
    def run_interactive(self):
        """Run interactive console"""
        self.log("Exit Gate Console started - Interactive mode")
        self.log("Commands: 'open', 'close', 'scan [barcode]', 'status', 'quit'")
        
        while self.running:
            try:
                command = raw_input("\nExit Gate> ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    self.running = False
                    break
                elif command == 'open':
                    self.manual_open_gate()
                elif command == 'close':
                    self.manual_close_gate()
                elif command.startswith('scan'):
                    parts = command.split(' ', 1)
                    barcode = parts[1] if len(parts) > 1 else None
                    self.test_barcode_scan(barcode)
                elif command == 'status':
                    self.log("Status - Gate: {}, Last Barcode: {}, Transactions: {}".format(
                        self.gate_status, self.last_barcode, self.transaction_count))
                    self.log("Scanner listeners: {}".format(len(self.scanner.listeners) if self.scanner else 'No scanner'))
                elif command == 'test':
                    self.test_barcode_scan("INTERACTIVE_TEST")
                else:
                    self.log("Unknown command. Use: open, close, scan [barcode], status, test, quit")
                    
            except KeyboardInterrupt:
                self.running = False
                break
            except EOFError:
                self.running = False
                break
            except Exception as e:
                self.log("Command error: {}".format(str(e)))
        
        self.log("Exit Gate Console stopped")
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            self.running = False
            self.log("Shutting down...")
            
            # Cleanup services
            if self.scanner:
                self.scanner.cleanup()
            
            if self.gate_service:
                self.gate_service.cleanup()
                
        except Exception as e:
            logger.error("Shutdown error: {}".format(str(e)))

def main():
    """Main function"""
    try:
        app = ExitGateConsole()
        
        import sys
        if len(sys.argv) > 1 and sys.argv[1] == 'interactive':
            app.run_interactive()
        else:
            # Run for 30 seconds with automatic testing
            app.log("Running automatic test mode for 30 seconds...")
            
            # Test manual gate operation
            app.manual_open_gate()
            time.sleep(2)
            app.manual_close_gate()
            time.sleep(1)
            
            # Test barcode scanning
            for i in range(3):
                app.test_barcode_scan("AUTO_TEST_{}".format(i+1))
                time.sleep(3)
            
            app.log("Automatic test completed")
            
        app.cleanup()
        
    except Exception as e:
        print("Application error: {}".format(str(e)))
        logger.error("Application error: {}".format(str(e)))

if __name__ == "__main__":
    main()
