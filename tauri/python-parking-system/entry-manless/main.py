"""
Entry Manless Gate - Standalone Application
Gate entry otomatis tanpa operator
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
from src.gates.entry.manless import ManlessEntryGate
from src.core.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('entry_manless_gate.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class EntryManlessGateApp:
    """Standalone Entry Manless Gate Application"""
    
    def __init__(self):
        self.settings = get_settings()
        self.gate = None
        self.is_running = False
        
    async def initialize(self):
        """Initialize the entry manless gate system"""
        try:
            logger.info("🚀 Initializing Entry Manless Gate System...")
            
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
            
            # Initialize entry manless gate
            try:
                self.gate = ManlessEntryGate("entry_manless")
                logger.info("✅ Entry Manless Gate initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize entry manless gate: {e}")
                raise
            
            logger.info("✅ Entry Manless Gate System initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Critical error during initialization: {e}")
            raise
    
    async def start_automatic_system(self):
        """Start the entry manless gate automatic system"""
        try:
            logger.info("🤖 Memulai Sistem Entry Manless Gate...")
            logger.info("="*50)
            logger.info("🚀 Gate Entry Otomatis - Tanpa Operator")
            logger.info("Sistem otomatis untuk kendaraan masuk")
            logger.info("="*50)
            logger.info("Fitur otomatis:")
            logger.info("  • Deteksi kendaraan secara otomatis")
            logger.info("  • Scan plat nomor otomatis")
            logger.info("  • Buka/tutup gate otomatis")
            logger.info("  • Monitoring 24/7")
            logger.info("  • Log aktivitas otomatis")
            logger.info("="*50)
            logger.info("✅ Sistem siap beroperasi otomatis")
            logger.info("⚠️  Tekan Ctrl+C untuk menghentikan sistem")
            
            if self.gate:
                try:
                    # Initialize gate
                    if hasattr(self.gate, 'initialize'):
                        self.gate.initialize()
                        logger.info("✅ Gate entry manless siap beroperasi")
                        
                    # Start monitoring
                    if hasattr(self.gate, 'start_monitoring'):
                        self.gate.start_monitoring()
                        logger.info("🔄 Monitoring otomatis dimulai...")
                except Exception as e:
                    logger.warning(f"⚠️ Gate initialization failed: {e}")
            else:
                logger.error("❌ Tidak ada gate yang tersedia")
                return
                
            # Auto-monitoring loop
            logger.info("🤖 Sistem entry manless aktif - monitoring...")
            logger.info("📡 Menunggu kendaraan masuk...")
            logger.info("🔄 Memulai automatic monitoring loop...")
            
            monitoring_counter = 0
            logger.info("✅ Monitoring loop dimulai, sistem berjalan...")
            
            while self.is_running:
                try:
                    await asyncio.sleep(3)  # Check every 3 seconds
                    
                    # Show periodic monitoring status (every 30 seconds)
                    monitoring_counter += 1
                    if monitoring_counter >= 10:  # 10 * 3 seconds = 30 seconds
                        if hasattr(self.gate, 'get_status'):
                            status = self.gate.get_status()
                            logger.info(f"🤖 Auto-Monitor: {status.gate_status} | Device: Entry Manless | Waktu: {status.last_scan_time or 'Belum ada scan'}")
                        else:
                            logger.info(f"🤖 Auto-Monitor: Sistem aktif | Device: Entry Manless")
                        monitoring_counter = 0
                    
                    # Show that system is alive every 3 seconds during first minute
                    if monitoring_counter <= 20:  # First 60 seconds
                        logger.info(f"🔄 Auto-monitoring aktif... ({monitoring_counter * 3}s)")
                    
                    # In a real implementation, this would be handled by the gate's automatic monitoring
                    # For now, just show that the system is running and ready
                    
                except KeyboardInterrupt:
                    logger.info("🛑 Received interrupt signal, shutting down...")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in monitoring loop: {e}")
                    await asyncio.sleep(5)  # Wait before retrying
                    
        except Exception as e:
            logger.error(f"❌ Error in entry manless system: {e}")
    
    async def start(self):
        """Start the entry manless gate system"""
        if self.is_running:
            logger.warning("System is already running")
            return

        try:
            logger.info("🔄 Starting Entry Manless Gate System...")
            self.is_running = True

            # Start automatic system
            await self.start_automatic_system()

        except Exception as e:
            logger.error(f"❌ Error running entry manless gate system: {e}")
            await self.stop()
    
    async def stop(self):
        """Stop the entry manless gate system"""
        if not self.is_running:
            return
        
        logger.info("🛑 Stopping Entry Manless Gate System...")
        self.is_running = False
        
        # Cleanup gate
        if self.gate:
            try:
                self.gate.cleanup()
                logger.info("✅ Entry manless gate cleaned up")
            except Exception as e:
                logger.error(f"❌ Error cleaning up gate: {e}")
        
        # Cleanup services
        try:
            camera_service.cleanup()
            logger.info("✅ Camera service cleaned up")
        except Exception as e:
            logger.error(f"❌ Error cleaning up camera service: {e}")
        
        logger.info("✅ Entry Manless Gate System stopped")
    
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
            "gate_type": "entry_manless",
            "gate": gate_status,
            "database": database_service.get_connection_status(),
            "alpr": alpr_service.get_status(),
            "cameras": camera_service.get_camera_status()
        }


# Global app instance
app = EntryManlessGateApp()


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
        
        logger.info("🚀 Starting Entry Manless Gate Application...")
        
        # Initialize system
        await app.initialize()
        
        # Start system
        await app.start()
        
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
🤖 Entry Manless Gate - Standalone Application
============================================

Gate Entry Otomatis tanpa operator untuk kendaraan masuk.

Fitur:
- Deteksi kendaraan otomatis
- Scan plat nomor otomatis dengan ALPR
- Buka/tutup gate otomatis
- Monitoring 24/7
- Log aktivitas otomatis

Press Ctrl+C to stop the system.
    """)
    
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        logger.info("Application terminated")
