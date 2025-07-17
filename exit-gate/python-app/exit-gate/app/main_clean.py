#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exit Gate System - Core Processing (No Web Interface)
Compatible with Python 2.7 and 3.x
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import time
import threading
from datetime import datetime
import signal
import sys

# Import our services
from config import config, EXIT_GATE_VERSION
from database_service import db_service
from gate_service import gate_service
from usb_barcode_scanner import usb_barcode_scanner
from camera_service import camera_service
from audio_service import audio_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Global state
app_state = {
    'current_transaction': None,
    'gate_status': 'CLOSED',
    'last_scan': None,
    'processing': False,
    'running': True,
    'stats': {
        'total_exits': 0,
        'total_revenue': 0
    }
}

def process_barcode(barcode_value):
    """Process a scanned barcode"""
    start_time = time.time()
    
    if app_state['processing']:
        logger.warning("Another scan is already being processed")
        return {'success': False, 'message': 'Already processing another scan'}
    
    app_state['processing'] = True
    
    try:
        logger.info("Processing barcode: {}".format(barcode_value))
        
        # Find transaction in database
        transaction = db_service.find_transaction_by_barcode(barcode_value)
        
        if not transaction:
            logger.warning("Transaction not found for barcode: {}".format(barcode_value))
            audio_service.play_error_sound()
            return {'success': False, 'message': 'Transaction not found'}
        
        logger.info("Found transaction: {}".format(transaction.get('_id', 'N/A')))
        
        # Determine if this is a member card (starts with 'M')
        is_member_card = barcode_value.startswith('M')
        
        # Process exit based on type
        if is_member_card:
            # Use optimized member processing
            result = db_service.process_member_exit_optimized(transaction)
        else:
            # Use regular barcode processing
            result = db_service.process_exit(transaction)
        
        processing_time = (time.time() - start_time) * 1000  # ms
        
        if result.get('success'):
            # Open gate
            gate_service.open_gate()
            
            # Update state
            app_state['current_transaction'] = transaction
            app_state['gate_status'] = 'OPEN'
            app_state['last_scan'] = {
                'barcode': barcode_value,
                'time': datetime.now(),
                'type': 'member' if is_member_card else 'barcode'
            }
            app_state['stats']['total_exits'] += 1
            
            # Play success sound
            audio_service.play_success_sound()
            
            # Log performance metrics
            process_type = "MEMBER" if is_member_card else "BARCODE"
            
            logger.info("=== EXIT PERFORMANCE METRICS ===")
            logger.info("Process Type: {}".format(process_type))
            logger.info("Total Processing Time: {:.2f}ms".format(processing_time))
            logger.info("Barcode: {}".format(barcode_value))
            logger.info("Transaction ID: {}".format(transaction.get('_id', 'N/A')))
            logger.info("================================")
            
            logger.info("Exit processed successfully in {:.2f}ms".format(processing_time))
            
            return {
                'success': True, 
                'message': 'Exit processed successfully',
                'transaction_id': transaction.get('_id'),
                'processing_time_ms': processing_time,
                'type': 'member' if is_member_card else 'barcode'
            }
        else:
            # Play error sound
            audio_service.play_error_sound()
            logger.error("Exit processing failed: {}".format(result.get('message', 'Unknown error')))
            return {
                'success': False, 
                'message': result.get('message', 'Exit processing failed'),
                'processing_time_ms': processing_time
            }
            
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000  # ms
        logger.error("Error processing barcode: {}".format(str(e)))
        audio_service.play_error_sound()
        return {
            'success': False, 
            'message': 'Error processing barcode: {}'.format(str(e)),
            'processing_time_ms': processing_time
        }
    finally:
        app_state['processing'] = False

def on_barcode_scan(barcode):
    """Callback function when barcode is scanned"""
    logger.info("Barcode scanned: {}".format(barcode))
    
    # Process the barcode in a separate thread to avoid blocking
    def process_in_thread():
        result = process_barcode(barcode)
        if result['success']:
            logger.info("Barcode processing completed successfully")
        else:
            logger.error("Barcode processing failed: {}".format(result['message']))
    
    # Start processing thread
    thread = threading.Thread(target=process_in_thread)
    thread.daemon = True
    thread.start()

def initialize_services():
    """Initialize all system services"""
    logger.info("Initializing Exit Gate System v{}".format(EXIT_GATE_VERSION))
    
    try:
        # Initialize database service
        logger.info("Initializing database service...")
        db_service.initialize()
        
        # Initialize gate service
        logger.info("Initializing gate service...")
        gate_service.initialize()
        
        # Initialize camera service
        logger.info("Initializing camera service...")
        camera_service.initialize()
        
        # Initialize audio service
        logger.info("Initializing audio service...")
        audio_service.initialize()
        
        # Initialize barcode scanner with callback
        logger.info("Initializing USB barcode scanner...")
        usb_barcode_scanner.initialize(on_barcode_scan)
        
        logger.info("All services initialized successfully")
        return True
        
    except Exception as e:
        logger.error("Failed to initialize services: {}".format(str(e)))
        return False

def cleanup_services():
    """Clean up all services"""
    logger.info("Shutting down services...")
    
    try:
        usb_barcode_scanner.cleanup()
        gate_service.cleanup()
        audio_service.cleanup()
        camera_service.cleanup()
        db_service.cleanup()
        logger.info("Cleanup completed successfully")
    except Exception as e:
        logger.error("Error during cleanup: {}".format(str(e)))

def signal_handler(signum, frame):
    """Handle shutdown signal"""
    logger.info("Received shutdown signal {}".format(signum))
    app_state['running'] = False

def main_loop():
    """Main application loop"""
    logger.info("Exit Gate System is running...")
    logger.info("Waiting for barcode scans...")
    
    # Print status every 30 seconds
    last_status_time = time.time()
    
    try:
        while app_state['running']:
            current_time = time.time()
            
            # Print periodic status
            if current_time - last_status_time >= 30:
                logger.info("System Status - Gate: {}, Total Exits: {}, Processing: {}".format(
                    app_state['gate_status'],
                    app_state['stats']['total_exits'],
                    app_state['processing']
                ))
                last_status_time = current_time
            
            # Sleep briefly to avoid high CPU usage
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        app_state['running'] = False

if __name__ == '__main__':
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize services
        if not initialize_services():
            logger.error("Failed to initialize services, exiting...")
            sys.exit(1)
        
        # Run main loop
        main_loop()
        
    except Exception as e:
        logger.error("Application error: {}".format(str(e)))
    finally:
        # Cleanup
        cleanup_services()
        logger.info("Exit Gate System shutdown complete")
