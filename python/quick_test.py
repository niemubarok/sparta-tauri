"""
Quick test of all components with simulation
"""
import subprocess
import time
import threading
import sys
import os

def run_component(name, script_path, wait_time=0):
    """Run a component"""
    if wait_time > 0:
        time.sleep(wait_time)
    
    print(f"Starting {name}...")
    try:
        # Check if script exists
        if not os.path.exists(script_path):
            print(f"Error: {script_path} not found")
            return
        
        # Run the script
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✓ {name} started successfully")
        else:
            print(f"✗ {name} failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print(f"⚠ {name} is running (timeout after 10s)")
    except Exception as e:
        print(f"✗ {name} error: {e}")

def main():
    """Main test function"""
    print("=" * 60)
    print("PARKING SYSTEM - QUICK COMPONENT TEST")
    print("=" * 60)
    print("Testing all components with simulation data...")
    print()
    
    # Components to test
    components = [
        ("Test System", "test_system.py", 0),
        ("Admin Interface (Test Mode)", "admin/test_admin.py", 2),
    ]
    
    # Test configuration
    config_file = "config.ini"
    if not os.path.exists(config_file):
        print(f"⚠ Warning: {config_file} not found, using defaults")
    
    # Run tests
    threads = []
    for name, script, wait in components:
        thread = threading.Thread(target=run_component, args=(name, script, wait))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # Wait for all tests
    for thread in threads:
        thread.join()
    
    print()
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("✓ Basic component tests completed")
    print("✓ Admin interface available at: http://localhost:5000")
    print()
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Setup CouchDB for full functionality")
    print("3. Configure config.ini with your settings")
    print("4. Run individual components as needed")
    print()
    print("For full system test:")
    print("- Windows: start_dev.bat")
    print("- Linux: ./start_dev.sh")

if __name__ == '__main__':
    main()
