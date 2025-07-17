#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exit Gate Console Application
Simple console-based exit gate system for barcode input
Compatible dengan Python 2.7 - No GUI required
"""

from __future__ import print_function
import threading
import time
import logging
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='exit_gate_console.log'
)
logger = logging.getLogger(__name__)

class ExitGateConsole(object):
    """Console-based Exit Gate Application"""
    
    def __init__(self):
        self.gate_status = "CLOSED"
        self.transaction_count = 0
        self.running = True
        
        # Services
        self.gate_service = None
        self.scanner = None
        self.db_service = None
        
        self.initialize_services()
        
    def initialize_services(self):
        """Initialize gate services"""
        try:
            print("Initializing services...")
            
            # Import services
            from gate_service import gate_service
            from usb_barcode_scanner import usb_barcode_scanner
            from database_service import db_service
            
            self.gate_service = gate_service
            self.scanner = usb_barcode_scanner
            self.db_service = db_service
            
            print("Services imported successfully")
            
            # Add barcode listener
            if self.scanner:
                print("Adding barcode listener...")
                self.scanner.add_listener(self.on_barcode_scan)
                print("Barcode listener added. Total listeners: {}".format(len(self.scanner.listeners)))
            else:
                print("ERROR: Scanner is None!")
            
            # Add gate status listener
            if self.gate_service:
                print("Adding gate status listener...")
                self.gate_service.add_status_listener(self.on_gate_status_change)
                print("Gate status listener added")
            else:
                print("ERROR: Gate service is None!")
            
            print("Services initialized successfully")
            
        except Exception as e:
            error_msg = "Failed to initialize services: {}".format(str(e))
            print("ERROR: " + error_msg)
            logger.error(error_msg)
            
            # Print full traceback
            import traceback
            print("Full error traceback:")
            for line in traceback.format_exc().splitlines():
                print(line)
    
    def on_barcode_scan(self, result):
        """Handle barcode scan events"""
        try:
            barcode = result.code
            is_valid = result.is_valid
            
            self.log("BARCODE SCANNED: {} (valid: {})".format(barcode, is_valid))
            
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
                            self.log("Gate opened successfully - Transaction count: {}".format(self.transaction_count))
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
                    gate_result = self.gate_service.open_gate(5)
                    if gate_result:
                        self.transaction_count += 1
                        self.log("Gate opened for test - Transaction count: {}".format(self.transaction_count))
                
        except Exception as e:
            error_msg = "Exit processing error: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            logger.error(error_msg)
    
    def on_gate_status_change(self, status):
        """Handle gate status changes"""
        self.gate_status = status
        self.log("Gate status: {}".format(status))
    
    def process_barcode_input(self, barcode):
        """Process barcode input from console"""
        try:
            barcode = barcode.strip().upper()
            if len(barcode) >= 6:  # Minimum length
                self.log("Processing manual barcode: {}".format(barcode))
                self.process_vehicle_exit(barcode)
            else:
                self.log("Barcode too short: {} (minimum 6 characters)".format(len(barcode)))
                
        except Exception as e:
            error_msg = "Barcode input processing error: {}".format(str(e))
            self.log("ERROR: " + error_msg)
            logger.error(error_msg)
    
    def manual_gate_control(self, action):
        """Manual gate control"""
        try:
            if action.lower() == 'open':
                if self.gate_service:
                    result = self.gate_service.open_gate()
                    self.log("Manual gate open: {}".format("Success" if result else "Failed"))
                else:
                    self.log("ERROR: Gate service not available")
            elif action.lower() == 'close':
                if self.gate_service:
                    result = self.gate_service.close_gate()
                    self.log("Manual gate close: {}".format("Success" if result else "Failed"))
                else:
                    self.log("ERROR: Gate service not available")
            else:
                self.log("Invalid gate action: {}".format(action))
                
        except Exception as e:
            self.log("ERROR: Manual gate control failed: {}".format(str(e)))
    
    def log(self, message):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = "[{}] {}".format(timestamp, message)
        print(log_message)
        logger.info(message)
    
    def print_status(self):
        """Print current system status"""
        print("\n" + "="*50)
        print("EXIT GATE SYSTEM STATUS")
        print("="*50)
        print("Gate Status: {}".format(self.gate_status))
        print("Transactions: {}".format(self.transaction_count))
        print("Scanner Listeners: {}".format(len(self.scanner.listeners) if self.scanner else 0))
        print("Time: {}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        print("="*50)
    
    def print_help(self):
        """Print help information"""
        print("\n" + "="*50)
        print("EXIT GATE CONSOLE COMMANDS")
        print("="*50)
        print("Enter barcode: Type any barcode and press Enter")
        print("open         : Manually open gate")
        print("close        : Manually close gate")
        print("status       : Show system status")
        print("test         : Test barcode scan")
        print("help         : Show this help")
        print("quit/exit    : Exit application")
        print("="*50)
    
    def start_console_input(self):
        """Start console input loop"""
        def input_loop():
            while self.running:
                try:
                    user_input = raw_input("Barcode/Command: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle commands
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        self.running = False
                        break
                    elif user_input.lower() == 'help':
                        self.print_help()
                    elif user_input.lower() == 'status':
                        self.print_status()
                    elif user_input.lower() == 'open':
                        self.manual_gate_control('open')
                    elif user_input.lower() == 'close':
                        self.manual_gate_control('close')
                    elif user_input.lower() == 'test':
                        test_barcode = "TEST{}".format(int(time.time()) % 10000)
                        self.log("Testing with barcode: {}".format(test_barcode))
                        if self.scanner:
                            self.scanner.simulate_scan(test_barcode)
                    else:
                        # Treat as barcode
                        self.process_barcode_input(user_input)
                        
                except EOFError:
                    break
                except KeyboardInterrupt:
                    self.running = False
                    break
                except Exception as e:
                    self.log("Input error: {}".format(str(e)))
        
        # Start input thread
        input_thread = threading.Thread(target=input_loop)
        input_thread.daemon = True
        input_thread.start()
        
        return input_thread
    
    def run(self):
        """Run the console application"""
        try:
            self.log("Exit Gate Console Application Started")
            self.print_help()
            self.print_status()
            
            # Start console input
            input_thread = self.start_console_input()
            
            # Main loop
            while self.running:
                time.sleep(1)
            
            self.log("Application shutting down...")
            
            # Cleanup
            if self.scanner:
                self.scanner.cleanup()
            if self.gate_service:
                self.gate_service.cleanup()
                
        except KeyboardInterrupt:
            self.log("Application interrupted by user")
        except Exception as e:
            self.log("Application error: {}".format(str(e)))
            logger.error("Application error: {}".format(str(e)))

def main():
    """Main function"""
    try:
        app = ExitGateConsole()
        app.run()
    except Exception as e:
        print("Application startup error: {}".format(str(e)))
        logger.error("Application startup error: {}".format(str(e)))

if __name__ == "__main__":
    main()
