#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main Flask Web Application for Exit Gate System
Compatible with Python 2.7 and 3.x
"""

from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import json
import time
import threading
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.serving import run_simple

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

# Create Flask app
app = Flask(__name__)
app.secret_key = config.get('flask', 'secret_key', 'exit-gate-secret-key')

# Global state
app_state = {
    'current_transaction': None,
    'gate_status': 'CLOSED',
    'last_scan': None,
    'processing': False,
    'stats': {
        'total_exits': 0,
        'total_revenue': 0
    }
}

# Initialize services
def initialize_services():
    """Initialize all services"""
    logger.info("Initializing Exit Gate System v{}".format(EXIT_GATE_VERSION))
    
    # Initialize barcode scanner
    usb_barcode_scanner.add_listener(handle_barcode_scan)
    
    # Initialize gate status listener
    gate_service.add_status_listener(handle_gate_status_change)
    
    # Load initial stats
    update_stats()
    
    logger.info("All services initialized successfully")

def handle_barcode_scan(barcode_result):
    """Handle barcode scan events"""
    global app_state
    
    logger.info("Barcode scanned: {} (valid: {})".format(
        barcode_result.code, barcode_result.is_valid))
    
    app_state['last_scan'] = barcode_result.to_dict()
    
    if barcode_result.is_valid:
        # Process the barcode immediately - this will trigger GPIO
        logger.info("Processing barcode scan - this should trigger GPIO")
        threading.Thread(target=process_barcode, args=(barcode_result.code,)).start()
    else:
        # Play error sound for invalid barcode
        audio_service.play_error_sound()

def handle_gate_status_change(status):
    """Handle gate status changes"""
    global app_state
    
    app_state['gate_status'] = status
    logger.info("Gate status changed to: {}".format(status))
    
    # Play appropriate sound
    if status == 'OPEN':
        audio_service.play_gate_open_sound()
    elif status == 'CLOSED':
        audio_service.play_gate_close_sound()

def process_barcode(barcode):
    """Process barcode and handle exit"""
    global app_state
    
    if app_state['processing']:
        logger.warning("Already processing a transaction")
        return
    
    app_state['processing'] = True
    
    try:
        logger.info("=== BARCODE PROCESSING STARTED ===")
        logger.info("Barcode: {}".format(barcode))
        
        # Play scan sound
        audio_service.play_scan_sound()
        
        # Process vehicle exit
        result = db_service.process_vehicle_exit(
            barcode,
            config.get('system', 'operator_id', 'SYSTEM'),
            config.get('system', 'gate_id', 'EXIT_GATE_01')
        )
        
        if result['success']:
            # Update current transaction
            app_state['current_transaction'] = result
            
            # Log performance metrics
            search_time = result.get('search_time_ms', 0)
            total_time = result.get('total_processing_time_ms', 0)
            search_method = result.get('search_method', 'unknown')
            transaction_type = result.get('transaction_type', 'unknown')
            
            logger.info("=== EXIT PERFORMANCE METRICS ===")
            logger.info("Search method: {}".format(search_method))
            logger.info("Transaction type: {}".format(transaction_type))
            logger.info("Search time: {:.2f}ms".format(search_time))
            logger.info("Total processing time: {:.2f}ms".format(total_time))
            
            # Capture exit images
            capture_exit_images(result['transaction']['_id'])
            
            # Open gate - THIS SHOULD TRIGGER GPIO
            logger.info("=== OPENING GATE - GPIO SHOULD TRIGGER NOW ===")
            gate_opened = gate_service.open_gate(config.getint('system', 'auto_close_timeout', 10))
            logger.info("Gate open result: {}".format(gate_opened))
            
            # Play success sound
            audio_service.play_success_sound()
            
            # Update stats
            update_stats()
            
            logger.info("Exit processed successfully: fee = {}".format(result.get('fee', 0)))
        else:
            # Play error sound
            audio_service.play_error_sound()
            logger.error("Exit processing failed: {}".format(result['message']))
    
    except Exception as e:
        logger.error("Error processing barcode: {}".format(str(e)))
        audio_service.play_error_sound()
    
    finally:
        app_state['processing'] = False

def capture_exit_images(transaction_id):
    """Capture exit images and save to transaction"""
    try:
        if not camera_service:
            return
        
        # Capture images from cameras
        result = camera_service.capture_exit_images()
        
        if result.success and result.image_data:
            # Add image to transaction
            db_service.add_image_to_transaction(
                transaction_id,
                'exit_combined.jpg',
                result.image_data
            )
            logger.info("Exit images captured and saved to transaction")
        else:
            logger.warning("Failed to capture exit images: {}".format(result.error_message))
    
    except Exception as e:
        logger.error("Error capturing exit images: {}".format(str(e)))

def update_stats():
    """Update today's statistics"""
    global app_state
    
    try:
        stats = db_service.get_today_exit_stats()
        app_state['stats'] = stats
        logger.debug("Stats updated: {}".format(stats))
    except Exception as e:
        logger.error("Error updating stats: {}".format(str(e)))

# Web Routes

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', 
                         version=EXIT_GATE_VERSION,
                         state=app_state)

@app.route('/api/status')
def api_status():
    """Get system status"""
    system_info = gate_service.get_system_info()
    camera_status = camera_service.get_cameras_status()
    audio_info = audio_service.get_audio_info()
    scanner_config = usb_barcode_scanner.get_config()
    sync_status = db_service.get_sync_status()
    
    return jsonify({
        'success': True,
        'data': {
            'version': EXIT_GATE_VERSION,
            'app_state': app_state,
            'system': system_info,
            'cameras': camera_status,
            'audio': audio_info,
            'scanner': scanner_config,
            'database': sync_status
        }
    })

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Simulate barcode scan"""
    data = request.get_json()
    barcode = data.get('barcode', '')
    
    if not barcode:
        return jsonify({'success': False, 'message': 'Barcode required'})
    
    # Simulate scan
    usb_barcode_scanner.simulate_scan(barcode)
    
    return jsonify({'success': True, 'message': 'Barcode scan simulated'})

@app.route('/api/gate/open', methods=['POST'])
def api_gate_open():
    """Open gate manually"""
    success = gate_service.open_gate()
    return jsonify({
        'success': success,
        'message': 'Gate opened' if success else 'Failed to open gate'
    })

@app.route('/api/gate/close', methods=['POST'])
def api_gate_close():
    """Close gate manually"""
    success = gate_service.close_gate()
    return jsonify({
        'success': success,
        'message': 'Gate closed' if success else 'Failed to close gate'
    })

@app.route('/api/gate/test', methods=['POST'])
def api_gate_test():
    """Test gate operation"""
    success = gate_service.test_gate()
    return jsonify({
        'success': success,
        'message': 'Gate test completed' if success else 'Gate test failed'
    })

@app.route('/api/camera/capture/<camera_name>')
def api_camera_capture(camera_name):
    """Capture image from camera"""
    result = camera_service.capture_image(camera_name)
    return jsonify({
        'success': result.success,
        'image_data': result.image_data if result.success else None,
        'error': result.error_message if not result.success else None
    })

@app.route('/api/camera/test/<camera_name>')
def api_camera_test(camera_name):
    """Test camera"""
    success = camera_service.test_camera(camera_name)
    return jsonify({
        'success': success,
        'message': 'Camera test passed' if success else 'Camera test failed'
    })

@app.route('/api/audio/play/<sound_name>')
def api_audio_play(sound_name):
    """Play audio sound"""
    success = audio_service.play_sound(sound_name)
    return jsonify({
        'success': success,
        'message': 'Sound played' if success else 'Failed to play sound'
    })

@app.route('/api/audio/test')
def api_audio_test():
    """Test audio system"""
    success = audio_service.test_audio()
    return jsonify({
        'success': success,
        'message': 'Audio test completed' if success else 'Audio test failed'
    })

@app.route('/api/transaction/<transaction_id>')
def api_get_transaction(transaction_id):
    """Get transaction details"""
    try:
        doc = db_service.local_db[transaction_id]
        return jsonify({'success': True, 'data': doc})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/transactions/search')
def api_search_transactions():
    """Search transactions"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'success': False, 'message': 'Query required'})
    
    # Try to find by barcode
    transaction = db_service.find_transaction_by_barcode(query)
    if not transaction:
        # Try to find by plate
        transaction = db_service.find_transaction_by_plate(query)
    
    if transaction:
        return jsonify({'success': True, 'data': transaction})
    else:
        return jsonify({'success': False, 'message': 'Transaction not found'})

@app.route('/api/stats')
def api_stats():
    """Get statistics"""
    update_stats()
    return jsonify({'success': True, 'data': app_state['stats']})

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or update configuration"""
    if request.method == 'GET':
        return jsonify({
            'success': True,
            'data': config.to_dict()
        })
    else:
        # Update configuration
        data = request.get_json()
        try:
            for section, options in data.items():
                for option, value in options.items():
                    config.set(section, option, value)
            
            config.save_config()
            return jsonify({'success': True, 'message': 'Configuration updated'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html',
                         config=config.to_dict(),
                         system_info=gate_service.get_system_info())

@app.route('/logs')
def logs():
    """Logs page"""
    return render_template('logs.html')

# Static files
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('error.html', 
                         error="Page not found",
                         code=404), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('error.html',
                         error="Internal server error",
                         code=500), 500

# Cleanup function
def cleanup():
    """Cleanup all services"""
    logger.info("Shutting down Exit Gate System...")
    
    try:
        usb_barcode_scanner.cleanup()
        gate_service.cleanup()
        audio_service.cleanup()
        logger.info("Cleanup completed successfully")
    except Exception as e:
        logger.error("Error during cleanup: {}".format(str(e)))

if __name__ == '__main__':
    try:
        # Initialize services
        initialize_services()
        
        # Start Flask application
        host = config.get('flask', 'host', '0.0.0.0')
        port = config.getint('flask', 'port', 5001)
        debug = config.getboolean('flask', 'debug', False)
        
        logger.info("Starting Exit Gate System web server on {}:{}".format(host, port))
        
        # Use run_simple for better Python 2.7 compatibility
        run_simple(host, port, app, 
                  use_reloader=debug,
                  use_debugger=debug,
                  threaded=True)
    
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error("Application error: {}".format(str(e)))
    finally:
        cleanup()
