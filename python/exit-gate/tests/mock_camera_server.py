#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo Camera Server
Simple HTTP server yang mensimulasikan CCTV IP camera untuk testing
"""

from __future__ import print_function
try:
    # Python 2.7
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from urlparse import urlparse, parse_qs
except ImportError:
    # Python 3.x
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs

import base64
import os
import time
from datetime import datetime

class MockCameraHandler(BaseHTTPRequestHandler):
    """Mock camera HTTP handler"""
    
    def do_GET(self):
        """Handle GET requests for snapshot"""
        try:
            # Parse URL
            parsed_url = urlparse(self.path)
            
            # Check if this is a snapshot request
            snapshot_paths = [
                '/Streaming/Channels/1/picture',  # Generic/default
                '/ISAPI/Streaming/channels/101/picture',  # Hikvision
                '/cgi-bin/snapshot.cgi',  # Dahua
                '/onvif-http/snapshot',  # Glenz
                '/axis-cgi/jpg/image.cgi',  # Axis
                '/onvif/media_service/snapshot',  # Generic ONVIF
                '/Snapshot/1/RemoteImageCapture'  # Custom camera format
            ]
            
            if any(parsed_url.path.startswith(path) for path in snapshot_paths):
                # Generate a simple test image
                self.send_snapshot()
            else:
                # Return 404 for unknown paths
                self.send_error(404, "Path not found: {}".format(self.path))
                
        except Exception as e:
            self.send_error(500, "Server error: {}".format(str(e)))
    
    def send_snapshot(self):
        """Send a mock snapshot image"""
        try:
            # Create a simple test image (PNG format)
            # This is a minimal 1x1 white pixel PNG
            png_data = base64.b64decode(
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=='
            )
            
            # Add timestamp overlay (mock)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("Mock camera snapshot requested at {}".format(timestamp))
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', str(len(png_data)))
            self.end_headers()
            self.wfile.write(png_data)
            
        except Exception as e:
            self.send_error(500, "Error generating snapshot: {}".format(str(e)))
    
    def log_message(self, format, *args):
        """Override log message to reduce noise"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print("[{}] {}".format(timestamp, format % args))

def start_mock_camera_server(port=8080):
    """Start mock camera server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, MockCameraHandler)
    
    print("Mock Camera Server Starting...")
    print("Server URL: http://localhost:{}".format(port))
    print("Snapshot URLs:")
    print("  Default: http://localhost:{}/Streaming/Channels/1/picture".format(port))
    print("  Hikvision: http://localhost:{}/ISAPI/Streaming/channels/101/picture".format(port))
    print("  Glenz: http://localhost:{}/onvif-http/snapshot?Profile_1".format(port))
    print("  Dahua: http://localhost:{}/cgi-bin/snapshot.cgi?channel=1".format(port))
    print("  Custom: http://localhost:{}/Snapshot/1/RemoteImageCapture?ImageFormat=2".format(port))
    print("\nTo test with curl:")
    print("  curl http://localhost:{}/Streaming/Channels/1/picture -o test.jpg".format(port))
    print("  curl http://admin:admin@localhost:{}/Snapshot/1/RemoteImageCapture?ImageFormat=2 -o test.jpg".format(port))
    print("\nPress Ctrl+C to stop server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down mock camera server...")
        httpd.shutdown()

if __name__ == "__main__":
    # Start on port 8080 by default
    start_mock_camera_server(8080)
