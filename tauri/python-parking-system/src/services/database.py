"""
Database Service for Python Parking System
Supports CouchDB with JSON file fallback
"""

import logging
import uuid
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union

try:
    import couchdb
    from couchdb.client import Row
    COUCHDB_AVAILABLE = True
except ImportError:
    COUCHDB_AVAILABLE = False
    logger.warning("CouchDB library not available, using JSON fallback only")

from ..core.config import settings
from ..core.models import (
    ParkingTransactionCreate, SystemStatus
)

logger = logging.getLogger(__name__)


"""
Database Service for Python Parking System
Supports CouchDB with JSON file fallback
"""

import logging
import uuid
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union

from ..core.config import settings
from ..core.models import (
    ParkingTransactionCreate, SystemStatus
)

logger = logging.getLogger(__name__)

try:
    import couchdb
    from couchdb.client import Row
    COUCHDB_AVAILABLE = True
except ImportError:
    COUCHDB_AVAILABLE = False
    logger.warning("CouchDB library not available, using JSON fallback only")


class DatabaseService:
    """Database service with CouchDB and JSON fallback"""
    
    def __init__(self):
        self.server = None
        self.db = None
        self.connected = False
        self.data_file = "parking_data.json"
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize CouchDB connection with fallback"""
        if COUCHDB_AVAILABLE:
            try:
                # Connect to CouchDB server
                if settings.couchdb_username and settings.couchdb_password:
                    server_url = f"http://{settings.couchdb_username}:{settings.couchdb_password}@{settings.couchdb_url.replace('http://', '')}"
                    self.server = couchdb.Server(server_url)
                else:
                    self.server = couchdb.Server(settings.couchdb_url)
                
                # Create or connect to database
                db_name = settings.couchdb_database
                if db_name in self.server:
                    self.db = self.server[db_name]
                else:
                    self.db = self.server.create(db_name)
                    logger.info(f"Created new CouchDB database: {db_name}")
                
                # Create design documents (views)
                self._create_design_documents()
                
                self.connected = True
                logger.info(f"Connected to CouchDB: {settings.couchdb_url}/{db_name}")
                return
                
            except Exception as e:
                logger.warning(f"CouchDB not available, using JSON file fallback: {e}")
        
        # Fallback to JSON file storage
        self.connected = False
        self._init_json_storage()
    
    def _init_json_storage(self):
        """Initialize JSON file storage"""
        if not os.path.exists(self.data_file):
            initial_data = {
                "transactions": {},
                "members": {},
                "settings": {},
                "activity_logs": []
            }
            with open(self.data_file, 'w') as f:
                json.dump(initial_data, f, indent=2)
        
        logger.info(f"Using JSON file storage: {self.data_file}")
    
    def _load_json_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load JSON data: {e}")
            return {"transactions": {}, "members": {}, "settings": {}, "activity_logs": []}
    
    def _save_json_data(self, data: Dict[str, Any]):
        """Save data to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save JSON data: {e}")
    
    def _create_design_documents(self):
        """Create CouchDB design documents for views"""
        if not self.connected:
            return
            
        try:
            # Transactions view
            transactions_design = {
                "_id": "_design/transactions",
                "views": {
                    "by_plate": {
                        "map": """
                        function(doc) {
                            if (doc.type === 'transaction' && doc.no_pol) {
                                emit(doc.no_pol, doc);
                            }
                        }
                        """
                    },
                    "active_by_plate": {
                        "map": """
                        function(doc) {
                            if (doc.type === 'transaction' && doc.status === 0 && doc.no_pol) {
                                emit(doc.no_pol, doc);
                            }
                        }
                        """
                    }
                }
            }
            
            # Save design documents
            for design in [transactions_design]:
                doc_id = design["_id"]
                if doc_id in self.db:
                    existing = self.db[doc_id]
                    design["_rev"] = existing["_rev"]
                self.db[doc_id] = design
            
            logger.info("CouchDB design documents created/updated")
            
        except Exception as e:
            logger.error(f"Failed to create design documents: {e}")
    
    def create_transaction(self, transaction_data: ParkingTransactionCreate, gate_id: str) -> Dict[str, Any]:
        """Create new parking transaction"""
        try:
            transaction_id = str(uuid.uuid4())
            transaction_doc = {
                "id": transaction_id,
                "_id": transaction_id,
                "type": "transaction",
                "no_pol": transaction_data.no_pol,
                "id_kendaraan": transaction_data.id_kendaraan,
                "entry_time": datetime.utcnow().isoformat(),
                "waktu_keluar": None,
                "status": 0,  # 0 = active, 1 = completed
                "tarif": 0,
                "durasi": 0,
                "jenis_system": transaction_data.jenis_system,
                "kategori": transaction_data.kategori,
                "id_pintu_masuk": gate_id,
                "id_pintu_keluar": None,
                "id_op_masuk": None,
                "id_op_keluar": None,
                "pic_no_pol_masuk": None,
                "pic_driver_masuk": None,
                "pic_no_pol_keluar": None,
                "pic_driver_keluar": None,
                "entry_plate_confidence": None,
                "exit_plate_confidence": None,
                "manual": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if self.connected:
                # Save to CouchDB
                doc_id, doc_rev = self.db.save(transaction_doc)
                transaction_doc["_rev"] = doc_rev
            else:
                # Save to JSON file
                data = self._load_json_data()
                data["transactions"][transaction_id] = transaction_doc
                self._save_json_data(data)
            
            logger.info(f"Created transaction: {transaction_id} for plate {transaction_data.no_pol}")
            
            # Convert to object-like access
            class TransactionObj:
                def __init__(self, data):
                    for key, value in data.items():
                        setattr(self, key, value)
            
            return TransactionObj(transaction_doc)
            
        except Exception as e:
            logger.error(f"Failed to create transaction: {e}")
            raise
    
    def find_transaction_by_plate(self, plate_number: str, status: int = None) -> Optional[Dict[str, Any]]:
        """Find transaction by plate number"""
        try:
            if self.connected:
                # Use CouchDB views
                if status is not None and status == 0:
                    result = self.db.view('transactions/active_by_plate', key=plate_number)
                else:
                    result = self.db.view('transactions/by_plate', key=plate_number)
                
                transactions = [row.value for row in result]
            else:
                # Use JSON file
                data = self._load_json_data()
                transactions = [t for t in data["transactions"].values() 
                              if t.get("no_pol") == plate_number]
            
            if status is not None:
                transactions = [t for t in transactions if t.get('status') == status]
            
            # Return most recent transaction
            if transactions:
                latest = max(transactions, key=lambda x: x.get('entry_time', ''))
                
                # Convert to object-like access
                class TransactionObj:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                
                return TransactionObj(latest)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find transaction by plate {plate_number}: {e}")
            return None
    
    def find_transaction_by_id(self, transaction_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        """Find transaction by ID"""
        try:
            doc_id = str(transaction_id)
            
            if self.connected:
                # Use CouchDB
                if doc_id in self.db:
                    doc = self.db[doc_id]
                else:
                    return None
            else:
                # Use JSON file
                data = self._load_json_data()
                doc = data["transactions"].get(doc_id)
                if not doc:
                    return None
            
            # Convert to object-like access
            class TransactionObj:
                def __init__(self, data):
                    for key, value in data.items():
                        setattr(self, key, value)
            
            return TransactionObj(doc)
            
        except Exception as e:
            logger.error(f"Failed to find transaction by ID {transaction_id}: {e}")
            return None
    
    def get_session(self):
        """Get session context (for compatibility)"""
        class SessionContext:
            def __init__(self, db_service):
                self.db_service = db_service
            
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass
            
            def add(self, obj):
                # For compatibility - actual saving will be done in commit()
                pass
            
            def commit(self):
                # For compatibility
                pass
            
            def refresh(self, obj):
                # For compatibility - refresh object from database
                if hasattr(obj, 'id') or hasattr(obj, '_id'):
                    doc_id = getattr(obj, 'id', None) or getattr(obj, '_id', None)
                    # In JSON mode, object is already up to date
                    pass
            
            def merge(self, obj):
                # Update object in database
                if hasattr(obj, 'id') or hasattr(obj, '_id'):
                    doc_id = getattr(obj, 'id', None) or getattr(obj, '_id', None)
                    doc_data = {key: getattr(obj, key) for key in dir(obj) 
                               if not key.startswith('_') and not callable(getattr(obj, key))}
                    doc_data['updated_at'] = datetime.utcnow().isoformat()
                    
                    if self.db_service.connected:
                        # Update in CouchDB
                        if hasattr(obj, '_rev'):
                            doc_data['_rev'] = obj._rev
                        doc_data['_id'] = doc_id
                        self.db_service.db.save(doc_data)
                    else:
                        # Update in JSON file
                        data = self.db_service._load_json_data()
                        if 'type' in doc_data and doc_data['type'] == 'transaction':
                            data["transactions"][doc_id] = doc_data
                        self.db_service._save_json_data(data)
                return obj
        
        return SessionContext(self)
    
    def check_membership(self, plate_number: str) -> bool:
        """Check if plate number belongs to active member"""
        try:
            if self.connected:
                # Use CouchDB (would need design document for members)
                return False  # Simplified for now
            else:
                # Use JSON file
                data = self._load_json_data()
                for member in data["members"].values():
                    if member.get("no_pol") == plate_number and member.get("active"):
                        return True
                return False
            
        except Exception as e:
            logger.error(f"Failed to check membership for {plate_number}: {e}")
            return False
    
    def get_gate_settings(self, gate_id: str) -> Optional[Dict[str, Any]]:
        """Get gate settings by ID"""
        try:
            if self.connected:
                # Use CouchDB (would need design document)
                return None  # Simplified for now
            else:
                # Use JSON file
                data = self._load_json_data()
                settings_data = data["settings"].get(gate_id)
                
                if settings_data:
                    class SettingsObj:
                        def __init__(self, data):
                            for key, value in data.items():
                                setattr(self, key, value)
                    
                    return SettingsObj(settings_data)
                return None
            
        except Exception as e:
            logger.error(f"Failed to get gate settings for {gate_id}: {e}")
            return None
    
    def update_gate_settings(self, gate_id: str, settings_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update gate settings"""
        try:
            if self.connected:
                # Use CouchDB (simplified)
                return None
            else:
                # Use JSON file
                data = self._load_json_data()
                
                existing = data["settings"].get(gate_id, {})
                existing.update(settings_data)
                existing["updated_at"] = datetime.utcnow().isoformat()
                data["settings"][gate_id] = existing
                
                self._save_json_data(data)
                
                class SettingsObj:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                
                return SettingsObj(existing)
                
        except Exception as e:
            logger.error(f"Failed to update gate settings for {gate_id}: {e}")
            return None
    
    def log_activity(self, gate_id: str, gate_type: str, message: str, 
                    level: str = "INFO", plate_number: str = None, 
                    operator_id: str = None):
        """Log system activity"""
        try:
            activity_doc = {
                "id": str(uuid.uuid4()),
                "type": "activity_log",
                "gate_id": gate_id,
                "gate_type": gate_type,
                "level": level,
                "message": message,
                "plate_number": plate_number,
                "operator_id": operator_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if self.connected:
                # Save to CouchDB
                self.db.save(activity_doc)
            else:
                # Save to JSON file
                data = self._load_json_data()
                data["activity_logs"].append(activity_doc)
                # Keep only last 1000 logs
                if len(data["activity_logs"]) > 1000:
                    data["activity_logs"] = data["activity_logs"][-1000:]
                self._save_json_data(data)
            
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
    
    def get_activity_logs(self, gate_id: str = None, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent activity logs"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            cutoff_iso = cutoff_time.isoformat()
            
            if self.connected:
                # Use CouchDB (simplified)
                return []
            else:
                # Use JSON file
                data = self._load_json_data()
                logs = data["activity_logs"]
                
                # Filter by time and gate
                filtered_logs = []
                for log in logs:
                    if log.get("timestamp", "") >= cutoff_iso:
                        if gate_id is None or log.get("gate_id") == gate_id:
                            filtered_logs.append(log)
                
                # Sort by timestamp descending
                filtered_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                
                # Convert to object-like access
                class LogObj:
                    def __init__(self, data):
                        for key, value in data.items():
                            setattr(self, key, value)
                
                return [LogObj(log) for log in filtered_logs]
            
        except Exception as e:
            logger.error(f"Failed to get activity logs: {e}")
            return []
    
    def get_vehicle_type(self, vehicle_type_id: str) -> Optional[Dict[str, Any]]:
        """Get vehicle type info"""
        vehicle_types = {
            "1": {"name": "Motor", "tarif_per_jam": 2000},
            "2": {"name": "Mobil", "tarif_per_jam": 5000},
            "3": {"name": "Truk", "tarif_per_jam": 10000}
        }
        return vehicle_types.get(vehicle_type_id)
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get database connection status"""
        try:
            if self.connected and self.db:
                # CouchDB connection
                info = self.server.version()
                return {
                    "connected": True,
                    "type": "couchdb",
                    "database": settings.couchdb_database,
                    "server_version": info,
                    "doc_count": self.db.info()["doc_count"]
                }
            else:
                # JSON file storage
                data = self._load_json_data()
                return {
                    "connected": True,
                    "type": "json_file",
                    "database": self.data_file,
                    "transaction_count": len(data.get("transactions", {})),
                    "member_count": len(data.get("members", {})),
                    "log_count": len(data.get("activity_logs", []))
                }
        except Exception as e:
            return {
                "connected": False,
                "type": "unknown",
                "error": str(e)
            }
    
    def initialize_sample_data(self):
        """Initialize sample data for testing"""
        try:
            if self.connected:
                # CouchDB sample data
                sample_members = [
                    {
                        "_id": str(uuid.uuid4()),
                        "type": "member",
                        "no_pol": "B1234ABC",
                        "name": "John Doe",
                        "phone": "081234567890",
                        "active": True,
                        "membership_type": "premium",
                        "created_at": datetime.utcnow().isoformat()
                    }
                ]
                
                for member in sample_members:
                    self.db.save(member)
            else:
                # JSON file sample data
                data = self._load_json_data()
                data["members"]["member1"] = {
                    "id": "member1",
                    "no_pol": "B1234ABC",
                    "name": "John Doe",
                    "phone": "081234567890",
                    "active": True,
                    "membership_type": "premium",
                    "created_at": datetime.utcnow().isoformat()
                }
                data["members"]["member2"] = {
                    "id": "member2",
                    "no_pol": "B5678DEF",
                    "name": "Jane Smith",
                    "phone": "081234567891",
                    "active": True,
                    "membership_type": "regular",
                    "created_at": datetime.utcnow().isoformat()
                }
                self._save_json_data(data)
            
            logger.info("Sample data initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize sample data: {e}")
    
    async def initialize(self):
        """Initialize database (async compatibility)"""
        # Database is already initialized in __init__
        # This method is for async compatibility with main.py
        try:
            self.initialize_sample_data()
            logger.info("Database service ready")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise


# Create global instance
database_service = DatabaseService()
