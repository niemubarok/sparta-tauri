"""
Database service for CouchDB
"""
import couchdb
import base64
import datetime
import logging
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, config):
        self.config = config
        self.server = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Connect to CouchDB"""
        try:
            username = self.config.get('DATABASE', 'username')
            password = self.config.get('DATABASE', 'password')
            host = self.config.get('DATABASE', 'host')
            port = self.config.getint('DATABASE', 'port')
            
            url = f"http://{username}:{password}@{host}:{port}/"
            self.server = couchdb.Server(url)
            
            db_name = self.config.get('DATABASE', 'database')
            if db_name in self.server:
                self.db = self.server[db_name]
            else:
                self.db = self.server.create(db_name)
                logger.info(f"Created database: {db_name}")
            
            logger.info("Connected to CouchDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to CouchDB: {e}")
            raise
    
    def test_connection(self):
        """Test database connection"""
        try:
            # Try to get database info
            if self.db is not None:
                info = self.db.info()
                logger.info(f"Database connection OK: {info.get('db_name', 'unknown')}")
                return True
            else:
                raise Exception("Database not initialized")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise
    
    def save_transaction(self, transaction_data: Dict[str, Any], entry_image: bytes = None, exit_image: bytes = None) -> str:
        """Save transaction with structure matching the provided format"""
        try:
            import time
            import uuid
            
            # Generate unique transaction ID
            transaction_id = str(int(time.time() * 1000000))  # Microsecond timestamp
            
            # Get current datetime
            now = datetime.datetime.now()
            iso_time = now.isoformat() + "Z"
            date_str = now.strftime("%Y-%m-%d")
            
            # Build transaction structure according to the provided format
            structured_transaction = {
                "_id": f"transaction_{transaction_id}",
                "id": transaction_id,
                "no_pol": transaction_data.get("license_plate", ""),
                "id_kendaraan": self._get_vehicle_type_id(transaction_data.get("vehicle_type", "Car")),
                "status": 1,  # Active
                "id_pintu_masuk": transaction_data.get("gate_id", "ENTRY_GATE_01"),
                "waktu_masuk": iso_time,
                "id_op_masuk": transaction_data.get("operator_id", "SYSTEM"),
                "id_shift_masuk": transaction_data.get("shift_id", "S1"),
                "kategori": "MEMBER" if transaction_data.get("is_member", False) else "UMUM",
                "status_transaksi": "1",  # Active transaction
                "jenis_system": transaction_data.get("system_type", "PREPAID"),
                "tanggal": date_str,
                "sinkron": 0,
                "upload": 0,
                "manual": 0,
                "veri_check": 0,
                "bayar_masuk": transaction_data.get("entry_fee", 0),
                "type": "parking_transaction",
                "created_at": iso_time
            }
            
            # Add exit data if this is an exit transaction
            if transaction_data.get("transaction_type") in ["member_exit", "non_member_exit", "exit"]:
                structured_transaction.update({
                    "waktu_keluar": iso_time,
                    "bayar_keluar": transaction_data.get("exit_fee", 0),
                    "id_pintu_keluar": transaction_data.get("exit_gate_id", "EXIT_GATE_01"),
                    "id_op_keluar": transaction_data.get("exit_operator_id", "SYSTEM"),
                    "id_shift_keluar": transaction_data.get("exit_shift_id", "SHIFT_001"),
                    "exit_method": transaction_data.get("exit_method", "alpr"),
                    "exit_input": transaction_data.get("exit_input", transaction_id),
                    "updated_at": iso_time,
                    "status_transaksi": "2"  # Completed transaction
                })
            
            # Save document
            doc_id, doc_rev = self.db.save(structured_transaction)
            
            # Add image attachments if provided
            if entry_image:
                doc = self.db[doc_id]
                self.db.put_attachment(doc, entry_image, 'entry.jpg', 'image/jpeg')
                
            if exit_image:
                doc = self.db[doc_id]
                self.db.put_attachment(doc, exit_image, 'exit.jpg', 'image/jpeg')
            
            logger.info(f"Transaction saved with ID: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Failed to save transaction: {e}")
            raise
    
    def _get_vehicle_type_id(self, vehicle_type: str) -> int:
        """Get vehicle type ID"""
        vehicle_types = {
            "Car": 2,
            "Motorcycle": 1,
            "Truck": 3,
            "Bus": 4
        }
        return vehicle_types.get(vehicle_type, 2)  # Default to Car
    
    def update_transaction_exit(self, transaction_id: str, exit_data: Dict[str, Any], exit_image: bytes = None) -> str:
        """Update existing transaction with exit information"""
        try:
            # Get existing transaction
            doc = self.db[transaction_id]
            
            # Get current datetime
            now = datetime.datetime.now()
            iso_time = now.isoformat() + "Z"
            
            # Update with exit data
            doc.update({
                "waktu_keluar": iso_time,
                "bayar_keluar": exit_data.get("exit_fee", 0),
                "id_pintu_keluar": exit_data.get("exit_gate_id", "EXIT_GATE_01"),
                "id_op_keluar": exit_data.get("exit_operator_id", "SYSTEM"),
                "id_shift_keluar": exit_data.get("exit_shift_id", "SHIFT_001"),
                "exit_method": exit_data.get("exit_method", "alpr"),
                "exit_input": exit_data.get("exit_input", ""),
                "updated_at": iso_time,
                "status_transaksi": "2"  # Completed transaction
            })
            
            # Save updated document
            doc_id, doc_rev = self.db.save(doc)
            
            # Add exit image if provided
            if exit_image:
                updated_doc = self.db[doc_id]
                self.db.put_attachment(updated_doc, exit_image, 'exit.jpg', 'image/jpeg')
            
            logger.info(f"Transaction updated with exit data: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Failed to update transaction exit: {e}")
            raise
    
    def get_transaction(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction by ID"""
        try:
            return self.db[doc_id]
        except couchdb.ResourceNotFound:
            return None
        except Exception as e:
            logger.error(f"Failed to get transaction {doc_id}: {e}")
            raise
    
    def get_member_by_plate(self, plate_number: str) -> Optional[Dict[str, Any]]:
        """Get member by plate number"""
        try:
            # Create view if not exists
            design_doc = {
                '_id': '_design/members',
                'views': {
                    'by_plate': {
                        'map': '''
                        function(doc) {
                            if (doc.type === 'member' && doc.plate_number) {
                                emit(doc.plate_number, doc);
                            }
                        }
                        '''
                    }
                }
            }
            
            if '_design/members' not in self.db:
                self.db.save(design_doc)
            
            # Query view
            result = self.db.view('members/by_plate', key=plate_number)
            if result.rows:
                return result.rows[0].value
            return None
        except Exception as e:
            logger.error(f"Failed to get member by plate {plate_number}: {e}")
            return None
    
    def get_last_entry_transaction(self, plate_number: str) -> Optional[Dict[str, Any]]:
        """Get last entry transaction for a plate number"""
        try:
            # Create view if not exists
            design_doc = {
                '_id': '_design/transactions',
                'views': {
                    'entry_by_plate': {
                        'map': '''
                        function(doc) {
                            if ((doc.type === 'member_entry' || doc.type === 'non_member_entry') && doc.plate_number) {
                                emit([doc.plate_number, doc.timestamp], doc);
                            }
                        }
                        '''
                    }
                }
            }
            
            if '_design/transactions' not in self.db:
                self.db.save(design_doc)
            
            # Query view with descending order to get latest
            result = self.db.view('transactions/entry_by_plate', 
                                startkey=[plate_number, {}], 
                                endkey=[plate_number], 
                                descending=True, 
                                limit=1)
            
            if result.rows:
                return result.rows[0].value
            return None
        except Exception as e:
            logger.error(f"Failed to get last entry transaction for plate {plate_number}: {e}")
            return None
    
    def save_member(self, member_data: Dict[str, Any]) -> str:
        """Save member data"""
        try:
            member_data['type'] = 'member'
            member_data['created_at'] = datetime.datetime.now().isoformat()
            doc_id, doc_rev = self.db.save(member_data)
            logger.info(f"Member saved with ID: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Failed to save member: {e}")
            raise
    
    def get_all_members(self) -> List[Dict[str, Any]]:
        """Get all members"""
        try:
            # Create view if not exists
            design_doc = {
                '_id': '_design/members',
                'views': {
                    'all': {
                        'map': '''
                        function(doc) {
                            if (doc.type === 'member') {
                                emit(doc._id, doc);
                            }
                        }
                        '''
                    }
                }
            }
            
            if '_design/members' not in self.db:
                self.db.save(design_doc)
            
            result = self.db.view('members/all')
            return [row.value for row in result.rows]
        except Exception as e:
            logger.error(f"Failed to get all members: {e}")
            return []
    
    def get_recent_transactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent transactions"""
        try:
            # Create view if not exists
            design_doc = {
                '_id': '_design/transactions',
                'views': {
                    'recent': {
                        'map': '''
                        function(doc) {
                            if (doc.type === 'parking_transaction' && doc.waktu_masuk) {
                                emit(doc.waktu_masuk, doc);
                            }
                        }
                        '''
                    }
                }
            }
            
            if '_design/transactions' not in self.db:
                self.db.save(design_doc)
            
            result = self.db.view('transactions/recent', descending=True, limit=limit)
            return [row.value for row in result.rows]
        except Exception as e:
            logger.error(f"Failed to get recent transactions: {e}")
            return []
