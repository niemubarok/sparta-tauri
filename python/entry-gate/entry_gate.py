"""
Entry Gate Application
"""
import asyncio
import websockets
import json
import logging
import sys
import os
import threading
import time
from datetime import datetime

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from config import Config
from gpio import GPIOService
from audio import AudioService
from printer import PrinterService

logger = logging.getLogger(__name__)

class EntryGateController:
    def __init__(self, config_file: str = None):
        self.config = Config(config_file)
        self.gpio = GPIOService(self.config)
        self.audio = AudioService(self.config)
        self.printer = PrinterService(self.config)
        
        self.websocket = None
        self.client_id = self.config.get('WEBSOCKET', 'entry_gate_id', 'entry_gate_01')
        self.server_url = f"ws://{self.config.get('WEBSOCKET', 'server_host')}:{self.config.get('WEBSOCKET', 'server_port')}"
        
        self.processing = False
        self.running = True
        
        logger.info("Entry Gate Controller initialized")
    
    async def connect_to_server(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            
            # Register with server
            await self.websocket.send(json.dumps({
                'type': 'register',
                'client_id': self.client_id
            }))
            
            logger.info(f"Connected to server at {self.server_url}")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to server: {e}")
            # Don't raise exception, just return False
            self.websocket = None
            return False
    
    async def send_message(self, message: dict):
        """Send message to server"""
        try:
            if self.websocket:
                await self.websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    
    async def handle_server_messages(self):
        """Handle incoming messages from server"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type', '')
                    
                    if msg_type == 'welcome':
                        logger.info(f"Server welcome: {data.get('message', '')}")
                    
                    elif msg_type == 'alpr_response':
                        await self.handle_alpr_response(data)
                    
                    elif msg_type == 'member_lookup_response':
                        await self.handle_member_lookup_response(data)
                    
                    elif msg_type == 'transaction_saved':
                        logger.info(f"Transaction saved: {data.get('transaction_id', '')}")
                    
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received from server")
                except Exception as e:
                    logger.error(f"Error handling server message: {e}")
        
        except websockets.exceptions.ConnectionClosedOK:
            logger.info("Server connection closed")
        except Exception as e:
            logger.error(f"Server communication error: {e}")
    
    async def handle_alpr_response(self, data: dict):
        """Handle ALPR response from server"""
        if not data.get('success', False):
            logger.error(f"ALPR failed: {data.get('error', 'Unknown error')}")
            # Continue with non-member flow
            await self.process_non_member_entry()
            return
        
        plate_data = data.get('plate_data')
        alpr_enabled = data.get('alpr_enabled', False)
        
        if not alpr_enabled or not plate_data:
            # ALPR disabled or no plate detected - treat as non-member
            await self.process_non_member_entry()
        else:
            # ALPR enabled and plate detected
            plate_number = plate_data.get('plate_number', '')
            logger.info(f"Plate detected: {plate_number}")
            
            # Check if member
            await self.send_message({
                'type': 'member_lookup',
                'plate_number': plate_number
            })
            
            # Store plate data for later use
            self.current_plate_data = plate_data
    
    async def handle_member_lookup_response(self, data: dict):
        """Handle member lookup response"""
        if not data.get('success', False):
            logger.error(f"Member lookup failed: {data.get('error', 'Unknown error')}")
            await self.process_non_member_entry()
            return
        
        is_member = data.get('is_member', False)
        member_data = data.get('member', {})
        
        if is_member:
            logger.info(f"Member detected: {member_data.get('name', 'Unknown')}")
            await self.process_member_entry(member_data)
        else:
            logger.info("Non-member vehicle")
            await self.process_non_member_entry()
    
    async def process_member_entry(self, member_data: dict):
        """Process member entry"""
        try:
            # Save member entry transaction
            transaction_data = {
                'type': 'member_entry',
                'plate_number': self.current_plate_data.get('plate_number', ''),
                'member_id': member_data.get('_id', ''),
                'member_name': member_data.get('name', ''),
                'confidence': self.current_plate_data.get('confidence', 0),
                'entry_time': datetime.now().isoformat(),
                'gate_id': self.client_id
            }
            
            await self.send_message({
                'type': 'save_transaction',
                'transaction_data': transaction_data
            })
            
            # Print entry ticket
            try:
                self.printer.print_ticket(transaction_data)
                logger.info("Entry ticket printed successfully")
            except Exception as print_error:
                logger.error(f"Failed to print ticket: {print_error}")
            
            # Open gate
            logger.info("Opening gate for member")
            self.gpio.open_gate()
            
            # Play thank you message
            self.audio.speak_text("Terima Kasih silahkan masuk")
            self.audio.play_goodbye()
            
        except Exception as e:
            logger.error(f"Error processing member entry: {e}")
        finally:
            self.processing = False
    
    async def process_non_member_entry(self):
        """Process non-member entry"""
        try:
            # Save non-member entry transaction
            transaction_data = {
                'type': 'non_member_entry',
                'entry_time': datetime.now().isoformat(),
                'gate_id': self.client_id
            }
            
            # Add plate data if available
            if hasattr(self, 'current_plate_data') and self.current_plate_data:
                transaction_data.update({
                    'plate_number': self.current_plate_data.get('plate_number', ''),
                    'confidence': self.current_plate_data.get('confidence', 0)
                })
            
            await self.send_message({
                'type': 'save_transaction',
                'transaction_data': transaction_data
            })
            
            # Print entry ticket
            try:
                self.printer.print_ticket(transaction_data)
                logger.info("Non-member entry ticket printed successfully")
            except Exception as print_error:
                logger.error(f"Failed to print ticket: {print_error}")
            
            # Open gate
            logger.info("Opening gate for non-member")
            self.gpio.open_gate()
            
            # Play instruction
            self.audio.speak_text("Silahkan masuk, jangan lupa bayar di kasir")
            
        except Exception as e:
            logger.error(f"Error processing non-member entry: {e}")
        finally:
            self.processing = False
    
    def on_loop1_triggered(self):
        """Handle loop1 trigger - vehicle approaching"""
        logger.info("Vehicle approaching entry gate")
        # Just log for now, main processing happens on loop2
    
    def on_loop2_triggered(self):
        """Handle loop2 trigger - vehicle positioned"""
        if self.processing:
            logger.info("Already processing a vehicle, ignoring trigger")
            return
        
        logger.info("Vehicle positioned at entry gate")
        self.processing = True
        
        # Play welcome message
        self.audio.speak_text("Selamat Datang silahkan tempelkan kartu atau tekan tombol")
        self.audio.play_welcome()
        
        # Start ALPR processing - handle async properly
        try:
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                # If loop is running, create task
                asyncio.create_task(self.start_alpr_processing())
            except RuntimeError:
                # No running loop, use thread
                threading.Thread(target=self._start_alpr_processing_sync, daemon=True).start()
        except Exception as e:
            logger.error(f"Error starting ALPR: {e}")
            threading.Thread(target=self._start_alpr_processing_sync, daemon=True).start()
    
    async def start_alpr_processing(self):
        """Start ALPR processing"""
        try:
            # Request ALPR processing from server
            await self.send_message({
                'type': 'alpr_request',
                'gate_id': self.client_id
            })
        except Exception as e:
            logger.error(f"Error starting ALPR processing: {e}")
            # Fallback to non-member processing
            await self.process_non_member_entry()
    
    def _start_alpr_processing_sync(self):
        """Synchronous wrapper for ALPR processing"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Run the async function
            loop.run_until_complete(self._alpr_processing_thread())
        except Exception as e:
            logger.error(f"Error in ALPR processing thread: {e}")
            # Fallback to non-member processing
            self._process_non_member_entry_sync()
        finally:
            self.processing = False
    
    async def _alpr_processing_thread(self):
        """ALPR processing in separate thread"""
        try:
            # Connect to server if not connected
            if not self.websocket:
                await self.connect_to_server()
            
            if self.websocket:
                await self.start_alpr_processing()
            else:
                # No server connection, process as non-member
                await self.process_non_member_entry()
        except Exception as e:
            logger.error(f"Error in ALPR thread: {e}")
            await self.process_non_member_entry()
    
    def _process_non_member_entry_sync(self):
        """Synchronous non-member processing"""
        try:
            logger.info("Processing non-member entry (sync)")
            
            # Print ticket
            self.gpio.print_ticket()
            
            # Open gate
            self.gpio.open_gate()
            
            # Play thank you message
            self.audio.speak_text("Terima Kasih silahkan masuk")
            self.audio.play_goodbye()
            
        except Exception as e:
            logger.error(f"Error processing non-member entry: {e}")
        finally:
            self.processing = False
    
    def setup_gpio_callbacks(self):
        """Setup GPIO callbacks"""
        self.gpio.setup_loop_detection(
            loop1_callback=self.on_loop1_triggered,
            loop2_callback=self.on_loop2_triggered
        )
    
    async def run(self):
        """Main run loop"""
        logger.info("Starting Entry Gate application")
        
        # Setup GPIO callbacks
        self.setup_gpio_callbacks()
        
        # Try to connect to server (optional)
        connection_attempts = 3
        for attempt in range(connection_attempts):
            if await self.connect_to_server():
                break
            if attempt < connection_attempts - 1:
                logger.warning(f"Retrying connection in 2 seconds... (attempt {attempt + 1}/{connection_attempts})")
                await asyncio.sleep(2)
        
        if not self.websocket:
            logger.warning("Running in standalone mode without server connection")
        
        try:
            if self.websocket:
                # Handle server messages
                await self.handle_server_messages()
            else:
                # Run without server - just keep alive
                logger.info("Entry gate running in standalone mode")
                while self.running:
                    await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Entry Gate application")
        self.running = False
        self.gpio.cleanup()
        self.audio.cleanup()
    
    def simulate_vehicle_entry(self):
        """Simulate vehicle entry for testing"""
        logger.info("SIMULATION: Vehicle entry triggered")
        # Use the sync version to avoid event loop issues
        self.on_loop2_triggered()

def main():
    """Main function"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
    
    # Create controller
    controller = EntryGateController(config_file)
    
    try:
        # For simulation mode, add test commands
        if controller.gpio.simulation_mode:
            def test_thread():
                time.sleep(10)  # Wait for startup
                logger.info("Starting simulation test...")
                controller.simulate_vehicle_entry()
            
            threading.Thread(target=test_thread, daemon=True).start()
        
        # Run controller
        asyncio.run(controller.run())
    except KeyboardInterrupt:
        logger.info("Entry Gate stopped by user")
        controller.cleanup()
    except Exception as e:
        logger.error(f"Entry Gate error: {e}")
        controller.cleanup()

if __name__ == '__main__':
    main()
