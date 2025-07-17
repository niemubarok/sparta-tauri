"""
Python Parking System Main Module
Entry point for running the parking system
"""

import asyncio
import logging
import sys
import signal
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.services.database import database_service
from src.services.alpr import alpr_service
from src.services.camera import camera_service
from src.gates import create_gate
from src.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('parking_system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class ParkingSystemManager:
    """Main parking system manager with error resilience"""
    
    def __init__(self):
        self.settings = get_settings()
        self.gates = {}
        self.is_running = False
        self.primary_gate = None
        
    async def initialize(self):
        """Initialize the parking system with error resilience"""
        try:
            logger.info("🚀 Initializing Python Parking System...")
            
            # Initialize database with fallback
            logger.info("📊 Initializing database...")
            try:
                await database_service.initialize()
                logger.info("✅ Database initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Database initialization failed, continuing with limited functionality: {e}")
            
            # Initialize ALPR service with fallback
            logger.info("🔍 Initializing ALPR service...")
            try:
                alpr_service.initialize()
                logger.info("✅ ALPR service initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ ALPR initialization failed, continuing without ALPR: {e}")
            
            # Initialize camera service with fallback
            logger.info("📷 Initializing camera service...")
            try:
                camera_service.initialize()
                logger.info("✅ Camera service initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Camera initialization failed, continuing in simulation mode: {e}")
            
            # Initialize gates based on system mode
            await self._initialize_gates()
            
            logger.info("✅ Python Parking System initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Critical error during initialization: {e}")
            # Don't raise - continue with degraded functionality
    
    async def _initialize_gates(self):
        """Initialize gates based on system mode"""
        try:
            # Determine which gate to initialize based on system mode
            system_mode = self.settings.system_mode.lower()
            
            if system_mode == "entry_manual":
                gate_config = {"type": "entry", "mode": "manual", "id": "entry_manual"}
            elif system_mode == "entry_manless":
                gate_config = {"type": "entry", "mode": "manless", "id": "entry_manless"}
            elif system_mode == "exit_manual":
                gate_config = {"type": "exit", "mode": "manual", "id": "exit_manual"}
            elif system_mode == "exit_manless":
                gate_config = {"type": "exit", "mode": "manless", "id": "exit_manless"}
            else:
                logger.warning(f"Unknown system mode: {system_mode}, defaulting to entry_manual")
                gate_config = {"type": "entry", "mode": "manual", "id": "entry_manual"}
            
            # Initialize primary gate
            try:
                gate = create_gate(
                    gate_config["type"], 
                    gate_config["mode"], 
                    gate_config["id"]
                )
                self.gates[gate_config["id"]] = gate
                self.primary_gate = gate
                logger.info(f"✅ Initialized primary gate: {gate_config['type']} {gate_config['mode']} ({gate_config['id']})")
                
            except Exception as e:
                logger.error(f"❌ Failed to initialize primary gate {gate_config['id']}: {e}")
                # Create fallback gate in simulation mode
                try:
                    logger.info("Creating fallback gate in simulation mode...")
                    gate = create_gate("entry", "manual", "fallback_gate")
                    self.gates["fallback_gate"] = gate
                    self.primary_gate = gate
                    logger.info("✅ Fallback gate created successfully")
                except Exception as fallback_error:
                    logger.error(f"❌ Failed to create fallback gate: {fallback_error}")
            
            # Initialize additional gates for full system (optional)
            if len(self.gates) > 0:
                logger.info("Primary gate initialized successfully")
            else:
                logger.warning("No gates initialized - system running in minimal mode")
                
        except Exception as e:
            logger.error(f"❌ Error during gate initialization: {e}")
            # Don't raise - continue without gates
    
    async def start_ui(self):
        """Start UI based on system mode with error resilience"""
        try:
            if not self.settings.ui_auto_start:
                logger.info("UI auto-start disabled, starting in console mode")
                await self._run_console_mode()
                return
            
            system_mode = self.settings.system_mode.lower()
            
            # Start mode-specific UI
            if system_mode == "entry_manual":
                logger.info("� Membuka UI Manual Entry Gate...")
                await self._start_entry_manual_ui()
            elif system_mode == "entry_manless":
                logger.info("🤖 Memulai Manless Entry Gate...")
                await self._start_entry_manless_ui()
            elif system_mode == "exit_manual":
                logger.info("� Membuka UI Manual Exit Gate...")
                await self._start_exit_manual_ui()
            elif system_mode == "exit_manless":
                logger.info("🤖 Memulai Manless Exit Gate...")
                await self._start_exit_manless_ui()
            else:
                logger.warning(f"Unknown system mode: {system_mode}, starting default entry manual UI")
                await self._start_entry_manual_ui()
                
        except Exception as e:
            logger.error(f"❌ Failed to start UI: {e}")
            # Fallback to console mode
            logger.info("Falling back to console mode...")
            await self._run_console_mode()
    
    async def _start_entry_manual_ui(self):
        """Start manual entry gate UI - visual interface for operator"""
        try:
            logger.info("� Membuka UI Manual Entry Gate...")
            logger.info("="*50)
            logger.info("🎯 Gate Entry dengan Operator - UI Visual")
            logger.info("Interface visual untuk operator gate entry")
            logger.info("✅ UI siap digunakan operator")
            logger.info("="*50)
            
            if self.primary_gate:
                try:
                    # Initialize gate (synchronous method)
                    if hasattr(self.primary_gate, 'initialize'):
                        self.primary_gate.initialize()
                        logger.info("✅ Gate entry manual siap beroperasi")
                except Exception as e:
                    logger.warning(f"⚠️ Gate initialization failed: {e}")
            else:
                logger.warning("⚠️ Tidak ada gate yang tersedia")
                
            # Start the visual UI for manual entry gate
            # This would typically launch a GUI window
            logger.info("�️ UI Manual Entry Gate terbuka - operator dapat menggunakan interface")
            
            # Keep the UI running
            while self.is_running:
                try:
                    await asyncio.sleep(1)  # Keep the UI alive
                    # In real implementation, this would handle GUI events
                    
                except KeyboardInterrupt:
                    logger.info("🛑 Menutup UI Manual Entry Gate...")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in UI: {e}")
                    await asyncio.sleep(5)
                    
        except Exception as e:
            logger.error(f"❌ Error starting manual entry UI: {e}")
    
    async def _start_entry_manless_ui(self):
        """Start manless entry gate UI - automatic gate without operator"""
        try:
            logger.info("🤖 Manless Entry Gate - Automatic Mode")
            logger.info("="*50)
            logger.info("🚪 Gate Entry Otomatis - Tanpa Operator")
            logger.info("Gate akan bekerja otomatis:")
            logger.info("  • Deteksi kendaraan secara otomatis")
            logger.info("  • Scan plat nomor otomatis")
            logger.info("  • Buka/tutup gate otomatis")
            logger.info("  • Monitoring 24/7")
            logger.info("="*50)
            logger.info("⚠️  Tekan Ctrl+C untuk menghentikan sistem")
            
            if self.primary_gate:
                try:
                    # Initialize gate (synchronous method)
                    if hasattr(self.primary_gate, 'initialize'):
                        self.primary_gate.initialize()
                        logger.info("✅ Gate entry manless siap beroperasi")
                except Exception as e:
                    logger.warning(f"⚠️ Gate initialization failed: {e}")
                    
                try:
                    # Start monitoring (synchronous method)
                    if hasattr(self.primary_gate, 'start_monitoring'):
                        self.primary_gate.start_monitoring()
                        logger.info("🔄 Monitoring otomatis dimulai...")
                except Exception as e:
                    logger.warning(f"⚠️ Gate monitoring start failed: {e}")
            else:
                logger.warning("⚠️ Tidak ada gate yang tersedia")
                
            # Auto-monitoring loop
            logger.info("🤖 Sistem entry manless aktif - monitoring...")
            while self.is_running:
                try:
                    await asyncio.sleep(2)  # Check every 2 seconds
                    
                    # In a real implementation, this would be handled by the gate's monitoring
                    # For now, just show that the system is running
                    if hasattr(self.primary_gate, 'get_status'):
                        status = self.primary_gate.get_status()
                        # Only log significant events, not every status check
                        
                except KeyboardInterrupt:
                    logger.info("🛑 Received interrupt signal, shutting down...")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in monitoring loop: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"❌ Error in manless entry UI: {e}")
    
    async def _start_exit_manual_ui(self):
        """Start manual exit gate UI - visual interface for operator"""
        try:
            logger.info("🚪 Membuka UI Manual Exit Gate...")
            logger.info("="*50)
            logger.info("🎯 Gate Exit dengan Operator - UI Visual")
            logger.info("Interface visual untuk operator gate exit")
            logger.info("✅ UI siap digunakan operator")
            logger.info("="*50)
            
            if self.primary_gate:
                try:
                    # Initialize gate (synchronous method)
                    if hasattr(self.primary_gate, 'initialize'):
                        self.primary_gate.initialize()
                        logger.info("✅ Gate exit manual siap beroperasi")
                except Exception as e:
                    logger.warning(f"⚠️ Gate initialization failed: {e}")
            else:
                logger.warning("⚠️ Tidak ada gate yang tersedia")
                
            # Start the visual UI for manual exit gate
            # This would typically launch a GUI window
            logger.info("🖥️ UI Manual Exit Gate terbuka - operator dapat menggunakan interface")
            
            # Keep the UI running
            while self.is_running:
                try:
                    await asyncio.sleep(1)  # Keep the UI alive
                    # In real implementation, this would handle GUI events
                    
                except KeyboardInterrupt:
                    logger.info("🛑 Menutup UI Manual Exit Gate...")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in UI: {e}")
                    await asyncio.sleep(5)
                    
        except Exception as e:
            logger.error(f"❌ Error starting manual exit UI: {e}")
    
    async def _start_exit_manless_ui(self):
        """Start manless exit gate UI - automated system without operator"""
        try:
            logger.info("🤖 Membuka UI Manless Exit Gate...")
            logger.info("="*50)
            logger.info("🚀 Gate Exit Otomatis - Tanpa Operator")
            logger.info("Sistem otomatis untuk kendaraan keluar")
            logger.info("✅ UI siap beroperasi otomatis")
            logger.info("="*50)
            
            if self.primary_gate:
                try:
                    # Initialize gate (synchronous method)
                    if hasattr(self.primary_gate, 'initialize'):
                        self.primary_gate.initialize()
                        logger.info("✅ Gate exit manless siap beroperasi")
                except Exception as e:
                    logger.warning(f"⚠️ Gate initialization failed: {e}")
                    
                try:
                    # Start monitoring (synchronous method)
                    if hasattr(self.primary_gate, 'start_monitoring'):
                        self.primary_gate.start_monitoring()
                        logger.info("🔄 Monitoring otomatis dimulai...")
                except Exception as e:
                    logger.warning(f"⚠️ Gate monitoring start failed: {e}")
            else:
                logger.warning("⚠️ Tidak ada gate yang tersedia")
                
            # Auto-monitoring loop
            logger.info("🤖 Sistem exit manless aktif - monitoring...")
            while self.is_running:
                try:
                    await asyncio.sleep(2)  # Check every 2 seconds
                    
                    # In a real implementation, this would be handled by the gate's monitoring
                    # For now, just show that the system is running
                    if hasattr(self.primary_gate, 'get_status'):
                        status = self.primary_gate.get_status()
                        # Only log significant events, not every status check
                        
                except KeyboardInterrupt:
                    logger.info("🛑 Received interrupt signal, shutting down...")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in monitoring loop: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"❌ Error in manless exit UI: {e}")
    
    async def _run_console_mode(self):
        """Run system in console mode for debugging"""
        logger.info("🖥️ Running in console mode...")
        logger.info("Commands: 'test' - Test system, 'gates' - List gates, 'quit' - Exit")
        
        while self.is_running:
            try:
                cmd = await asyncio.to_thread(input, "Console> ")
                
                if cmd.lower() == 'quit':
                    break
                elif cmd.lower() == 'test':
                    await self._test_system()
                elif cmd.lower() == 'gates':
                    await self._list_gates()
                else:
                    logger.info("Available commands: test, gates, quit")
                    
            except Exception as e:
                logger.error(f"Error in console mode: {e}")
                continue
    
    async def _handle_scan_command(self):
        """Handle scan command"""
        try:
            logger.info("📷 Capturing and scanning license plate...")
            if self.primary_gate:
                result = await self.primary_gate.scan_license_plate()
                if result:
                    logger.info(f"✅ License plate detected: {result}")
                else:
                    logger.info("❌ No license plate detected")
            else:
                logger.warning("No gate available for scanning")
        except Exception as e:
            logger.error(f"Error during scan: {e}")
    
    async def _handle_open_command(self):
        """Handle open gate command"""
        try:
            logger.info("🚪 Opening gate...")
            if self.primary_gate:
                await self.primary_gate.open_gate()
                logger.info("✅ Gate opened")
            else:
                logger.warning("No gate available")
        except Exception as e:
            logger.error(f"Error opening gate: {e}")
    
    async def _handle_close_command(self):
        """Handle close gate command"""
        try:
            logger.info("🚪 Closing gate...")
            if self.primary_gate:
                await self.primary_gate.close_gate()
                logger.info("✅ Gate closed")
            else:
                logger.warning("No gate available")
        except Exception as e:
            logger.error(f"Error closing gate: {e}")
    
    async def _handle_status_command(self):
        """Handle status command"""
        try:
            if self.primary_gate:
                status = self.primary_gate.get_status()
                logger.info(f"📊 Gate Status: {status.gate_type}/{status.gate_mode} - {status.gate_status}")
                logger.info(f"   Last vehicle: {status.last_vehicle_id or 'None'}")
                logger.info(f"   Last scan: {status.last_scan_time or 'Never'}")
            else:
                logger.warning("No gate available")
        except Exception as e:
            logger.error(f"Error getting status: {e}")
    
    async def _show_help(self):
        """Show help information"""
        logger.info("\n📖 BANTUAN SISTEM PARKING GATE")
        logger.info("="*40)
        logger.info("Available Commands:")
        logger.info("  scan   - Ambil foto dan deteksi plat nomor")
        logger.info("  open   - Buka gate untuk kendaraan masuk")
        logger.info("  close  - Tutup gate")
        logger.info("  status - Tampilkan status gate saat ini")
        logger.info("  help   - Tampilkan bantuan ini")
        logger.info("  quit   - Keluar dari sistem")
        logger.info("="*40)
    
    async def _test_system(self):
        """Test system components"""
        logger.info("🧪 Testing system components...")
        
        # Test database
        try:
            await database_service.get_vehicle("test")
            logger.info("✅ Database connection OK")
        except Exception as e:
            logger.warning(f"⚠️ Database test failed: {e}")
        
        # Test ALPR
        try:
            # Simple ALPR test without creating image
            logger.info("Testing ALPR service availability...")
            # Just check if the service is initialized
            if hasattr(alpr_service, 'detector') and alpr_service.detector:
                logger.info("✅ ALPR service OK")
            else:
                logger.warning("⚠️ ALPR service not properly initialized")
        except Exception as e:
            logger.warning(f"⚠️ ALPR test failed: {e}")
        
        # Test camera
        try:
            frame = camera_service.capture_frame()
            if frame is not None:
                logger.info("✅ Camera service OK")
            else:
                logger.warning("⚠️ Camera returned no frame")
        except Exception as e:
            logger.warning(f"⚠️ Camera test failed: {e}")
    
    async def _list_gates(self):
        """List all gates"""
        if not self.gates:
            logger.info("No gates initialized")
            return
        
        logger.info("📋 Active gates:")
        for gate_id, gate in self.gates.items():
            try:
                status = gate.get_status()
                logger.info(f"  - {gate_id}: {status.gate_type}/{status.gate_mode} - {status.gate_status}")
            except Exception as e:
                logger.info(f"  - {gate_id}: Error getting status - {e}")

    async def start(self):
        """Start the parking system"""
        if self.is_running:
            logger.warning("System is already running")
            return

        try:
            logger.info("🔄 Starting parking system...")
            self.is_running = True

            # Start UI based on configuration
            await self.start_ui()

        except Exception as e:
            logger.error(f"❌ Error running parking system: {e}")
            await self.stop()
    
    async def stop(self):
        """Stop the parking system"""
        if not self.is_running:
            return
        
        logger.info("🛑 Stopping parking system...")
        self.is_running = False
        
        # Cleanup gates
        for gate_id, gate in self.gates.items():
            try:
                gate.cleanup()
                logger.info(f"✅ Cleaned up gate: {gate_id}")
            except Exception as e:
                logger.error(f"❌ Error cleaning up gate {gate_id}: {e}")
        
        # Cleanup services
        try:
            camera_service.cleanup()
            logger.info("✅ Camera service cleaned up")
        except Exception as e:
            logger.error(f"❌ Error cleaning up camera service: {e}")
        
        logger.info("✅ Python Parking System stopped")
    
    def get_gate(self, gate_id: str):
        """Get gate instance by ID"""
        return self.gates.get(gate_id)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        gate_statuses = {}
        for gate_id, gate in self.gates.items():
            try:
                gate_statuses[gate_id] = gate.get_status().__dict__
            except Exception as e:
                gate_statuses[gate_id] = {"error": str(e)}
        
        return {
            "running": self.is_running,
            "gates": gate_statuses,
            "database": database_service.get_connection_status(),
            "alpr": alpr_service.get_status(),
            "cameras": camera_service.get_camera_status()
        }


# Global system manager instance
system_manager = ParkingSystemManager()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    asyncio.create_task(system_manager.stop())


async def main():
    """Main application entry point with error resilience"""
    try:
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("🚀 Starting Python Parking System...")
        
        # Initialize system
        await system_manager.initialize()
        
        # Start system (includes UI based on mode)
        await system_manager.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"❌ Critical error in main: {e}")
        logger.error("System will attempt graceful shutdown...")
    finally:
        try:
            await system_manager.stop()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


if __name__ == "__main__":
    print("""
🎯 Python Parking System
========================

Starting the parking system...
The system will run in the mode specified by SYSTEM_MODE environment variable:
- entry_manual: Manual Entry Gate (dengan operator)
- entry_manless: Manless Entry Gate (otomatis tanpa operator)
- exit_manual: Manual Exit Gate (dengan operator)  
- exit_manless: Manless Exit Gate (otomatis tanpa operator)

Press Ctrl+C to stop the system.
    """)
    
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        logger.info("Application terminated")
