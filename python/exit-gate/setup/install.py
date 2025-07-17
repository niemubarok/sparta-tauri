#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exit Gate System - Installation and Setup Script for Raspberry Pi
"""

from __future__ import print_function, unicode_literals, absolute_import
import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if we're running on compatible Python version"""
    version = sys.version_info
    print("Python version: {}.{}.{}".format(version.major, version.minor, version.micro))
    
    if version.major == 2 and version.minor < 7:
        print("ERROR: Python 2.7 or higher required")
        return False
    elif version.major == 3 and version.minor < 5:
        print("ERROR: Python 3.5 or higher required")
        return False
    
    print("✓ Python version compatible")
    return True

def check_platform():
    """Check if we're on Raspberry Pi"""
    is_rpi = False
    
    try:
        with open('/proc/cpuinfo', 'r') as f:
            content = f.read()
            if 'BCM' in content or 'Raspberry' in content:
                is_rpi = True
    except:
        pass
    
    system = platform.system()
    machine = platform.machine()
    
    print("Platform: {} {}".format(system, machine))
    if is_rpi:
        print("✓ Raspberry Pi detected")
    else:
        print("⚠ Not running on Raspberry Pi - some features may be limited")
    
    return is_rpi

def install_system_dependencies():
    """Install system-level dependencies"""
    print("\n=== Installing system dependencies ===")
    
    # Update package list
    print("Updating package list...")
    subprocess.call(['sudo', 'apt-get', 'update', '-y'])
    
    # Essential packages
    packages = [
        'python-pip' if sys.version_info.major == 2 else 'python3-pip',
        'python-dev' if sys.version_info.major == 2 else 'python3-dev',
        'build-essential',
        'git',
        'curl',
        'wget',
        'ffmpeg',
        'portaudio19-dev',
        'alsa-utils',
        'pulseaudio',
        'libjpeg-dev',
        'libpng-dev',
        'libfreetype6-dev',
        'libffi-dev',
        'libssl-dev'
    ]
    
    print("Installing packages: {}".format(', '.join(packages)))
    cmd = ['sudo', 'apt-get', 'install', '-y'] + packages
    result = subprocess.call(cmd)
    
    if result == 0:
        print("✓ System dependencies installed successfully")
    else:
        print("✗ Failed to install system dependencies")
        return False
    
    return True

def setup_gpio():
    """Setup GPIO access for pi user"""
    print("\n=== Setting up GPIO access ===")
    
    # Add pi user to gpio group
    subprocess.call(['sudo', 'usermod', '-a', '-G', 'gpio', 'pi'])
    
    # Install RPi.GPIO if on Raspberry Pi
    try:
        if sys.version_info.major == 2:
            subprocess.call(['sudo', 'pip', 'install', 'RPi.GPIO==0.7.0'])
        else:
            subprocess.call(['sudo', 'pip3', 'install', 'RPi.GPIO'])
        print("✓ GPIO setup complete")
        return True
    except:
        print("⚠ GPIO setup failed - may not be on Raspberry Pi")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("\n=== Installing Python dependencies ===")
    
    # Upgrade pip first
    if sys.version_info.major == 2:
        subprocess.call(['python', '-m', 'pip', 'install', '--upgrade', 'pip==20.3.4'])
    else:
        subprocess.call(['python3', '-m', 'pip', 'install', '--upgrade', 'pip'])
    
    # Install requirements
    if os.path.exists('requirements.txt'):
        print("Installing from requirements.txt...")
        if sys.version_info.major == 2:
            result = subprocess.call(['pip', 'install', '-r', 'requirements.txt'])
        else:
            result = subprocess.call(['pip3', 'install', '-r', 'requirements.txt'])
        
        if result == 0:
            print("✓ Python dependencies installed successfully")
            return True
        else:
            print("✗ Failed to install Python dependencies")
            return False
    else:
        print("✗ requirements.txt not found")
        return False

def setup_audio():
    """Setup audio system"""
    print("\n=== Setting up audio system ===")
    
    # Add pi user to audio group
    subprocess.call(['sudo', 'usermod', '-a', '-G', 'audio', 'pi'])
    
    # Create sounds directory
    sounds_dir = os.path.join(os.path.dirname(__file__), 'sounds')
    if not os.path.exists(sounds_dir):
        os.makedirs(sounds_dir)
        print("✓ Created sounds directory")
    
    # Test audio
    print("Testing audio system...")
    try:
        import pygame
        pygame.mixer.init()
        print("✓ Audio system working")
        return True
    except Exception as e:
        print("⚠ Audio test failed: {}".format(e))
        return False

def setup_database():
    """Setup database directory and test CouchDB connection"""
    print("\n=== Setting up database ===")
    
    # Create database directory
    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print("✓ Created database directory")
    
    # Test CouchDB module
    try:
        import couchdb
        print("✓ CouchDB module available")
        return True
    except ImportError as e:
        print("✗ CouchDB module not available: {}".format(e))
        return False

def create_config():
    """Create default configuration file"""
    print("\n=== Creating configuration ===")
    
    config_file = os.path.join(os.path.dirname(__file__), 'config.ini')
    
    if os.path.exists(config_file):
        print("✓ Configuration file already exists")
        return True
    
    try:
        # Import and create default config
        sys.path.insert(0, os.path.dirname(__file__))
        from config import Config
        
        config = Config()
        config.save()
        print("✓ Default configuration created")
        return True
    except Exception as e:
        print("✗ Failed to create configuration: {}".format(e))
        return False

def setup_systemd_service():
    """Setup systemd service for auto-start"""
    print("\n=== Setting up systemd service ===")
    
    service_content = """[Unit]
Description=Exit Gate System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/exit-gate/python-app
ExecStart=/usr/bin/python /home/pi/exit-gate/python-app/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = '/etc/systemd/system/exit-gate.service'
    
    try:
        with open('/tmp/exit-gate.service', 'w') as f:
            f.write(service_content)
        
        subprocess.call(['sudo', 'mv', '/tmp/exit-gate.service', service_file])
        subprocess.call(['sudo', 'systemctl', 'daemon-reload'])
        
        print("✓ Systemd service created")
        print("  To enable auto-start: sudo systemctl enable exit-gate")
        print("  To start service: sudo systemctl start exit-gate")
        print("  To check status: sudo systemctl status exit-gate")
        return True
    except Exception as e:
        print("⚠ Failed to setup systemd service: {}".format(e))
        return False

def create_launcher_script():
    """Create launcher script"""
    print("\n=== Creating launcher script ===")
    
    script_content = """#!/bin/bash
# Exit Gate System Launcher

cd "$(dirname "$0")"

echo "Starting Exit Gate System..."
echo "Python version: $(python --version 2>&1)"
echo "Working directory: $(pwd)"

# Check if config exists
if [ ! -f "config.ini" ]; then
    echo "Creating default configuration..."
    python -c "from config import Config; Config().save()"
fi

# Start the application
python main.py
"""
    
    script_file = os.path.join(os.path.dirname(__file__), 'start.sh')
    
    try:
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # Make executable
        os.chmod(script_file, 0o755)
        print("✓ Launcher script created: start.sh")
        return True
    except Exception as e:
        print("✗ Failed to create launcher script: {}".format(e))
        return False

def test_installation():
    """Test the installation"""
    print("\n=== Testing installation ===")
    
    # Test imports
    test_modules = [
        'flask',
        'configparser' if sys.version_info.major == 3 else 'ConfigParser',
        'couchdb',
        'pygame',
        'PIL',
        'requests'
    ]
    
    failed_imports = []
    
    for module in test_modules:
        try:
            __import__(module)
            print("✓ {}".format(module))
        except ImportError:
            print("✗ {}".format(module))
            failed_imports.append(module)
    
    if failed_imports:
        print("\n✗ Some modules failed to import: {}".format(', '.join(failed_imports)))
        return False
    
    # Test configuration
    try:
        sys.path.insert(0, os.path.dirname(__file__))
        from config import Config
        config = Config()
        print("✓ Configuration system working")
    except Exception as e:
        print("✗ Configuration test failed: {}".format(e))
        return False
    
    print("\n✓ Installation test completed successfully!")
    return True

def main():
    """Main installation function"""
    print("=" * 60)
    print("Exit Gate System - Installation Script")
    print("=" * 60)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print("Working directory: {}".format(script_dir))
    
    # Check requirements
    if not check_python_version():
        sys.exit(1)
    
    is_rpi = check_platform()
    
    # Installation steps
    steps = [
        install_system_dependencies,
        setup_gpio if is_rpi else lambda: True,
        install_python_dependencies,
        setup_audio,
        setup_database,
        create_config,
        create_launcher_script,
        setup_systemd_service if is_rpi else lambda: True,
        test_installation
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for i, step in enumerate(steps, 1):
        print("\n[{}/{}] {}".format(i, total_steps, step.__name__.replace('_', ' ').title()))
        
        try:
            if step():
                success_count += 1
                print("✓ Step completed successfully")
            else:
                print("✗ Step failed")
        except Exception as e:
            print("✗ Step failed with error: {}".format(e))
    
    # Summary
    print("\n" + "=" * 60)
    print("Installation Summary: {}/{} steps completed".format(success_count, total_steps))
    
    if success_count == total_steps:
        print("✓ Installation completed successfully!")
        print("\nNext steps:")
        print("1. Edit config.ini to configure your system")
        print("2. Run: ./start.sh to start the application")
        print("3. Or run: python main.py")
        print("4. Access web interface at: http://localhost:5000")
        
        if is_rpi:
            print("\nFor auto-start on boot:")
            print("sudo systemctl enable exit-gate")
            print("sudo systemctl start exit-gate")
    else:
        print("⚠ Installation completed with {} issues".format(total_steps - success_count))
        print("Please review the errors above and try again")
        sys.exit(1)

if __name__ == '__main__':
    main()
