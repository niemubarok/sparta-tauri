"""
WebSocket server for gate communication
"""
import asyncio
import websockets
import json
import logging
from typing import Dict, Any, Set
import threading
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from config import Config
from database import DatabaseService
from camera import CameraService
from alpr.alpr_service import ALPRService

logger = logging.getLogger(__name__)

class WebSocketServer:
    def __init__(self, config: Config):
        self.config = config
        self.database = DatabaseService(config)
        self.camera = CameraService(config)
        self.alpr = ALPRService(config)
        
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.server = None
        
        host = config.get('WEBSOCKET', 'server_host', 'localhost')
        port = config.getint('WEBSOCKET', 'server_port', 8765)
        self.host = host
        self.port = port
    
    async def register_client(self, websocket, client_id: str):
        """Register a new client"""
        self.clients[client_id] = websocket
        logger.info(f"Client registered: {client_id}")
        
        # Send welcome message
        await self.send_to_client(client_id, {
            'type': 'welcome',
            'message': 'Connected to parking server',
            'client_id': client_id
        })
    
    async def unregister_client(self, client_id: str):
        """Unregister a client"""
        if client_id in self.clients:
            del self.clients[client_id]
            logger.info(f"Client unregistered: {client_id}")
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific client"""
        if client_id in self.clients:
            try:
                await self.clients[client_id].send(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {client_id}: {e}")
                await self.unregister_client(client_id)
    
    async def broadcast(self, message: Dict[str, Any], exclude_client: str = None):
        """Broadcast message to all clients"""
        if not self.clients:
            return
        
        disconnected_clients = []
        for client_id, websocket in self.clients.items():
            if client_id == exclude_client:
                continue
            
            try:
                await websocket.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send broadcast to {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Remove disconnected clients
        for client_id in disconnected_clients:
            await self.unregister_client(client_id)
    
    async def handle_alpr_request(self, client_id: str, message: Dict[str, Any]):
        """Handle ALPR processing request"""
        try:
            # Get image from camera or use provided image data
            image_data = None
            if 'image_data' in message:
                import base64
                image_data = base64.b64decode(message['image_data'])
            else:
                image_data = self.camera.capture_image()
            
            if not image_data:
                await self.send_to_client(client_id, {
                    'type': 'alpr_response',
                    'success': False,
                    'error': 'Failed to capture image'
                })
                return
            
            # Process with ALPR if enabled
            plate_data = None
            if self.alpr.is_enabled():
                plate_data = self.alpr.detect_plate_from_bytes(image_data)
            
            # Resize image for storage
            resized_image = self.camera.resize_image(image_data)
            
            response = {
                'type': 'alpr_response',
                'success': True,
                'plate_data': plate_data,
                'image_size': len(resized_image),
                'alpr_enabled': self.alpr.is_enabled()
            }
            
            # Store image data temporarily for transaction saving
            response['_image_data'] = resized_image
            
            await self.send_to_client(client_id, response)
            
        except Exception as e:
            logger.error(f"Error processing ALPR request: {e}")
            await self.send_to_client(client_id, {
                'type': 'alpr_response',
                'success': False,
                'error': str(e)
            })
    
    async def handle_save_transaction(self, client_id: str, message: Dict[str, Any]):
        """Handle transaction save request"""
        try:
            transaction_data = message.get('transaction_data', {})
            
            # Save transaction to database
            doc_id = self.database.save_transaction(transaction_data)
            
            await self.send_to_client(client_id, {
                'type': 'transaction_saved',
                'success': True,
                'transaction_id': doc_id
            })
            
            # Broadcast to admin clients for real-time updates
            await self.broadcast({
                'type': 'new_transaction',
                'transaction': transaction_data,
                'transaction_id': doc_id
            }, exclude_client=client_id)
            
        except Exception as e:
            logger.error(f"Error saving transaction: {e}")
            await self.send_to_client(client_id, {
                'type': 'transaction_saved',
                'success': False,
                'error': str(e)
            })
    
    async def handle_member_lookup(self, client_id: str, message: Dict[str, Any]):
        """Handle member lookup request"""
        try:
            plate_number = message.get('plate_number', '')
            member = self.database.get_member_by_plate(plate_number)
            
            await self.send_to_client(client_id, {
                'type': 'member_lookup_response',
                'success': True,
                'member': member,
                'is_member': member is not None
            })
            
        except Exception as e:
            logger.error(f"Error looking up member: {e}")
            await self.send_to_client(client_id, {
                'type': 'member_lookup_response',
                'success': False,
                'error': str(e)
            })
    
    async def handle_last_entry_lookup(self, client_id: str, message: Dict[str, Any]):
        """Handle last entry transaction lookup"""
        try:
            plate_number = message.get('plate_number', '')
            transaction = self.database.get_last_entry_transaction(plate_number)
            
            await self.send_to_client(client_id, {
                'type': 'last_entry_response',
                'success': True,
                'transaction': transaction,
                'has_entry': transaction is not None
            })
            
        except Exception as e:
            logger.error(f"Error looking up last entry: {e}")
            await self.send_to_client(client_id, {
                'type': 'last_entry_response',
                'success': False,
                'error': str(e)
            })
    
    async def handle_message(self, websocket, path):
        """Handle incoming WebSocket messages"""
        client_id = None
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type', '')
                    
                    if msg_type == 'register':
                        client_id = data.get('client_id', '')
                        await self.register_client(websocket, client_id)
                    
                    elif msg_type == 'alpr_request':
                        await self.handle_alpr_request(client_id, data)
                    
                    elif msg_type == 'save_transaction':
                        await self.handle_save_transaction(client_id, data)
                    
                    elif msg_type == 'member_lookup':
                        await self.handle_member_lookup(client_id, data)
                    
                    elif msg_type == 'last_entry_lookup':
                        await self.handle_last_entry_lookup(client_id, data)
                    
                    else:
                        logger.warning(f"Unknown message type: {msg_type}")
                
                except json.JSONDecodeError:
                    logger.error("Invalid JSON received")
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
        
        except websockets.exceptions.ConnectionClosedOK:
            logger.info(f"Client {client_id} disconnected normally")
        except Exception as e:
            logger.error(f"WebSocket error for client {client_id}: {e}")
        finally:
            if client_id:
                await self.unregister_client(client_id)
    
    async def start_server(self):
        """Start the WebSocket server"""
        try:
            self.server = await websockets.serve(
                self.handle_message,
                self.host,
                self.port
            )
            logger.info(f"WebSocket server started on {self.host}:{self.port}")
            
            # Keep server running
            await self.server.wait_closed()
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            raise
    
    def run(self):
        """Run the server"""
        asyncio.run(self.start_server())

def main():
    """Main function"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
    config = Config(config_file)
    
    # Start server
    server = WebSocketServer(config)
    try:
        logger.info("Starting parking system server...")
        server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == '__main__':
    main()
