#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Exit Gate Flask Server
GPIO + Barcode Integration
"""

from flask import Flask, request, jsonify
import RPi.GPIO as GPIO
import time
import threading
import json

app = Flask(__name__)

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(24, GPIO.OUT)
GPIO.output(24, GPIO.LOW)  # Start closed

class GateController:
    def __init__(self):
        self.gate_open = False
        self.auto_close_timer = None
        
    def open_gate(self):
        """Open gate"""
        print("Opening gate...")
        GPIO.output(24, GPIO.HIGH)  # LED ON
        self.gate_open = True
        
        # Auto-close after 10 seconds
        if self.auto_close_timer:
            self.auto_close_timer.cancel()
        
        self.auto_close_timer = threading.Timer(10.0, self.close_gate)
        self.auto_close_timer.start()
        
        return True
        
    def close_gate(self):
        """Close gate"""
        print("Closing gate...")
        GPIO.output(24, GPIO.LOW)  # LED OFF
        self.gate_open = False
        
        if self.auto_close_timer:
            self.auto_close_timer.cancel()
            self.auto_close_timer = None
            
        return True
    
    def get_status(self):
        """Get status"""
        return {
            "gate_open": self.gate_open,
            "gpio_pin": 24,
            "gpio_value": GPIO.input(24)
        }

# Global gate controller
gate = GateController()

@app.route('/api/status')
def api_status():
    """API status"""
    return jsonify({
        "success": True,
        "message": "Exit Gate System Running",
        "gate": gate.get_status()
    })

@app.route('/api/gate/open', methods=['POST'])
def api_gate_open():
    """Open gate"""
    success = gate.open_gate()
    return jsonify({
        "success": success,
        "message": "Gate opened" if success else "Failed to open gate",
        "gate": gate.get_status()
    })

@app.route('/api/gate/close', methods=['POST'])  
def api_gate_close():
    """Close gate"""
    success = gate.close_gate()
    return jsonify({
        "success": success,
        "message": "Gate closed" if success else "Failed to close gate",
        "gate": gate.get_status()
    })

@app.route('/api/gate/test', methods=['POST'])
def api_gate_test():
    """Test gate"""
    gate.open_gate()
    time.sleep(3)
    gate.close_gate()
    return jsonify({
        "success": True,
        "message": "Gate test completed",
        "gate": gate.get_status()
    })

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Simulate barcode scan"""
    data = request.get_json() or {}
    barcode = data.get('barcode', 'UNKNOWN')
    
    print("Barcode scanned: {}".format(barcode))
    
    # Trigger gate open
    if not gate.gate_open:
        success = gate.open_gate()
        message = "Gate opened for barcode: {}".format(barcode)
    else:
        success = True
        message = "Gate already open"
    
    return jsonify({
        "success": success,
        "message": message,
        "barcode": barcode,
        "gate": gate.get_status()
    })

@app.route('/')
def index():
    """Simple web interface"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Exit Gate Control</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial; margin: 40px; }
            button { padding: 10px 20px; margin: 10px; font-size: 16px; }
            .status { margin: 20px 0; padding: 10px; background: #f0f0f0; }
            input { padding: 8px; margin: 5px; }
        </style>
    </head>
    <body>
        <h1>🚪 Exit Gate Control</h1>
        
        <div class="status" id="status">Loading...</div>
        
        <h3>Gate Control</h3>
        <button onclick="openGate()">Open Gate</button>
        <button onclick="closeGate()">Close Gate</button>
        <button onclick="testGate()">Test Gate</button>
        
        <h3>Barcode Simulation</h3>
        <input type="text" id="barcode" placeholder="Enter barcode" value="TEST123">
        <button onclick="scanBarcode()">Simulate Scan</button>
        
        <script>
            function updateStatus() {
                fetch('/api/status')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('status').innerHTML = 
                            '<strong>Status:</strong> ' + (data.gate.gate_open ? 'OPEN' : 'CLOSED') +
                            '<br><strong>GPIO Pin:</strong> ' + data.gate.gpio_pin +
                            '<br><strong>GPIO Value:</strong> ' + data.gate.gpio_value;
                    });
            }
            
            function openGate() {
                fetch('/api/gate/open', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => {
                        alert(data.message);
                        updateStatus();
                    });
            }
            
            function closeGate() {
                fetch('/api/gate/close', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => {
                        alert(data.message);
                        updateStatus();
                    });
            }
            
            function testGate() {
                fetch('/api/gate/test', {method: 'POST'})
                    .then(r => r.json())
                    .then(data => {
                        alert(data.message);
                        updateStatus();
                    });
            }
            
            function scanBarcode() {
                const barcode = document.getElementById('barcode').value;
                fetch('/api/scan', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({barcode: barcode})
                })
                .then(r => r.json())
                .then(data => {
                    alert(data.message);
                    updateStatus();
                });
            }
            
            // Update status every 2 seconds
            setInterval(updateStatus, 2000);
            updateStatus();
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    try:
        print("Starting Exit Gate Simple Server...")
        print("Web interface: http://localhost:5001")
        print("Press Ctrl+C to stop")
        
        app.run(host='0.0.0.0', port=5001, debug=False)
        
    except KeyboardInterrupt:
        pass
    finally:
        gate.close_gate()
        GPIO.cleanup()
        print("Server stopped. GPIO cleaned up.")
