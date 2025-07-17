#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gate Service Diagnostic Tool untuk Exit Gate System
Mendiagnosis dan memperbaiki masalah gate service yang tidak bereaksi
"""

import sys
import os
import subprocess
import time
import logging
import json
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GateServiceDiagnostic:
    def __init__(self):
        self.results = {}
        self.errors = []
        
    def log_result(self, test_name, success, message="", details=None):
        """Log test result"""
        self.results[test_name] = {
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        if not success:
            self.errors.append(f"{test_name}: {message}")

    def check_raspberry_pi(self):
        """Cek apakah berjalan di Raspberry Pi"""
        print("1️⃣ Memeriksa Raspberry Pi...")
        
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpuinfo = f.read()
            
            is_pi = 'Raspberry Pi' in cpuinfo or 'BCM' in cpuinfo
            
            if is_pi:
                # Extract model info
                model_line = [line for line in cpuinfo.split('\n') if 'Model' in line]
                model = model_line[0].split(':')[1].strip() if model_line else "Unknown"
                
                print(f"   ✅ Raspberry Pi terdeteksi: {model}")
                self.log_result('raspberry_pi_check', True, f"Model: {model}", {'model': model})
                return True
            else:
                print("   ❌ Tidak berjalan di Raspberry Pi")
                self.log_result('raspberry_pi_check', False, "Tidak berjalan di Raspberry Pi")
                return False
                
        except Exception as e:
            print(f"   ❌ Error cek Raspberry Pi: {e}")
            self.log_result('raspberry_pi_check', False, f"Error: {e}")
            return False

    def check_gpio_permissions(self):
        """Cek permissions GPIO"""
        print("\n2️⃣ Memeriksa GPIO Permissions...")
        
        issues = []
        
        # Cek grup gpio
        try:
            result = subprocess.run(['groups'], capture_output=True, text=True)
            groups = result.stdout.strip()
            if 'gpio' in groups:
                print("   ✅ User sudah dalam grup 'gpio'")
            else:
                print("   ❌ User TIDAK dalam grup 'gpio'")
                issues.append("User not in gpio group")
        except Exception as e:
            print(f"   ❌ Error cek grup: {e}")
            issues.append(f"Group check error: {e}")
        
        # Cek /dev/gpiomem
        if os.path.exists('/dev/gpiomem'):
            stat = os.stat('/dev/gpiomem')
            print(f"   ✅ /dev/gpiomem ada (mode: {oct(stat.st_mode)})")
        else:
            print("   ❌ /dev/gpiomem tidak ada")
            issues.append("/dev/gpiomem missing")
        
        # Cek /sys/class/gpio/export
        if os.path.exists('/sys/class/gpio/export'):
            try:
                # Test write permission
                with open('/sys/class/gpio/export', 'a') as f:
                    pass
                print("   ✅ /sys/class/gpio/export bisa ditulis")
            except PermissionError:
                print("   ❌ /sys/class/gpio/export tidak bisa ditulis")
                issues.append("GPIO export permission denied")
        else:
            print("   ❌ /sys/class/gpio/export tidak ada")
            issues.append("GPIO export missing")
        
        success = len(issues) == 0
        self.log_result('gpio_permissions', success, 
                       "GPIO permissions OK" if success else f"Issues: {', '.join(issues)}", 
                       {'issues': issues})
        
        return success

    def test_gpio_hardware(self, pin=24):
        """Test GPIO hardware secara manual"""
        print(f"\n3️⃣ Test GPIO Hardware (Pin {pin})...")
        
        try:
            # Cleanup dulu
            try:
                with open('/sys/class/gpio/unexport', 'w') as f:
                    f.write(str(pin))
                time.sleep(0.1)
            except:
                pass
            
            # Export pin
            with open('/sys/class/gpio/export', 'w') as f:
                f.write(str(pin))
            print(f"   ✅ GPIO {pin} berhasil di-export")
            
            time.sleep(0.1)
            
            # Set direction ke output
            with open(f'/sys/class/gpio/gpio{pin}/direction', 'w') as f:
                f.write('out')
            print(f"   ✅ GPIO {pin} direction set ke OUTPUT")
            
            # Test HIGH
            print(f"   🔆 Setting GPIO {pin} ke HIGH...")
            with open(f'/sys/class/gpio/gpio{pin}/value', 'w') as f:
                f.write('1')
            
            # Baca kembali nilai
            with open(f'/sys/class/gpio/gpio{pin}/value', 'r') as f:
                value_high = f.read().strip()
            print(f"   📖 GPIO {pin} value HIGH: {value_high}")
            
            time.sleep(1)
            
            # Test LOW
            print(f"   🔅 Setting GPIO {pin} ke LOW...")
            with open(f'/sys/class/gpio/gpio{pin}/value', 'w') as f:
                f.write('0')
            
            # Baca kembali nilai
            with open(f'/sys/class/gpio/gpio{pin}/value', 'r') as f:
                value_low = f.read().strip()
            print(f"   📖 GPIO {pin} value LOW: {value_low}")
            
            # Cleanup
            with open('/sys/class/gpio/unexport', 'w') as f:
                f.write(str(pin))
            print(f"   ✅ GPIO {pin} berhasil di-unexport")
            
            # Validate results
            success = value_high == '1' and value_low == '0'
            
            self.log_result('gpio_hardware_test', success, 
                           f"GPIO {pin} hardware test {'passed' if success else 'failed'}", 
                           {'pin': pin, 'high_value': value_high, 'low_value': value_low})
            
            return success
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.log_result('gpio_hardware_test', False, f"Error: {e}", {'pin': pin})
            return False

    def test_rpi_gpio_library(self):
        """Test RPi.GPIO library"""
        print("\n4️⃣ Test RPi.GPIO Library...")
        
        try:
            import RPi.GPIO as GPIO
            print("   ✅ RPi.GPIO berhasil diimport")
            
            # Setup
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            pin = 24
            GPIO.setup(pin, GPIO.OUT)
            print(f"   ✅ GPIO {pin} setup sebagai OUTPUT")
            
            # Test HIGH
            print(f"   🔆 Setting GPIO {pin} ke HIGH via RPi.GPIO...")
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(1)
            
            # Test LOW
            print(f"   🔅 Setting GPIO {pin} ke LOW via RPi.GPIO...")
            GPIO.output(pin, GPIO.LOW)
            time.sleep(1)
            
            # Cleanup
            GPIO.cleanup()
            print("   ✅ GPIO cleanup berhasil")
            
            self.log_result('rpi_gpio_library', True, "RPi.GPIO library test passed")
            return True
            
        except ImportError:
            print("   ❌ RPi.GPIO tidak tersedia")
            print("   💡 Install: sudo apt-get install python3-rpi.gpio")
            self.log_result('rpi_gpio_library', False, "RPi.GPIO not available")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            try:
                GPIO.cleanup()
            except:
                pass
            self.log_result('rpi_gpio_library', False, f"Error: {e}")
            return False

    def test_config_ini(self):
        """Test config.ini settings"""
        print("\n5️⃣ Test Configuration...")
        
        config_path = os.path.join(os.path.dirname(__file__), 'app', 'config.ini')
        
        try:
            if not os.path.exists(config_path):
                print(f"   ❌ config.ini tidak ditemukan di: {config_path}")
                self.log_result('config_test', False, f"config.ini not found at {config_path}")
                return False
            
            import configparser
            config = configparser.ConfigParser()
            config.read(config_path)
            
            print(f"   ✅ config.ini ditemukan: {config_path}")
            
            # Check gate section
            if 'gate' in config:
                gate_config = dict(config['gate'])
                print(f"   📝 Gate config: {gate_config}")
                
                # Check GPIO section
                if 'gpio' in config:
                    gpio_config = dict(config['gpio'])
                    print(f"   📝 GPIO config: {gpio_config}")
                else:
                    print("   ⚠️ GPIO section tidak ada dalam config")
                
                self.log_result('config_test', True, "Configuration loaded successfully", 
                               {'gate_config': gate_config, 'gpio_config': gpio_config if 'gpio' in config else {}})
                return True
            else:
                print("   ❌ Section 'gate' tidak ada dalam config")
                self.log_result('config_test', False, "Gate section missing in config")
                return False
                
        except Exception as e:
            print(f"   ❌ Error reading config: {e}")
            self.log_result('config_test', False, f"Config read error: {e}")
            return False

    def test_gate_service_import(self):
        """Test gate service import dan initialization"""
        print("\n6️⃣ Test Gate Service Import...")
        
        try:
            from gate_service import gate_service
            print("   ✅ Gate service berhasil diimport")
            
            # Get service info
            control_mode = gate_service.get_control_mode()
            status = gate_service.get_status()
            
            print(f"   📊 Control mode: {control_mode}")
            print(f"   📊 Status: {status}")
            
            self.log_result('gate_service_import', True, "Gate service imported successfully",
                           {'control_mode': control_mode, 'status': status})
            
            return True, gate_service
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            # Print full traceback for debugging
            import traceback
            print("\n   Full error traceback:")
            for line in traceback.format_exc().splitlines():
                print(f"   {line}")
                
            self.log_result('gate_service_import', False, f"Import error: {e}")
            return False, None

    def test_gate_service_functionality(self, gate_service):
        """Test gate service functionality"""
        print("\n7️⃣ Test Gate Service Functionality...")
        
        if not gate_service:
            print("   ❌ Gate service tidak tersedia untuk testing")
            return False
        
        try:
            # Test open gate
            print("   🔓 Testing gate OPEN...")
            open_result = gate_service.open_gate()
            print(f"   📊 Open result: {'✅ SUCCESS' if open_result else '❌ FAILED'}")
            
            time.sleep(2)
            
            # Test close gate
            print("   🔒 Testing gate CLOSE...")
            close_result = gate_service.close_gate()
            print(f"   📊 Close result: {'✅ SUCCESS' if close_result else '❌ FAILED'}")
            
            # Get final status
            final_status = gate_service.get_status()
            print(f"   📊 Final status: {final_status}")
            
            success = open_result and close_result
            
            self.log_result('gate_service_functionality', success, 
                           "Gate service functionality test " + ("passed" if success else "failed"),
                           {'open_result': open_result, 'close_result': close_result, 'final_status': final_status})
            
            return success
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            self.log_result('gate_service_functionality', False, f"Functionality test error: {e}")
            return False

    def generate_report(self):
        """Generate diagnostic report"""
        print("\n" + "="*60)
        print("📊 DIAGNOSTIC REPORT")
        print("="*60)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result['success'])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print()
        
        for test_name, result in self.results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} {test_name}: {result['message']}")
        
        if self.errors:
            print("\n🔥 ISSUES FOUND:")
            for error in self.errors:
                print(f"   • {error}")
            
            print("\n💡 RECOMMENDED FIXES:")
            self.print_recommendations()
        else:
            print("\n🎉 ALL TESTS PASSED!")
            print("   Gate service should be working correctly.")
        
        # Save report to file
        report_file = os.path.join(os.path.dirname(__file__), 'gate_service_diagnostic_report.json')
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")

    def print_recommendations(self):
        """Print recommended fixes based on errors"""
        
        for error in self.errors:
            if "not in gpio group" in error.lower():
                print("   🔒 Fix GPIO permissions:")
                print("      sudo usermod -a -G gpio $USER")
                print("      sudo reboot")
            
            elif "gpio export permission" in error.lower():
                print("   🔧 Fix GPIO export permissions:")
                print("      sudo chmod 666 /sys/class/gpio/export")
                print("      sudo chmod 666 /sys/class/gpio/unexport")
            
            elif "rpi.gpio not available" in error.lower():
                print("   📦 Install RPi.GPIO:")
                print("      sudo apt-get update")
                print("      sudo apt-get install python3-rpi.gpio")
            
            elif "config.ini not found" in error.lower():
                print("   📝 Create config.ini:")
                print("      Copy config.ini from app/ directory")
            
            elif "gate section missing" in error.lower():
                print("   ⚙️ Fix config.ini:")
                print("      Add [gate] and [gpio] sections to config.ini")
            
            elif "import error" in error.lower():
                print("   🐍 Fix Python imports:")
                print("      Check app/ directory structure")
                print("      Ensure all required files exist")
            
            elif "functionality test" in error.lower():
                print("   🔌 Check hardware connections:")
                print("      Verify GPIO pin wiring")
                print("      Check relay module")
                print("      Test with multimeter")

    def run_auto_fix(self):
        """Run automatic fixes for common issues"""
        print("\n🔧 RUNNING AUTO FIX...")
        
        fixes_applied = []
        
        # Fix 1: GPIO permissions
        try:
            subprocess.run(['sudo', 'usermod', '-a', '-G', 'gpio', os.getenv('USER', 'pi')], check=True)
            fixes_applied.append("Added user to gpio group")
        except:
            pass
        
        try:
            subprocess.run(['sudo', 'chmod', '666', '/dev/gpiomem'], check=True)
            fixes_applied.append("Fixed /dev/gpiomem permissions")
        except:
            pass
        
        try:
            subprocess.run(['sudo', 'chmod', '666', '/sys/class/gpio/export'], check=True)
            subprocess.run(['sudo', 'chmod', '666', '/sys/class/gpio/unexport'], check=True)
            fixes_applied.append("Fixed GPIO export permissions")
        except:
            pass
        
        # Fix 2: Create udev rules
        try:
            udev_content = """# GPIO permissions for exit gate system
KERNEL=="gpiomem", GROUP="gpio", MODE="0666"
KERNEL=="gpio*", GROUP="gpio", MODE="0666"
SUBSYSTEM=="gpio", GROUP="gpio", MODE="0666"
"""
            
            with open('/tmp/99-gpio-exit-gate.rules', 'w') as f:
                f.write(udev_content)
            
            subprocess.run(['sudo', 'mv', '/tmp/99-gpio-exit-gate.rules', '/etc/udev/rules.d/'], check=True)
            subprocess.run(['sudo', 'udevadm', 'control', '--reload-rules'], check=True)
            fixes_applied.append("Created GPIO udev rules")
        except:
            pass
        
        # Fix 3: Create default config if missing
        config_path = os.path.join(os.path.dirname(__file__), 'app', 'config.ini')
        if not os.path.exists(config_path):
            try:
                default_config = """[gate]
control_mode = gpio
serial_port = /dev/ttyUSB0
baud_rate = 9600
timeout = 5

[gpio]
gate_pin = 24
active_high = true
power_pin = 16
busy_pin = 20
live_pin = 21

[database]
local_db = transactions
remote_url = http://localhost:5984
username = admin
password = password
auto_sync = true
"""
                with open(config_path, 'w') as f:
                    f.write(default_config)
                fixes_applied.append("Created default config.ini")
            except:
                pass
        
        if fixes_applied:
            print("✅ Auto fixes applied:")
            for fix in fixes_applied:
                print(f"   • {fix}")
            print("\n⚠️  REBOOT REQUIRED: sudo reboot")
        else:
            print("❌ No auto fixes could be applied")

def main():
    """Main diagnostic function"""
    print("🚪 EXIT GATE SERVICE DIAGNOSTIC TOOL")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    diagnostic = GateServiceDiagnostic()
    
    # Run all tests
    diagnostic.check_raspberry_pi()
    diagnostic.check_gpio_permissions()
    diagnostic.test_gpio_hardware()
    diagnostic.test_rpi_gpio_library()
    diagnostic.test_config_ini()
    success, gate_service = diagnostic.test_gate_service_import()
    
    if success and gate_service:
        diagnostic.test_gate_service_functionality(gate_service)
    
    # Generate report
    diagnostic.generate_report()
    
    # Offer auto fix
    if diagnostic.errors:
        print("\n🤖 Run auto-fix? (y/n): ", end="")
        try:
            response = input().lower().strip()
            if response in ['y', 'yes']:
                diagnostic.run_auto_fix()
        except KeyboardInterrupt:
            print("\nAuto-fix cancelled.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        print("🔧 RUNNING AUTO FIX ONLY...")
        diagnostic = GateServiceDiagnostic()
        diagnostic.run_auto_fix()
    else:
        main()
