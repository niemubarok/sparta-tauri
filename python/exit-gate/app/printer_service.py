"""
Exit Gate Printer Integration
Adds printing capability to exit gate system
"""
import sys
import os

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from printer import PrinterService
from config import Config
import logging

logger = logging.getLogger(__name__)

class ExitGatePrinter:
    def __init__(self):
        """Initialize exit gate printer"""
        try:
            self.config = Config()
            self.printer = PrinterService(self.config)
            logger.info("Exit gate printer service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize printer service: {e}")
            self.printer = None
    
    def print_receipt(self, transaction_data):
        """Print exit receipt"""
        try:
            if not self.printer:
                logger.warning("Printer service not available")
                return False
                
            success = self.printer.print_exit_receipt(transaction_data)
            if success:
                logger.info(f"Exit receipt printed for transaction {transaction_data.get('id', 'unknown')}")
            else:
                logger.warning("Exit receipt printing failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error printing receipt: {e}")
            return False
    
    def test_printer(self):
        """Test printer connection"""
        try:
            if not self.printer:
                return False
            return self.printer.test_printer()
        except Exception as e:
            logger.error(f"Printer test failed: {e}")
            return False

# Global printer instance
exit_printer = ExitGatePrinter()
