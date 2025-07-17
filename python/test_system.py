"""
Test script for parking system components
"""
import asyncio
import websockets
import json
import sys
import os
import time
from datetime import datetime

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

from config import Config

async def test_server_connection():
    """Test WebSocket server connection"""
    print("Testing server connection...")
    
    config = Config('config.ini')
    server_url = f"ws://{config.get('WEBSOCKET', 'server_host')}:{config.get('WEBSOCKET', 'server_port')}"
    
    try:
        async with websockets.connect(server_url) as websocket:
            # Register as test client
            await websocket.send(json.dumps({
                'type': 'register',
                'client_id': 'test_client'
            }))
            
            # Wait for welcome message
            response = await websocket.recv()
            data = json.loads(response)
            print(f"✓ Server response: {data.get('message', 'Connected')}")
            
            # Test ALPR request
            await websocket.send(json.dumps({
                'type': 'alpr_request',
                'gate_id': 'test_gate'
            }))
            
            response = await websocket.recv()
            data = json.loads(response)
            if data.get('type') == 'alpr_response':
                print(f"✓ ALPR response received: {data.get('success', False)}")
            
            return True
    except Exception as e:
        print(f"✗ Server connection failed: {e}")
        return False

def test_gpio_simulation():
    """Test GPIO simulation"""
    print("Testing GPIO simulation...")
    
    try:
        from shared.gpio import GPIOService
        config = Config('config.ini')
        gpio = GPIOService(config)
        
        print("✓ GPIO service initialized")
        
        # Test gate opening
        gpio.open_gate()
        print("✓ Gate open simulation")
        
        # Test ticket printing
        gpio.print_ticket()
        print("✓ Ticket print simulation")
        
        gpio.cleanup()
        return True
    except Exception as e:
        print(f"✗ GPIO test failed: {e}")
        return False

def test_camera_simulation():
    """Test camera simulation"""
    print("Testing camera simulation...")
    
    try:
        from shared.camera import CameraService
        config = Config('config.ini')
        camera = CameraService(config)
        
        # This will fail in simulation but should handle gracefully
        image = camera.capture_image()
        if image is None:
            print("✓ Camera simulation handled gracefully")
        else:
            print("✓ Camera captured image")
        
        return True
    except Exception as e:
        print(f"✗ Camera test failed: {e}")
        return False

def test_audio_simulation():
    """Test audio simulation"""
    print("Testing audio simulation...")
    
    try:
        from shared.audio import AudioService
        config = Config('config.ini')
        audio = AudioService(config)
        
        audio.play_welcome()
        print("✓ Welcome audio simulation")
        
        audio.play_goodbye()
        print("✓ Goodbye audio simulation")
        
        audio.cleanup()
        return True
    except Exception as e:
        print(f"✗ Audio test failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    
    try:
        from shared.database import DatabaseService
        config = Config('config.ini')
        
        # This will fail if CouchDB is not running, but should handle gracefully
        try:
            database = DatabaseService(config)
            print("✓ Database connection successful")
            
            # Test saving a transaction
            test_transaction = {
                'type': 'test_transaction',
                'timestamp': datetime.now().isoformat(),
                'test_data': 'This is a test'
            }
            
            doc_id = database.save_transaction(test_transaction)
            print(f"✓ Test transaction saved: {doc_id}")
            
            return True
        except Exception as e:
            print(f"⚠ Database connection failed (expected if CouchDB not running): {e}")
            return False
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_alpr_simulation():
    """Test ALPR simulation"""
    print("Testing ALPR simulation...")
    
    try:
        from server.alpr.alpr_service import ALPRService
        config = Config('config.ini')
        alpr = ALPRService(config)
        
        # Create dummy image data
        dummy_image = b'\x89PNG\r\n\x1a\n...'  # Dummy image bytes
        
        result = alpr.detect_plate_from_bytes(dummy_image)
        if result:
            print(f"✓ ALPR simulation returned: {result.get('plate_number', 'N/A')}")
        else:
            print("✓ ALPR simulation handled gracefully")
        
        return True
    except Exception as e:
        print(f"✗ ALPR test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("=== Parking System Component Tests ===\n")
    
    tests = [
        ("Configuration", lambda: test_config()),
        ("GPIO Simulation", test_gpio_simulation),
        ("Camera Simulation", test_camera_simulation),
        ("Audio Simulation", test_audio_simulation),
        ("ALPR Simulation", test_alpr_simulation),
        ("Database Connection", test_database_connection),
        ("Server Connection", test_server_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n=== Test Results ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System ready for development.")
    elif passed > total // 2:
        print("⚠ Most tests passed. Check failed components.")
    else:
        print("❌ Many tests failed. Check system setup.")

def test_config():
    """Test configuration loading"""
    print("Testing configuration...")
    
    try:
        config = Config('config.ini')
        
        # Test getting values
        db_host = config.get('DATABASE', 'host')
        print(f"✓ Database host: {db_host}")
        
        alpr_enabled = config.getboolean('ALPR', 'enabled')
        print(f"✓ ALPR enabled: {alpr_enabled}")
        
        cctv_url = config.cctv_url
        print(f"✓ CCTV URL: {cctv_url}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Parking System Test Suite")
    print("=" * 40)
    
    # Check if config file exists
    if not os.path.exists('config.ini'):
        print("❌ config.ini not found. Please copy and configure it first.")
        return
    
    # Run tests
    asyncio.run(run_all_tests())

if __name__ == '__main__':
    main()
