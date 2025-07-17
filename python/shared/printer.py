"""
Printer service for ESC/POS thermal printer
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import socket
import struct

logger = logging.getLogger(__name__)

class PrinterService:
    def __init__(self, config):
        self.config = config
        self.printer_ip = config.get('PRINTER', 'ip', fallback='192.168.1.200')
        self.printer_port = config.getint('PRINTER', 'port', fallback=9100)
        self.printer_enabled = config.getboolean('PRINTER', 'enabled', fallback=True)
        
        # ESC/POS Commands
        self.ESC = b'\x1b'
        self.INIT = b'\x1b\x40'  # Initialize printer
        self.CUT = b'\x1d\x56\x42\x00'  # Full cut
        self.ALIGN_CENTER = b'\x1b\x61\x01'
        self.ALIGN_LEFT = b'\x1b\x61\x00'
        self.BOLD_ON = b'\x1b\x45\x01'
        self.BOLD_OFF = b'\x1b\x45\x00'
        self.DOUBLE_HEIGHT = b'\x1d\x21\x01'
        self.NORMAL_SIZE = b'\x1d\x21\x00'
        self.FEED_LINE = b'\x0a'
        
    def print_ticket(self, transaction_data: Dict[str, Any]) -> bool:
        """Print parking ticket"""
        try:
            if not self.printer_enabled:
                logger.info("Printer disabled - simulating ticket print")
                self._simulate_ticket_print(transaction_data)
                return True
                
            # Generate ticket content
            ticket_content = self._generate_ticket_content(transaction_data)
            
            # Send to printer
            return self._send_to_printer(ticket_content)
            
        except Exception as e:
            logger.error(f"Failed to print ticket: {e}")
            # Fallback to simulation
            self._simulate_ticket_print(transaction_data)
            return False
    
    def print_exit_receipt(self, transaction_data: Dict[str, Any]) -> bool:
        """Print exit receipt with payment details"""
        try:
            if not self.printer_enabled:
                logger.info("Printer disabled - simulating receipt print")
                self._simulate_receipt_print(transaction_data)
                return True
                
            # Generate receipt content
            receipt_content = self._generate_receipt_content(transaction_data)
            
            # Send to printer
            return self._send_to_printer(receipt_content)
            
        except Exception as e:
            logger.error(f"Failed to print receipt: {e}")
            # Fallback to simulation
            self._simulate_receipt_print(transaction_data)
            return False
    
    def _generate_ticket_content(self, transaction_data: Dict[str, Any]) -> bytes:
        """Generate parking ticket content"""
        ticket = b''
        
        # Initialize printer
        ticket += self.INIT
        
        # Header - Center aligned
        ticket += self.ALIGN_CENTER
        ticket += self.DOUBLE_HEIGHT + self.BOLD_ON
        ticket += "PARKING TICKET".encode('utf-8') + self.FEED_LINE
        ticket += self.NORMAL_SIZE + self.BOLD_OFF
        ticket += "=" * 32 + self.FEED_LINE.encode('utf-8')
        
        # Transaction details - Left aligned
        ticket += self.ALIGN_LEFT
        ticket += self.FEED_LINE
        
        # Ticket number
        ticket_id = transaction_data.get('id', 'N/A')
        ticket += f"Ticket No: {ticket_id}".encode('utf-8') + self.FEED_LINE
        
        # Entry time
        entry_time = transaction_data.get('waktu_masuk', datetime.now().isoformat())
        formatted_time = datetime.fromisoformat(entry_time.replace('Z', '')).strftime('%d/%m/%Y %H:%M:%S')
        ticket += f"Entry Time: {formatted_time}".encode('utf-8') + self.FEED_LINE
        
        # Plate number (if available)
        if transaction_data.get('no_pol'):
            ticket += f"Plate: {transaction_data['no_pol']}".encode('utf-8') + self.FEED_LINE
        
        # Vehicle type
        vehicle_types = {1: 'Motorcycle', 2: 'Car', 3: 'Truck', 4: 'Bus'}
        vehicle_type = vehicle_types.get(transaction_data.get('id_kendaraan', 2), 'Car')
        ticket += f"Vehicle: {vehicle_type}".encode('utf-8') + self.FEED_LINE
        
        # Gate info
        gate_id = transaction_data.get('id_pintu_masuk', 'ENTRY_GATE_01')
        ticket += f"Gate: {gate_id}".encode('utf-8') + self.FEED_LINE
        
        # Entry fee
        entry_fee = transaction_data.get('bayar_masuk', 0)
        ticket += f"Entry Fee: Rp {entry_fee:,}".encode('utf-8') + self.FEED_LINE
        
        # Separator
        ticket += self.FEED_LINE
        ticket += "-" * 32 + self.FEED_LINE.encode('utf-8')
        
        # Instructions - Center aligned
        ticket += self.ALIGN_CENTER
        ticket += "KEEP THIS TICKET".encode('utf-8') + self.FEED_LINE
        ticket += "Present at exit".encode('utf-8') + self.FEED_LINE
        ticket += self.FEED_LINE
        
        # QR Code placeholder (if printer supports)
        ticket += f"ID: {ticket_id}".encode('utf-8') + self.FEED_LINE
        
        # Footer
        ticket += self.FEED_LINE
        ticket += "Thank you for parking".encode('utf-8') + self.FEED_LINE
        ticket += "with us!".encode('utf-8') + self.FEED_LINE
        
        # Cut paper
        ticket += self.FEED_LINE * 3
        ticket += self.CUT
        
        return ticket
    
    def _generate_receipt_content(self, transaction_data: Dict[str, Any]) -> bytes:
        """Generate exit receipt content"""
        receipt = b''
        
        # Initialize printer
        receipt += self.INIT
        
        # Header - Center aligned
        receipt += self.ALIGN_CENTER
        receipt += self.DOUBLE_HEIGHT + self.BOLD_ON
        receipt += "PARKING RECEIPT".encode('utf-8') + self.FEED_LINE
        receipt += self.NORMAL_SIZE + self.BOLD_OFF
        receipt += "=" * 32 + self.FEED_LINE.encode('utf-8')
        
        # Transaction details - Left aligned
        receipt += self.ALIGN_LEFT
        receipt += self.FEED_LINE
        
        # Ticket number
        ticket_id = transaction_data.get('id', 'N/A')
        receipt += f"Ticket No: {ticket_id}".encode('utf-8') + self.FEED_LINE
        
        # Entry time
        entry_time = transaction_data.get('waktu_masuk')
        if entry_time:
            formatted_entry = datetime.fromisoformat(entry_time.replace('Z', '')).strftime('%d/%m/%Y %H:%M:%S')
            receipt += f"Entry: {formatted_entry}".encode('utf-8') + self.FEED_LINE
        
        # Exit time
        exit_time = transaction_data.get('waktu_keluar', datetime.now().isoformat())
        formatted_exit = datetime.fromisoformat(exit_time.replace('Z', '')).strftime('%d/%m/%Y %H:%M:%S')
        receipt += f"Exit: {formatted_exit}".encode('utf-8') + self.FEED_LINE
        
        # Calculate duration
        if entry_time:
            try:
                entry_dt = datetime.fromisoformat(entry_time.replace('Z', ''))
                exit_dt = datetime.fromisoformat(exit_time.replace('Z', ''))
                duration = exit_dt - entry_dt
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)
                receipt += f"Duration: {hours}h {minutes}m".encode('utf-8') + self.FEED_LINE
            except:
                pass
        
        # Plate number
        if transaction_data.get('no_pol'):
            receipt += f"Plate: {transaction_data['no_pol']}".encode('utf-8') + self.FEED_LINE
        
        # Payment details
        receipt += self.FEED_LINE
        receipt += "PAYMENT DETAILS".encode('utf-8') + self.FEED_LINE
        receipt += "-" * 20 + self.FEED_LINE.encode('utf-8')
        
        entry_fee = transaction_data.get('bayar_masuk', 0)
        exit_fee = transaction_data.get('bayar_keluar', 0)
        total_fee = entry_fee + exit_fee
        
        receipt += f"Entry Fee: Rp {entry_fee:,}".encode('utf-8') + self.FEED_LINE
        receipt += f"Exit Fee:  Rp {exit_fee:,}".encode('utf-8') + self.FEED_LINE
        receipt += "-" * 20 + self.FEED_LINE.encode('utf-8')
        receipt += self.BOLD_ON
        receipt += f"TOTAL:     Rp {total_fee:,}".encode('utf-8') + self.FEED_LINE
        receipt += self.BOLD_OFF
        
        # Payment method
        exit_method = transaction_data.get('exit_method', 'cash')
        receipt += f"Method: {exit_method.upper()}".encode('utf-8') + self.FEED_LINE
        
        # Footer - Center aligned
        receipt += self.FEED_LINE
        receipt += self.ALIGN_CENTER
        receipt += "Thank you for parking".encode('utf-8') + self.FEED_LINE
        receipt += "Drive safely!".encode('utf-8') + self.FEED_LINE
        
        # Cut paper
        receipt += self.FEED_LINE * 3
        receipt += self.CUT
        
        return receipt
    
    def _send_to_printer(self, content: bytes) -> bool:
        """Send content to ESC/POS printer via network"""
        try:
            # Create socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 second timeout
            
            # Connect to printer
            sock.connect((self.printer_ip, self.printer_port))
            
            # Send data
            sock.sendall(content)
            
            # Close connection
            sock.close()
            
            logger.info(f"Successfully sent print job to {self.printer_ip}:{self.printer_port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send to printer {self.printer_ip}:{self.printer_port}: {e}")
            return False
    
    def _simulate_ticket_print(self, transaction_data: Dict[str, Any]):
        """Simulate ticket printing for testing"""
        ticket_id = transaction_data.get('id', 'SIM123456')
        entry_time = transaction_data.get('waktu_masuk', datetime.now().isoformat())
        formatted_time = datetime.fromisoformat(entry_time.replace('Z', '')).strftime('%d/%m/%Y %H:%M:%S')
        
        print("\\n" + "="*40)
        print("         PARKING TICKET")
        print("="*40)
        print(f"Ticket No: {ticket_id}")
        print(f"Entry Time: {formatted_time}")
        if transaction_data.get('no_pol'):
            print(f"Plate: {transaction_data['no_pol']}")
        
        vehicle_types = {1: 'Motorcycle', 2: 'Car', 3: 'Truck', 4: 'Bus'}
        vehicle_type = vehicle_types.get(transaction_data.get('id_kendaraan', 2), 'Car')
        print(f"Vehicle: {vehicle_type}")
        
        entry_fee = transaction_data.get('bayar_masuk', 0)
        print(f"Entry Fee: Rp {entry_fee:,}")
        print("-"*40)
        print("      KEEP THIS TICKET")
        print("      Present at exit")
        print("="*40)
        
        logger.info(f"SIMULATION: Parking ticket printed for {ticket_id}")
    
    def _simulate_receipt_print(self, transaction_data: Dict[str, Any]):
        """Simulate receipt printing for testing"""
        ticket_id = transaction_data.get('id', 'SIM123456')
        exit_time = transaction_data.get('waktu_keluar', datetime.now().isoformat())
        formatted_time = datetime.fromisoformat(exit_time.replace('Z', '')).strftime('%d/%m/%Y %H:%M:%S')
        
        entry_fee = transaction_data.get('bayar_masuk', 0)
        exit_fee = transaction_data.get('bayar_keluar', 0)
        total_fee = entry_fee + exit_fee
        
        print("\\n" + "="*40)
        print("        PARKING RECEIPT")
        print("="*40)
        print(f"Ticket No: {ticket_id}")
        print(f"Exit Time: {formatted_time}")
        if transaction_data.get('no_pol'):
            print(f"Plate: {transaction_data['no_pol']}")
        print()
        print("PAYMENT DETAILS")
        print("-"*20)
        print(f"Entry Fee: Rp {entry_fee:,}")
        print(f"Exit Fee:  Rp {exit_fee:,}")
        print("-"*20)
        print(f"TOTAL:     Rp {total_fee:,}")
        print("="*40)
        print("    Thank you for parking")
        print("        Drive safely!")
        print("="*40)
        
        logger.info(f"SIMULATION: Exit receipt printed for {ticket_id}")
    
    def test_printer(self) -> bool:
        """Test printer connection"""
        try:
            if not self.printer_enabled:
                logger.info("Printer disabled - test simulation")
                print("\\n" + "="*30)
                print("    PRINTER TEST")
                print("="*30)
                print("Date:", datetime.now().strftime('%d/%m/%Y %H:%M:%S'))
                print("Status: OK (Simulation)")
                print("="*30)
                return True
                
            # Send test page
            test_content = self.INIT
            test_content += self.ALIGN_CENTER
            test_content += self.BOLD_ON
            test_content += "PRINTER TEST".encode('utf-8') + self.FEED_LINE
            test_content += self.BOLD_OFF
            test_content += datetime.now().strftime('%d/%m/%Y %H:%M:%S').encode('utf-8') + self.FEED_LINE
            test_content += "Status: OK".encode('utf-8') + self.FEED_LINE
            test_content += self.FEED_LINE * 3
            test_content += self.CUT
            
            return self._send_to_printer(test_content)
            
        except Exception as e:
            logger.error(f"Printer test failed: {e}")
            return False
