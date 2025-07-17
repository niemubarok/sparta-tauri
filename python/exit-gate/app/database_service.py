#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database Service for Exit Gate System
Compatible with Python 2.7 and 3.x
"""

from __future__ import absolute_import, print_function, unicode_literals

import json
import logging
import datetime
import time
import base64
from typing import Optional, Dict, List, Any  # For IDE support, handled by typing backport

import couchdb
import requests
from requests.auth import HTTPBasicAuth

from config import config

logger = logging.getLogger(__name__)

class DatabaseService(object):
    """Database service for PouchDB/CouchDB compatibility"""
    
    def __init__(self):
        self.local_db_name = config.get('database', 'local_db', 'transactions')
        self.remote_url = config.get('database', 'remote_url', 'http://localhost:5984')
        self.username = config.get('database', 'username', 'admin')
        self.password = config.get('database', 'password', 'password')
        
        self.server = None
        self.local_db = None
        self.remote_db = None
        
        self._sync_status = {
            'connected': False,
            'last_sync': None,
            'sync_active': False,
            'error_message': None,
            'docs_synced': 0,
            'pending_changes': 0
        }
        
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize local and remote database connections"""
        try:
            # Initialize CouchDB server connection
            if self.username and self.password:
                self.server = couchdb.Server(self.remote_url)
                self.server.resource.credentials = (self.username, self.password)
            else:
                self.server = couchdb.Server(self.remote_url)
            
            # Test connection first
            try:
                # Try to get server info to test connection
                # Use different methods depending on couchdb library version
                try:
                    info = self.server.info()
                except AttributeError:
                    # Fallback for older couchdb library versions
                    try:
                        # Try to list databases instead
                        list(self.server)
                        info = {'version': 'Unknown (legacy method)'}
                    except:
                        raise Exception("Cannot access CouchDB server")
                
                logger.info("Connected to CouchDB server: {}".format(info.get('version', 'Unknown')))
            except Exception as conn_error:
                logger.warning("Cannot connect to CouchDB server at {}: {}".format(self.remote_url, str(conn_error)))
                logger.info("Falling back to mock database mode for testing")
                self._initialize_mock_database()
                return
            
            # Create or get local database
            try:
                self.local_db = self.server[self.local_db_name]
                logger.info("Connected to existing database: {}".format(self.local_db_name))
            except couchdb.ResourceNotFound:
                self.local_db = self.server.create(self.local_db_name)
                logger.info("Created new database: {}".format(self.local_db_name))
            
            # Setup database views/indexes
            self._setup_views()
            
            # Test connection
            self._sync_status['connected'] = True
            logger.info("Database connection established")
            
        except Exception as e:
            logger.error("Failed to initialize database: {}".format(str(e)))
            logger.info("Falling back to mock database mode")
            self._initialize_mock_database()
    
    def _initialize_mock_database(self):
        """Initialize mock database for testing when CouchDB is not available"""
        try:
            logger.info("Initializing mock database...")
            
            # Create mock database object
            class MockDatabase:
                def __init__(self):
                    self.docs = {}
                    self.views = {}
                
                def __getitem__(self, doc_id):
                    if doc_id in self.docs:
                        return self.docs[doc_id].copy()
                    else:
                        raise couchdb.ResourceNotFound("Document not found: {}".format(doc_id))
                
                def __setitem__(self, doc_id, doc):
                    self.docs[doc_id] = doc.copy()
                
                def __contains__(self, doc_id):
                    return doc_id in self.docs
                
                def __iter__(self):
                    return iter(self.docs.keys())
                
                def get(self, doc_id, default=None):
                    return self.docs.get(doc_id, default)
                
                def save(self, doc):
                    doc_id = doc.get('_id')
                    if not doc_id:
                        import uuid
                        doc_id = str(uuid.uuid4())
                        doc['_id'] = doc_id
                    
                    # Add revision if not exists
                    if '_rev' not in doc:
                        doc['_rev'] = '1-{}'.format(hash(str(doc)) % 1000000)
                    
                    self.docs[doc_id] = doc.copy()
                    logger.info("Mock DB: Saved document {}".format(doc_id))
                    return doc_id, doc['_rev']
                
                def delete(self, doc):
                    doc_id = doc.get('_id')
                    if doc_id in self.docs:
                        del self.docs[doc_id]
                        logger.info("Mock DB: Deleted document {}".format(doc_id))
                        return True
                    return False
                
                def view(self, view_name, **kwargs):
                    # Simple mock view implementation
                    result = []
                    
                    if view_name == 'transactions/by_barcode':
                        key = kwargs.get('key')
                        for doc_id, doc in self.docs.items():
                            if (doc.get('type') in ['parking_transaction', 'member_entry'] and
                                (doc.get('no_barcode') == key or doc.get('card_number') == key)):
                                result.append(MockRow(doc_id, doc))
                    
                    elif view_name == 'transactions/by_plate':
                        key = kwargs.get('key')
                        for doc_id, doc in self.docs.items():
                            if (doc.get('type') in ['parking_transaction', 'member_entry'] and
                                (doc.get('no_pol') == key or doc.get('plat_nomor') == key)):
                                result.append(MockRow(doc_id, doc))
                    
                    elif view_name == 'transactions/active_transactions':
                        limit = kwargs.get('limit', 100)
                        count = 0
                        for doc_id, doc in self.docs.items():
                            if (doc.get('type') in ['parking_transaction', 'member_entry'] and
                                doc.get('status') == 0 and count < limit):
                                result.append(MockRow(doc_id, doc))
                                count += 1
                    
                    return result
                
                def info(self):
                    return {'doc_count': len(self.docs)}
                
                def put_attachment(self, doc, data, filename, content_type):
                    # Mock attachment storage
                    doc_id = doc.get('_id')
                    if doc_id in self.docs:
                        if '_attachments' not in self.docs[doc_id]:
                            self.docs[doc_id]['_attachments'] = {}
                        self.docs[doc_id]['_attachments'][filename] = {
                            'content_type': content_type,
                            'length': len(data),
                            'data': 'mock_attachment_data'
                        }
                        logger.info("Mock DB: Added attachment {} to {}".format(filename, doc_id))
                        return True
                    return False
            
            class MockRow:
                def __init__(self, key, value):
                    self.key = key
                    self.value = value
            
            self.local_db = MockDatabase()
            self._sync_status['connected'] = True
            self._sync_status['error_message'] = "Using mock database (CouchDB not available)"
            
            logger.info("Mock database initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize mock database: {}".format(str(e)))
            self._sync_status['connected'] = False
            self._sync_status['error_message'] = str(e)
    
    def _setup_views(self):
        """Setup CouchDB views for efficient querying"""
        
        # Skip view setup for mock database
        if hasattr(self.local_db, 'docs'):  # Mock database check
            logger.info("Skipping view setup for mock database")
            return
        
        views = {
            '_id': '_design/transactions',
            'views': {
                'by_barcode': {
                    'map': '''function(doc) {
                        if (doc.type === 'parking_transaction' && doc.no_barcode) {
                            emit(doc.no_barcode, doc);
                        }
                    }'''
                },
                'by_plate': {
                    'map': '''function(doc) {
                        if (doc.type === 'parking_transaction' && doc.no_pol) {
                            emit(doc.no_pol, doc);
                        }
                        if (doc.type === 'member_entry' && doc.plat_nomor) {
                            emit(doc.plat_nomor, doc);
                        }
                    }'''
                },
                'active_transactions': {
                    'map': '''function(doc) {
                        if ((doc.type === 'parking_transaction' || doc.type === 'member_entry') && doc.status === 0) {
                            emit(doc._id, doc);
                        }
                    }'''
                },
                'today_exits': {
                    'map': '''function(doc) {
                        if ((doc.type === 'parking_transaction' || doc.type === 'member_entry') && 
                            doc.status === 1 && doc.waktu_keluar) {
                            var exitDate = new Date(doc.waktu_keluar);
                            var today = new Date();
                            if (exitDate.toDateString() === today.toDateString()) {
                                emit(doc._id, doc);
                            }
                        }
                    }'''
                }
            }
        }
        
        try:
            # Check if design document exists
            try:
                existing_doc = self.local_db['_design/transactions']
                # Update if different
                if existing_doc.get('views') != views['views']:
                    views['_rev'] = existing_doc['_rev']
                    self.local_db.save(views)
                    logger.info("Updated database views")
            except couchdb.ResourceNotFound:
                # Create new design document
                self.local_db.save(views)
                logger.info("Created database views")
                
        except Exception as e:
            logger.error("Failed to setup database views: {}".format(str(e)))
    
    def find_transaction_by_barcode(self, barcode):
        """
        Find transaction by barcode
        
        Pattern yang digunakan:
        - _id: transaction_{barcode} (misal: transaction_1234)
        - no_barcode: {barcode} (misal: 1234)
        
        Jadi jika barcode adalah "1234", maka:
        - _id akan menjadi "transaction_1234"
        - no_barcode akan menjadi "1234"
        
        SPECIAL CASE: Jika user input sudah berupa "transaction_xxx", gunakan as-is
        """
        try:
            logger.info("Searching for transaction with barcode: {}".format(barcode))
            
            if not self.local_db:
                logger.error("Database not connected")
                return None
            
            # Strategy 1: Check if input is already a full transaction ID
            if barcode.lower().startswith('transaction_'):
                # Handle case-insensitive search
                actual_id = barcode.lower()
                try:
                    doc = self.local_db[actual_id]
                    if doc.get('type') in ['parking_transaction', 'member_entry']:
                        logger.info("Found transaction by full ID (lowercase): {}".format(actual_id))
                        return doc
                except couchdb.ResourceNotFound:
                    # Try exact case
                    try:
                        doc = self.local_db[barcode]
                        if doc.get('type') in ['parking_transaction', 'member_entry']:
                            logger.info("Found transaction by full ID (exact case): {}".format(barcode))
                            return doc
                    except couchdb.ResourceNotFound:
                        pass
                except Exception as e:
                    logger.warning("Error checking full ID {}: {}".format(barcode, str(e)))
            
            # Strategy 2: Direct lookup by transaction ID pattern
            # Primary pattern: transaction_{barcode}
            primary_id = "transaction_{}".format(barcode)
            
            try:
                doc = self.local_db[primary_id]
                if doc.get('type') in ['parking_transaction', 'member_entry']:
                    logger.info("Found transaction by primary ID: {}".format(primary_id))
                    return doc
            except couchdb.ResourceNotFound:
                pass
            except Exception as e:
                logger.warning("Error checking primary ID {}: {}".format(primary_id, str(e)))
            
            # Strategy 3: Alternative ID patterns
            alternative_ids = [
                barcode,  # Direct barcode as ID
                "parking_{}".format(barcode),
                "member_{}".format(barcode)
            ]
            
            for transaction_id in alternative_ids:
                try:
                    doc = self.local_db[transaction_id]
                    if doc.get('type') in ['parking_transaction', 'member_entry']:
                        logger.info("Found transaction by alternative ID: {}".format(transaction_id))
                        return doc
                except couchdb.ResourceNotFound:
                    continue
                except Exception as e:
                    logger.warning("Error checking alternative ID {}: {}".format(transaction_id, str(e)))
                    continue
            
            # Strategy 4: Search by barcode field in views (untuk active transactions)
            try:
                result = self.local_db.view('transactions/by_barcode', key=barcode)
                for row in result:
                    doc = row.value
                    if doc.get('status') == 0:  # Only active transactions for barcode field search
                        logger.info("Found active transaction by barcode view")
                        return doc
            except Exception as e:
                logger.warning("Barcode view search failed: {}".format(str(e)))
            
            # Strategy 5: Search active transactions manually (untuk active transactions)
            try:
                result = self.local_db.view('transactions/active_transactions')
                for row in result:
                    doc = row.value
                    doc_id = doc.get('_id', '')
                    
                    # Extract barcode from transaction ID (transaction_{barcode})
                    extracted_barcode = None
                    if doc_id.startswith('transaction_'):
                        extracted_barcode = doc_id.replace('transaction_', '')
                    
                    # Check various barcode fields and extracted barcode
                    if (str(extracted_barcode) == str(barcode) or
                        str(doc.get('no_barcode', '')) == str(barcode) or
                        str(doc.get('barcode', '')) == str(barcode) or
                        str(doc.get('ticket_number', '')) == str(barcode) or
                        str(doc.get('card_number', '')) == str(barcode)):
                        logger.info("Found active transaction by manual search (extracted barcode: {})".format(extracted_barcode))
                        return doc
            except Exception as e:
                logger.warning("Active transaction manual search failed: {}".format(str(e)))
            
            # Strategy 6: Fallback - scan all documents if database is small (untuk semua status)
            try:
                # Only do this if we have a small number of docs
                db_info = self.local_db.info()
                doc_count = db_info.get('doc_count', 0)
                
                if doc_count < 1000:  # Only scan if less than 1000 docs
                    logger.info("Performing full database scan (doc_count: {})".format(doc_count))
                    for doc_id in self.local_db:
                        if doc_id.startswith('_design'):
                            continue
                        try:
                            doc = self.local_db[doc_id]
                            if doc.get('type') in ['parking_transaction', 'member_entry']:
                                
                                # Extract barcode from transaction ID (transaction_{barcode})
                                extracted_barcode = None
                                if doc_id.startswith('transaction_'):
                                    extracted_barcode = doc_id.replace('transaction_', '')
                                      # Check if barcode matches any field or extracted barcode (case-insensitive)
                            if (str(extracted_barcode).lower() == str(barcode).lower() or
                                str(doc.get('no_barcode', '')).lower() == str(barcode).lower() or
                                str(doc.get('barcode', '')).lower() == str(barcode).lower() or
                                str(doc.get('ticket_number', '')).lower() == str(barcode).lower() or
                                str(doc.get('card_number', '')).lower() == str(barcode).lower() or
                                doc_id.lower().endswith('_{}'.format(barcode.lower())) or
                                doc_id.lower() == barcode.lower()):# Direct ID match
                                    logger.info("Found transaction by full scan: {} (extracted barcode: {}, status: {})".format(doc_id, extracted_barcode, doc.get('status')))
                                    return doc
                        except:
                            continue
                else:
                    logger.info("Skipping full scan - too many documents: {}".format(doc_count))
                    
            except Exception as e:
                logger.warning("Full scan failed: {}".format(str(e)))
            
            logger.info("No transaction found for barcode: {}".format(barcode))
            return None
            
        except Exception as e:
            logger.error("Error finding transaction by barcode {}: {}".format(barcode, str(e)))
            return None
    
    def find_any_transaction_by_barcode(self, barcode):
        """
        Find ANY transaction by barcode (regardless of status)
        Useful for lookup completed transactions
        """
        try:
            logger.info("Searching for ANY transaction with barcode: {}".format(barcode))
            
            if not self.local_db:
                logger.error("Database not connected")
                return None
            
            # Strategy 1: Check if input is already a full transaction ID
            if barcode.lower().startswith('transaction_'):
                # Handle case-insensitive search
                actual_id = barcode.lower()
                try:
                    doc = self.local_db[actual_id]
                    if doc.get('type') in ['parking_transaction', 'member_entry']:
                        logger.info("Found transaction by full ID (lowercase): {} (status: {})".format(actual_id, doc.get('status')))
                        return doc
                except couchdb.ResourceNotFound:
                    # Try exact case
                    try:
                        doc = self.local_db[barcode]
                        if doc.get('type') in ['parking_transaction', 'member_entry']:
                            logger.info("Found transaction by full ID (exact case): {} (status: {})".format(barcode, doc.get('status')))
                            return doc
                    except couchdb.ResourceNotFound:
                        pass
                except Exception as e:
                    logger.warning("Error checking full ID {}: {}".format(barcode, str(e)))
            
            # Strategy 2: Direct lookup by transaction ID pattern
            primary_id = "transaction_{}".format(barcode)
            try:
                doc = self.local_db[primary_id]
                if doc.get('type') in ['parking_transaction', 'member_entry']:
                    logger.info("Found transaction by primary ID: {} (status: {})".format(primary_id, doc.get('status')))
                    return doc
            except couchdb.ResourceNotFound:
                pass
            except Exception as e:
                logger.warning("Error checking primary ID {}: {}".format(primary_id, str(e)))
            
            # Strategy 3: Full database scan (all statuses)
            try:
                db_info = self.local_db.info()
                doc_count = db_info.get('doc_count', 0)
                
                logger.info("Performing full database scan for ANY status (doc_count: {})".format(doc_count))
                for doc_id in self.local_db:
                    if doc_id.startswith('_design'):
                        continue
                    try:
                        doc = self.local_db[doc_id]
                        if doc.get('type') in ['parking_transaction', 'member_entry']:
                            
                            # Extract barcode from transaction ID
                            extracted_barcode = None
                            if doc_id.startswith('transaction_'):
                                extracted_barcode = doc_id.replace('transaction_', '')
                            
                            # Check if barcode matches (case-insensitive)
                            if (str(extracted_barcode).lower() == str(barcode).lower() or
                                str(doc.get('no_barcode', '')).lower() == str(barcode).lower() or
                                str(doc.get('barcode', '')).lower() == str(barcode).lower() or
                                str(doc.get('ticket_number', '')).lower() == str(barcode).lower() or
                                str(doc.get('card_number', '')).lower() == str(barcode).lower() or
                                doc_id.lower().endswith('_{}'.format(barcode.lower())) or
                                doc_id.lower() == barcode.lower()):
                                logger.info("Found transaction by full scan: {} (extracted barcode: {}, status: {})".format(doc_id, extracted_barcode, doc.get('status')))
                                return doc
                    except:
                        continue
                        
            except Exception as e:
                logger.warning("Full scan failed: {}".format(str(e)))
            
            logger.info("No transaction found for barcode: {} (any status)".format(barcode))
            return None
            
        except Exception as e:
            logger.error("Error finding ANY transaction by barcode {}: {}".format(barcode, str(e)))
            return None
    
    def find_transaction_by_plate(self, plate_number):
        """Find transaction by plate number"""
        try:
            # Try plate number view
            try:
                result = self.local_db.view('transactions/by_plate', key=plate_number)
                for row in result:
                    if row.value.get('status') == 0:
                        return row.value
            except:
                pass
            
            # Scan active transactions
            try:
                result = self.local_db.view('transactions/active_transactions')
                for row in result:
                    doc = row.value
                    if (doc.get('no_pol') == plate_number or 
                        doc.get('plat_nomor') == plate_number):
                        return doc
            except:
                pass
            
            return None
            
        except Exception as e:
            logger.error("Error finding transaction by plate {}: {}".format(plate_number, str(e)))
            return None
    
    def calculate_parking_fee(self, transaction, exit_time=None):
        """Calculate parking fee based on transaction and exit time"""
        try:
            if not exit_time:
                exit_time = datetime.datetime.now()
            elif isinstance(exit_time, str):
                exit_time = datetime.datetime.fromisoformat(exit_time.replace('Z', '+00:00'))
            
            # Get entry time
            entry_time_str = transaction.get('waktu_masuk') or transaction.get('entry_time')
            if not entry_time_str:
                return 0
            
            entry_time = datetime.datetime.fromisoformat(entry_time_str.replace('Z', '+00:00'))
            
            # Calculate duration in hours
            duration = exit_time - entry_time
            hours = max(1, int(duration.total_seconds() / 3600))  # Minimum 1 hour
            
            # Get vehicle type and tariff
            vehicle_id = transaction.get('id_kendaraan', 1)
            base_tariff = self._get_vehicle_tariff(vehicle_id)
            
            # Calculate total fee
            total_fee = hours * base_tariff
            
            logger.info("Calculated parking fee: {} hours x {} = {}".format(
                hours, base_tariff, total_fee))
            
            return total_fee
            
        except Exception as e:
            logger.error("Error calculating parking fee: {}".format(str(e)))
            return 0
    
    def _get_vehicle_tariff(self, vehicle_id):
        """Get tariff for vehicle type"""
        try:
            # Try to get from kendaraan database
            tariff = 5000  # Default tariff
            
            # This would be enhanced to query tariff database
            # For now, return default based on vehicle type
            tariff_map = {
                1: 5000,   # Motor
                2: 10000,  # Mobil
                3: 15000,  # Truck
            }
            
            return tariff_map.get(vehicle_id, 5000)
            
        except Exception as e:
            logger.error("Error getting vehicle tariff: {}".format(str(e)))
            return 5000
    
    def exit_transaction(self, transaction_id, exit_data):
        """Update transaction with exit data"""
        try:
            # Get existing transaction
            doc = self.local_db[transaction_id]
            
            # Update with exit data
            doc.update(exit_data)
            doc['status'] = 1  # Mark as exited
            doc['status_transaksi'] = "1"
            doc['updated_at'] = datetime.datetime.now().isoformat()
            
            # Save updated document
            self.local_db.save(doc)
            
            logger.info("Transaction {} marked as exited".format(transaction_id))
            return True
            
        except Exception as e:
            logger.error("Error updating exit transaction: {}".format(str(e)))
            return False
    
    def process_vehicle_exit(self, plate_or_barcode, operator_id, gate_id, exit_image_data=None):
        """Comprehensive exit processing method"""
        try:
            logger.info("Processing vehicle exit for: {}".format(plate_or_barcode))
            
            if not self.local_db:
                return {
                    'success': False,
                    'message': 'Database not connected',
                    'fee': 0,
                    'error_code': 'DB_NOT_CONNECTED'
                }
            
            # Find transaction by barcode first, then by plate
            transaction = None
            search_method = None
            
            # Try barcode search first
            transaction = self.find_transaction_by_barcode(plate_or_barcode)
            if transaction:
                search_method = 'barcode'
                logger.info("Found transaction by barcode")
            else:
                # Try plate number search
                transaction = self.find_transaction_by_plate(plate_or_barcode)
                if transaction:
                    search_method = 'plate'
                    logger.info("Found transaction by plate number")
            
            if not transaction:
                logger.warning("No transaction found for: {}".format(plate_or_barcode))
                return {
                    'success': False,
                    'message': 'No active transaction found for: {}'.format(plate_or_barcode),
                    'fee': 0,
                    'error_code': 'TRANSACTION_NOT_FOUND',
                    'search_methods_tried': ['barcode', 'plate']
                }
            
            # Check if already exited
            current_status = transaction.get('status', 0)
            if current_status == 1:
                exit_time = transaction.get('waktu_keluar', 'Unknown')
                logger.warning("Vehicle already exited at: {}".format(exit_time))
                return {
                    'success': False,
                    'message': 'Vehicle already exited at: {}'.format(exit_time),
                    'fee': transaction.get('bayar_keluar', 0),
                    'error_code': 'ALREADY_EXITED',
                    'transaction': transaction
                }
            
            # Calculate fee
            exit_time = datetime.datetime.now()
            fee = self.calculate_parking_fee(transaction, exit_time)
            duration_hours = self._calculate_duration_hours(transaction, exit_time)
            
            logger.info("Calculated fee: {} for {} hours".format(fee, duration_hours))
            
            # Prepare exit data
            exit_data = {
                'waktu_keluar': exit_time.isoformat(),
                'bayar_keluar': fee,
                'id_pintu_keluar': gate_id,
                'id_op_keluar': operator_id,
                'id_shift_keluar': 'SHIFT_001',  # Default shift
                'exit_method': search_method,
                'exit_input': plate_or_barcode,
                'status': 1,  # Mark as exited
                'status_transaksi': "1"
            }
            
            # Update transaction
            success = self.exit_transaction(transaction['_id'], exit_data)
            
            if success:
                # Add exit image as attachment if provided
                if exit_image_data:
                    image_success = self.add_image_to_transaction(transaction['_id'], 'exit.jpg', exit_image_data)
                    if image_success:
                        logger.info("Added exit image to transaction")
                    else:
                        logger.warning("Failed to add exit image to transaction")
                
                logger.info("Vehicle exit processed successfully for: {}".format(plate_or_barcode))
                return {
                    'success': True,
                    'message': 'Vehicle exit processed successfully',
                    'fee': fee,
                    'transaction': transaction,
                    'duration_hours': duration_hours,
                    'exit_time': exit_time.isoformat(),
                    'search_method': search_method,
                    'transaction_id': transaction['_id']
                }
            else:
                logger.error("Failed to update transaction in database")
                return {
                    'success': False,
                    'message': 'Failed to update transaction in database',
                    'fee': fee,
                    'error_code': 'UPDATE_FAILED',
                    'transaction': transaction
                }
            
        except Exception as e:
            error_msg = "System error processing exit: {}".format(str(e))
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'fee': 0,
                'error_code': 'SYSTEM_ERROR',
                'exception': str(e)
            }
    
    def _calculate_duration_hours(self, transaction, exit_time):
        """Calculate parking duration in hours"""
        try:
            entry_time_str = transaction.get('waktu_masuk') or transaction.get('entry_time')
            if not entry_time_str:
                return 0
            
            entry_time = datetime.datetime.fromisoformat(entry_time_str.replace('Z', '+00:00'))
            duration = exit_time - entry_time
            return max(1, int(duration.total_seconds() / 3600))
            
        except:
            return 0
    
    def get_today_exit_stats(self):
        """Get today's exit statistics"""
        try:
            result = self.local_db.view('transactions/today_exits')
            
            total_exits = 0
            total_revenue = 0
            
            for row in result:
                doc = row.value
                total_exits += 1
                total_revenue += doc.get('bayar_keluar', 0)
            
            return {
                'total_exits': total_exits,
                'total_revenue': total_revenue
            }
            
        except Exception as e:
            logger.error("Error getting today's stats: {}".format(str(e)))
            return {'total_exits': 0, 'total_revenue': 0}
    
    def get_settings(self):
        """Get gate settings from database"""
        try:
            # Try to get settings document
            settings_doc = self.local_db.get('gate_settings')
            if settings_doc:
                return settings_doc
            
            # Create default settings
            default_settings = {
                '_id': 'gate_settings',
                'type': 'gate_settings',
                'serial_port': config.get('gate', 'serial_port'),
                'baud_rate': config.getint('gate', 'baud_rate'),
                'gate_timeout': config.getint('gate', 'timeout'),
                'control_mode': config.get('gate', 'control_mode'),
                'gpio_pin': config.getint('gpio', 'gate_pin'),
                'gpio_active_high': config.getboolean('gpio', 'active_high'),
                'camera_enabled': config.getboolean('camera', 'enabled'),
                'plate_camera_ip': config.get('camera', 'plate_camera_ip'),
                'plate_camera_username': config.get('camera', 'plate_camera_username'),
                'plate_camera_password': config.get('camera', 'plate_camera_password'),
                'driver_camera_ip': config.get('camera', 'driver_camera_ip'),
                'driver_camera_username': config.get('camera', 'driver_camera_username'),
                'driver_camera_password': config.get('camera', 'driver_camera_password'),
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat()
            }
            
            self.local_db.save(default_settings)
            return default_settings
            
        except Exception as e:
            logger.error("Error getting settings: {}".format(str(e)))
            return None
    
    def save_settings(self, settings):
        """Save gate settings to database"""
        try:
            settings['updated_at'] = datetime.datetime.now().isoformat()
            self.local_db.save(settings)
            return True
        except Exception as e:
            logger.error("Error saving settings: {}".format(str(e)))
            return False
    
    def sync_with_remote(self):
        """Sync local database with remote"""
        try:
            if not self._sync_status['connected']:
                return False
            
            self._sync_status['sync_active'] = True
            
            # This would implement actual sync logic
            # For now, just update sync status
            self._sync_status['last_sync'] = datetime.datetime.now().isoformat()
            self._sync_status['sync_active'] = False
            
            return True
            
        except Exception as e:
            logger.error("Sync error: {}".format(str(e)))
            self._sync_status['sync_active'] = False
            self._sync_status['error_message'] = str(e)
            return False
    
    def get_sync_status(self):
        """Get current sync status"""
        # Update connection status based on current database state
        if hasattr(self.local_db, 'docs'):
            # Mock database mode
            self._sync_status['connected'] = True
            if 'error_message' not in self._sync_status or not self._sync_status['error_message']:
                self._sync_status['error_message'] = "Using mock database (CouchDB not available)"
        else:
            # Real CouchDB connection - test it
            try:
                if self.local_db and self.server:
                    # Try a simple operation to verify connection
                    try:
                        self.server.info()
                        self._sync_status['connected'] = True
                        self._sync_status['error_message'] = None
                    except AttributeError:
                        # Fallback test for older library versions
                        list(self.server)
                        self._sync_status['connected'] = True
                        self._sync_status['error_message'] = None
                else:
                    self._sync_status['connected'] = False
            except Exception as e:
                self._sync_status['connected'] = False
                self._sync_status['error_message'] = str(e)
        
        return self._sync_status.copy()
    
    def add_image_to_transaction(self, transaction_id, image_name, image_data):
        """Add image attachment to transaction"""
        try:
            doc = self.local_db[transaction_id]
            
            # Convert base64 image data if needed
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                # Remove data URL prefix
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Add as attachment
            self.local_db.put_attachment(doc, image_bytes, filename=image_name, 
                                       content_type='image/jpeg')
            
            logger.info("Added image {} to transaction {}".format(image_name, transaction_id))
            return True
            
        except Exception as e:
            logger.error("Error adding image to transaction: {}".format(str(e)))
            return False
    
    def create_test_transaction(self, barcode, plate_number=None, entry_image_data=None):
        """Create a test transaction for debugging"""
        try:
            if not self.local_db:
                logger.error("Database not connected")
                return False
            
            # Generate test transaction
            now = datetime.datetime.now()
            transaction_id = "transaction_{}".format(barcode)
            
            test_transaction = {
                '_id': transaction_id,
                'type': 'parking_transaction',
                'no_barcode': barcode,  # barcode adalah bagian setelah transaction_ di _id
                'no_pol': plate_number or "TEST{}".format(barcode[-4:]),
                'id_kendaraan': 1,  # Motor
                'waktu_masuk': now.isoformat(),
                'id_pintu_masuk': 'ENTRY_GATE_01',
                'id_op_masuk': 'SYSTEM',
                'id_shift_masuk': 'SHIFT_001',
                'status': 0,  # Active transaction
                'status_transaksi': "0",
                'created_at': now.isoformat(),
                'updated_at': now.isoformat(),
                'test_transaction': True
            }
            
            # Save to database
            saved_doc = self.local_db.save(test_transaction)
            
            # Add entry image as attachment if provided
            if entry_image_data:
                success = self.add_image_to_transaction(transaction_id, 'entry.jpg', entry_image_data)
                if success:
                    logger.info("Added entry image to test transaction")
                else:
                    logger.warning("Failed to add entry image to test transaction")
            
            logger.info("Created test transaction: {} with barcode: {}".format(transaction_id, barcode))
            return True
            
        except Exception as e:
            logger.error("Error creating test transaction: {}".format(str(e)))
            return False
    
    def create_test_member_entry(self, barcode, plate_number=None):
        """Create a test member entry for debugging"""
        try:
            if not self.local_db:
                logger.error("Database not connected")
                return False
            
            # Generate test member entry
            now = datetime.datetime.now()
            transaction_id = "member_{}".format(barcode)
            
            member_entry = {
                '_id': transaction_id,
                'type': 'member_entry',
                'card_number': barcode,
                'plat_nomor': plate_number or "MEMBER{}".format(barcode[-3:]),
                'id_member': 'MEMBER_TEST',
                'member_name': 'Test Member',
                'waktu_masuk': now.isoformat(),
                'entry_time': now.isoformat(),
                'id_pintu_masuk': 'ENTRY_GATE_01',
                'id_op_masuk': 'SYSTEM',
                'status': 0,  # Active entry
                'created_at': now.isoformat(),
                'updated_at': now.isoformat(),
                'test_transaction': True
            }
            
            # Save to database
            self.local_db.save(member_entry)
            logger.info("Created test member entry: {}".format(transaction_id))
            return True
            
        except Exception as e:
            logger.error("Error creating test member entry: {}".format(str(e)))
            return False
    
    def generate_sample_image_data(self, image_type='entry'):
        """Generate sample base64 image data for testing"""
        try:
            import base64
            
            # Create a simple colored rectangle as sample image
            # This is a minimal 10x10 pixel PNG in base64 format
            if image_type == 'entry':
                # Green rectangle for entry
                sample_png = (
                    "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAABHNCSVQICAgIfAhkiAAAAAlwSFlz"
                    "AAALETAAABE0lQVyiAAAAJ0lEQVQYV2NkQAOMo4qRCcOGIRZgpE49MjAyMjIyMjIyMjIyMjIyMg=="
                )
            else:
                # Red rectangle for exit  
                sample_png = (
                    "iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAYAAACNMs+9AAAABHNCSVQICAgIfAhkiAAAAAlwSFlz"
                    "AAALETAAABE0lQVyiAAAAJ0lEQVQYV2P8//8/IyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjI8j4wQ=="
                )
            
            return sample_png
            
        except Exception as e:
            logger.error("Error generating sample image data: {}".format(str(e)))
            return None
    
    def cleanup_test_transactions(self):
        """Clean up all test transactions"""
        try:
            if not self.local_db:
                return False
            
            deleted_count = 0
            
            # Find all test transactions first (to avoid dictionary size change during iteration)
            test_doc_ids = []
            for doc_id in list(self.local_db):  # Convert to list to avoid iteration issues
                if doc_id.startswith('_design'):
                    continue
                    
                try:
                    doc = self.local_db[doc_id]
                    if doc.get('test_transaction'):
                        test_doc_ids.append(doc_id)
                except:
                    continue
            
            # Now delete them
            for doc_id in test_doc_ids:
                try:
                    doc = self.local_db[doc_id]
                    self.local_db.delete(doc)
                    deleted_count += 1
                    logger.info("Deleted test transaction: {}".format(doc_id))
                except:
                    continue
            
            logger.info("Cleaned up {} test transactions".format(deleted_count))
            return True
            
        except Exception as e:
            logger.error("Error cleaning up test transactions: {}".format(str(e)))
            return False
    
    def list_active_transactions(self, limit=10):
        """List active transactions for debugging"""
        try:
            if not self.local_db:
                return []
            
            transactions = []
            result = self.local_db.view('transactions/active_transactions', limit=limit)
            
            for row in result:
                doc = row.value
                transactions.append({
                    'id': doc.get('_id'),
                    'type': doc.get('type'),
                    'barcode': doc.get('no_barcode') or doc.get('card_number'),
                    'plate': doc.get('no_pol') or doc.get('plat_nomor'),
                    'entry_time': doc.get('waktu_masuk') or doc.get('entry_time'),
                    'test': doc.get('test_transaction', False)
                })
            
            return transactions
            
        except Exception as e:
            logger.error("Error listing active transactions: {}".format(str(e)))
            return []
    
    def get_transaction_info(self, barcode_or_id):
        """Get detailed transaction info for debugging"""
        try:
            if not self.local_db:
                return None
            
            # Try to find transaction
            transaction = self.find_transaction_by_barcode(barcode_or_id)
            
            if not transaction:
                # Try direct ID lookup
                try:
                    transaction = self.local_db[barcode_or_id]
                except:
                    return None
            
            if transaction:
                doc_id = transaction.get('_id', '')
                
                # Extract barcode from ID if it follows transaction_ pattern
                extracted_barcode = None
                if doc_id.startswith('transaction_'):
                    extracted_barcode = doc_id.replace('transaction_', '')
                
                return {
                    'found': True,
                    'id': doc_id,
                    'type': transaction.get('type'),
                    'status': transaction.get('status'),
                    'barcode_field': transaction.get('no_barcode') or transaction.get('card_number'),
                    'extracted_barcode': extracted_barcode,  # Barcode dari _id
                    'plate': transaction.get('no_pol') or transaction.get('plat_nomor'),
                    'entry_time': transaction.get('waktu_masuk') or transaction.get('entry_time'),
                    'exit_time': transaction.get('waktu_keluar'),
                    'fee': transaction.get('bayar_keluar', 0),
                    'test': transaction.get('test_transaction', False),
                    'full_doc': transaction
                }
            
            return None
            
        except Exception as e:
            logger.error("Error getting transaction info: {}".format(str(e)))
            return None

# Global database service instance
db_service = DatabaseService()
