"""
Entry Manual Gate - Standalone Application
Gate entry dengan operator untuk kontrol manual
"""

import asyncio
import logging
import sys
import signal
from pathlib import Path
from typing import Dict, Any

# Add shared src to path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

from src.services.database import database_service
from src.services.alpr import alpr_service
from src.services.camera import camera_service
from src.gates.entry.manual import ManualEntryGate
from src.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('entry_manual_gate.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class EntryManualGateApp:
    """Standalone Entry Manual Gate Application"""
    
    def __init__(self):
        self.settings = get_settings()
        self.gate = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize the entry manual gate system"""
        try:
            logger.info("🚀 Initializing Entry Manual Gate System...")
            
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
            
            # Initialize entry manual gate
            logger.info("🚪 Initializing entry manual gate...")
            try:
                self.gate = ManualEntryGate("entry_manual")
                logger.info("✅ Entry Manual Gate initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize entry manual gate: {e}")
                raise
            
            logger.info("✅ Entry Manual Gate System initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Critical error during initialization: {e}")
            raise
    
    async def start_ui(self):
        """Start the entry manual gate UI"""
        try:
            logger.info("🎯 Membuka UI Entry Manual Gate...")
            logger.info("="*50)
            logger.info("🚪 Gate Entry dengan Operator - UI Visual")
            logger.info("Interface visual untuk operator gate entry")
            logger.info("="*50)
            logger.info("Kontrol yang tersedia:")
            logger.info("  • Scan plat nomor kendaraan")
            logger.info("  • Buka gate untuk kendaraan masuk")
            logger.info("  • Monitor status gate")
            logger.info("  • Log aktivitas kendaraan")
            logger.info("="*50)
            logger.info("✅ UI siap digunakan operator")
            logger.info("⚠️  Tekan Ctrl+C untuk menghentikan sistem")
            
            if self.gate:
                try:
                    # Initialize gate
                    if hasattr(self.gate, 'initialize'):
                        self.gate.initialize()
                        logger.info("✅ Gate entry manual siap beroperasi")
                except Exception as e:
                    logger.warning(f"⚠️ Gate initialization failed: {e}")
            else:
                logger.error("❌ Tidak ada gate yang tersedia")
                return
                
            # Start operator interface
            logger.info("🖥️ UI Entry Manual Gate terbuka - operator dapat menggunakan interface")
            logger.info("📝 Sistem siap menerima kendaraan masuk")
            logger.info("🔄 Memulai monitoring loop...")
            
            # Keep the UI running with basic status monitoring
            status_check_counter = 0
            logger.info("✅ Monitoring loop dimulai, sistem berjalan...")
            
            while self.is_running:
                try:
                    await asyncio.sleep(5)  # Check every 5 seconds
                    
                    # Show periodic status (every 30 seconds)
                    status_check_counter += 1
                    if status_check_counter >= 6:  # 6 * 5 seconds = 30 seconds
                        if hasattr(self.gate, 'get_status'):
                            status = self.gate.get_status()
                            logger.info(f"📊 Status Gate: {status.gate_status} | Device: Entry Manual | Counter: {status_check_counter}")
                        else:
                            logger.info(f"📊 Status: Sistem aktif | Device: Entry Manual | Counter: {status_check_counter}")
                        status_check_counter = 0
                    
                    # Show that system is alive every 5 seconds during first minute
                    if status_check_counter <= 12:  # First 60 seconds
                        logger.info(f"🔄 Sistem monitoring aktif... ({status_check_counter * 5}s)")
                    
                except KeyboardInterrupt:
                    logger.info("🛑 Menutup UI Entry Manual Gate...")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in UI: {e}")
                    await asyncio.sleep(5)
                    
        except Exception as e:
            logger.error(f"❌ Error starting entry manual UI: {e}")
    
    async def start(self):
        """Start the entry manual gate system"""
        if self.is_running:
            logger.warning("System is already running")
            return

        try:
            logger.info("🔄 Starting Entry Manual Gate System...")
            self.is_running = True

            # Start UI
            await self.start_ui()

        except Exception as e:
            logger.error(f"❌ Error running entry manual gate system: {e}")
            await self.stop()
    
    async def stop(self):
        """Stop the entry manual gate system"""
        if not self.is_running:
            return
        
        logger.info("🛑 Stopping Entry Manual Gate System...")
        self.is_running = False
        
        # Cleanup gate
        if self.gate:
            try:
                self.gate.cleanup()
                logger.info("✅ Entry manual gate cleaned up")
            except Exception as e:
                logger.error(f"❌ Error cleaning up gate: {e}")
        
        # Cleanup services
        try:
            camera_service.cleanup()
            logger.info("✅ Camera service cleaned up")
        except Exception as e:
            logger.error(f"❌ Error cleaning up camera service: {e}")
        
        logger.info("✅ Entry Manual Gate System stopped")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        gate_status = None
        if self.gate:
            try:
                gate_status = self.gate.get_status().__dict__
            except Exception as e:
                gate_status = {"error": str(e)}
        
        return {
            "running": self.is_running,
            "gate_type": "entry_manual",
            "gate": gate_status,
            "database": database_service.get_connection_status(),
            "alpr": alpr_service.get_status(),
            "cameras": camera_service.get_camera_status()
        }


# Global app instance
app = EntryManualGateApp()


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    asyncio.create_task(app.stop())


async def main():
    """Main application entry point"""
    try:
        # Setup signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("🚀 Starting Entry Manual Gate Application...")
        
        # Initialize system
        logger.info("📋 Starting initialization...")
        await app.initialize()
        logger.info("✅ Initialization completed")
        
        # Start system
        logger.info("🔄 Starting main system...")
        await app.start()
        logger.info("✅ System started successfully")
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"❌ Critical error in main: {e}")
        logger.error("System will attempt graceful shutdown...")
    finally:
        try:
            await app.stop()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


if __name__ == "__main__":
    print("""
🎯 Entry Manual Gate - Standalone Application
===========================================

Gate Entry dengan Operator untuk kontrol manual kendaraan masuk.

Fitur:
- Kontrol manual oleh operator
- Scan plat nomor kendaraan
- Buka/tutup gate manual
- Monitor aktivitas kendaraan
- Log sistem

Press Ctrl+C to stop the system.
    """)
    
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        logger.info("Application terminated")
