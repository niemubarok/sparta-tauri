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
from member_cache import member_cache
from member_views import MEMBER_VIEWS, TRANSACTION_VIEWS_ENHANCED, MEMBER_INDEXES

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
        
        # Member optimization flags
        self.views_initialized = False
        self.member_cache_enabled = True
        
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
            
            # Initialize member optimization views
            self._initialize_member_views()
            
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
    
    def _initialize_member_views(self):
        """Initialize CouchDB views untuk member optimization"""
        try:
            if not self.local_db:
                logger.error("Database not connected")
                return False
            
            # Skip for mock database
            if hasattr(self.local_db, 'docs'):  # Mock database check
                logger.info("Skipping member views setup for mock database")
                self.views_initialized = True
                return True
            
            logger.info("Initializing member optimization views...")
            
            # Create member views
            try:
                existing_doc = self.local_db[MEMBER_VIEWS['_id']]
                # Update if different
                if existing_doc.get('views') != MEMBER_VIEWS['views']:
                    existing_doc['views'] = MEMBER_VIEWS['views']
                    existing_doc['_rev'] = existing_doc['_rev']  # Keep existing revision
                    self.local_db.save(existing_doc)
                    logger.info("Updated member views")
                else:
                    logger.info("Member views already up to date")
            except couchdb.ResourceNotFound:
                self.local_db.save(MEMBER_VIEWS)
                logger.info("Created member views")
            
            # Create enhanced transaction views
            try:
                existing_doc = self.local_db[TRANSACTION_VIEWS_ENHANCED['_id']]
                if existing_doc.get('views') != TRANSACTION_VIEWS_ENHANCED['views']:
                    existing_doc['views'] = TRANSACTION_VIEWS_ENHANCED['views']
                    existing_doc['_rev'] = existing_doc['_rev']
                    self.local_db.save(existing_doc)
                    logger.info("Updated enhanced transaction views")
                else:
                    logger.info("Enhanced transaction views already up to date")
            except couchdb.ResourceNotFound:
                self.local_db.save(TRANSACTION_VIEWS_ENHANCED)
                logger.info("Created enhanced transaction views")
            
            # Create indexes for better performance (CouchDB 2.0+)
            try:
                for index_def in MEMBER_INDEXES:
                    # Try to create index (will ignore if exists)
                    try:
                        # This requires python-couchdb2 or similar
                        # For now, we'll skip index creation to maintain compatibility
                        pass
                    except:
                        pass
                logger.info("Index creation attempted")
            except Exception as e:
                logger.warning("Index creation failed (this is OK for older CouchDB): {}".format(str(e)))
            
            self.views_initialized = True
            
            # Preload active members after view creation
            self._preload_active_members()
            
            logger.info("Member optimization views initialized successfully")
            return True
            
        except Exception as e:
            logger.error("Failed to initialize member views: {}".format(str(e)))
            self.views_initialized = False
            return False
    
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
    
    def find_member_transaction_optimized(self, card_number):
        """
        Optimized member transaction lookup dengan multiple strategies
        Performance target: <5ms untuk cached, <20ms untuk uncached
        
        Args:
            card_number (str): Member card number
            
        Returns:
            dict or None: Member transaction if found, None otherwise
        """
        start_time = time.time()
        
        try:
            logger.info("Searching for member transaction with card: {}".format(card_number))
            
            if not self.local_db:
                logger.error("Database not connected")
                return None
            
            # Strategy 1: Cache lookup (Fastest - <1ms)
            if self.member_cache_enabled:
                cached_result = member_cache.get(card_number)
                if cached_result:
                    elapsed = (time.time() - start_time) * 1000
                    logger.info("✅ Found member in cache ({:.2f}ms)".format(elapsed))
                    return cached_result
            
            # Strategy 2: Direct ID pattern lookup (Fast - 1-3ms)
            member_id_patterns = [
                "member_{}".format(card_number),
                "member_entry_{}".format(card_number),
                card_number  # Direct card as ID
            ]
            
            for pattern in member_id_patterns:
                try:
                    doc = self.local_db[pattern]
                    if (doc.get('type') == 'member_entry' and 
                        doc.get('status') == 0 and 
                        doc.get('card_number') == card_number):
                        
                        # Cache the result
                        if self.member_cache_enabled:
                            member_cache.put(card_number, doc)
                        
                        elapsed = (time.time() - start_time) * 1000
                        logger.info("✅ Found member by direct ID: {} ({:.2f}ms)".format(pattern, elapsed))
                        return doc
                except couchdb.ResourceNotFound:
                    continue
                except Exception as e:
                    logger.warning("Error checking direct ID {}: {}".format(pattern, str(e)))
                    continue
            
            # Strategy 3: Indexed view lookup (Fast - 3-10ms)
            if self.views_initialized:
                try:
                    # Use active members view
                    result = self.local_db.view('members/active_members', key=card_number, limit=1)
                    for row in result:
                        doc_summary = row.value
                        if doc_summary and doc_summary.get('_id'):
                            # Get full document
                            try:
                                full_doc = self.local_db[doc_summary['_id']]
                                if self.member_cache_enabled:
                                    member_cache.put(card_number, full_doc)
                                elapsed = (time.time() - start_time) * 1000
                                logger.info("✅ Found member by active_members view ({:.2f}ms)".format(elapsed))
                                return full_doc
                            except couchdb.ResourceNotFound:
                                logger.warning("Document {} not found in active_members view".format(doc_summary['_id']))
                                continue
                except Exception as e:
                    logger.warning("Active members view failed: {}".format(str(e)))
                
                try:
                    # Use composite view
                    result = self.local_db.view('members/by_card_and_status', 
                                              key=[card_number, 0], limit=1)
                    for row in result:
                        doc = row.value
                        if self.member_cache_enabled:
                            member_cache.put(card_number, doc)
                        elapsed = (time.time() - start_time) * 1000
                        logger.info("✅ Found member by composite view ({:.2f}ms)".format(elapsed))
                        return doc
                except Exception as e:
                    logger.warning("Composite view failed: {}".format(str(e)))
            
            # Strategy 4: Enhanced universal view (Medium - 10-30ms)
            if self.views_initialized:
                try:
                    result = self.local_db.view('transactions_enhanced/active_by_type', 
                                              key=['member', card_number], limit=1)
                    for row in result:
                        doc = row.value
                        if self.member_cache_enabled:
                            member_cache.put(card_number, doc)
                        elapsed = (time.time() - start_time) * 1000
                        logger.info("✅ Found member by enhanced view ({:.2f}ms)".format(elapsed))
                        return doc
                except Exception as e:
                    logger.warning("Enhanced view failed: {}".format(str(e)))
            
            # Strategy 5: Fallback to manual search (Slow - 50-200ms)
            try:
                result = self.local_db.view('transactions/active_transactions')
                for row in result:
                    doc = row.value
                    if (doc.get('type') == 'member_entry' and 
                        doc.get('card_number') == card_number and 
                        doc.get('status') == 0):
                        
                        if self.member_cache_enabled:
                            member_cache.put(card_number, doc)
                        elapsed = (time.time() - start_time) * 1000
                        logger.info("✅ Found member by manual search ({:.2f}ms)".format(elapsed))
                        return doc
            except Exception as e:
                logger.warning("Manual search failed: {}".format(str(e)))
            
            elapsed = (time.time() - start_time) * 1000
            logger.warning("❌ Member transaction not found ({:.2f}ms)".format(elapsed))
            return None
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error("Error finding member transaction {} ({:.2f}ms): {}".format(card_number, elapsed, str(e)))
            return None
    
    def _preload_active_members(self):
        """Preload active members into cache"""
        try:
            if not self.member_cache_enabled:
                return 0
                
            logger.info("Preloading active members into cache...")
            start_time = time.time()
            
            members_list = []
            
            if self.views_initialized and not hasattr(self.local_db, 'docs'):
                # Use optimized view for real database
                try:
                    result = self.local_db.view('members/active_members', include_docs=True)
                    for row in result:
                        doc = row.doc if hasattr(row, 'doc') else row.value
                        if (doc and doc.get('type') == 'member_entry' and 
                            doc.get('status') == 0 and doc.get('card_number')):
                            members_list.append(doc)
                except Exception as e:
                    logger.warning("Failed to use view for preload: {}".format(str(e)))
            
            if not members_list:
                # Fallback to manual search
                try:
                    result = self.local_db.view('transactions/active_transactions')
                    for row in result:
                        doc = row.value
                        if (doc and doc.get('type') == 'member_entry' and 
                            doc.get('status') == 0 and doc.get('card_number')):
                            members_list.append(doc)
                except Exception as e:
                    logger.warning("Failed manual preload: {}".format(str(e)))
            
            # Preload into cache
            count = member_cache.preload_members(members_list)
            
            elapsed = (time.time() - start_time) * 1000
            logger.info("✅ Preloaded {} active members ({:.2f}ms)".format(count, elapsed))
            return count
            
        except Exception as e:
            logger.error("Failed to preload members: {}".format(str(e)))
            return 0
    
    def create_member_transaction_optimized(self, card_number, plat_nomor, id_member, member_name=None):
        """Create member transaction dengan optimized ID pattern"""
        try:
            # Use optimized ID pattern untuk fast lookup
            doc_id = "member_{}".format(card_number)
            
            transaction = {
                '_id': doc_id,
                'type': 'member_entry',
                'card_number': card_number,
                'plat_nomor': plat_nomor,
                'id_member': id_member,
                'member_name': member_name or "Member {}".format(id_member),
                'waktu_masuk': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'entry_time': time.strftime('%Y-%m-%dT%H:%M:%S'),
                'status': 0,
                'created_at': time.time(),
                'updated_at': time.time()
            }
            
            # Save to database
            self.local_db.save(transaction)
            
            # Cache the new transaction
            if self.member_cache_enabled:
                member_cache.put(card_number, transaction)
            
            logger.info("✅ Created optimized member transaction: {}".format(doc_id))
            return transaction
            
        except Exception as e:
            logger.error("Failed to create member transaction: {}".format(str(e)))
            return None
    
    def update_transaction_status(self, transaction, operator="SYSTEM", gate_id="EXIT_GATE_01", exit_image_data=None):
        """
        Unified method untuk update status transaksi dari 0 ke 1 (exit)
        Digunakan untuk member_entry dan parking_transaction
        """
        try:
            if not transaction:
                return {
                    'success': False,
                    'message': 'Transaction not provided',
                    'error_code': 'TRANSACTION_NULL'
                }
            
            # Check if already exited
            if transaction.get('status') != 0:
                transaction_type = "Member" if transaction.get('type') == 'member_entry' else "Vehicle"
                exit_time = transaction.get('waktu_keluar', 'Unknown')
                return {
                    'success': False,
                    'message': '{} already exited at: {}'.format(transaction_type, exit_time),
                    'error_code': 'ALREADY_EXITED',
                    'transaction': transaction
                }
            
            # Calculate fee (0 for members, calculated for parking)
            exit_time = datetime.datetime.now()
            if transaction.get('type') == 'member_entry':
                fee = 0  # Members don't pay fees
            else:
                fee = self.calculate_parking_fee(transaction, exit_time)
            
            # Common update fields for both transaction types
            transaction['status'] = 1
            transaction['waktu_keluar'] = exit_time.isoformat()
            transaction['bayar_keluar'] = fee
            transaction['id_pintu_keluar'] = gate_id
            transaction['id_op_keluar'] = operator
            transaction['id_shift_keluar'] = 'SHIFT_001'  # Default shift
            transaction['exit_processed_at'] = time.time()
            transaction['updated_at'] = time.time()
            transaction['status_transaksi'] = "1"
            
            # Additional fields for member transactions
            if transaction.get('type') == 'member_entry':
                transaction['exit_time'] = exit_time.isoformat()
                transaction['operator'] = operator
                transaction['gate_id'] = gate_id
            
            # Save to database
            self.local_db.save(transaction)
            
            # Add exit image as attachment if provided
            if exit_image_data:
                image_success = self.add_image_to_transaction(transaction['_id'], 'exit.jpg', exit_image_data)
                if image_success:
                    logger.info("Added exit image to transaction")
                else:
                    logger.warning("Failed to add exit image to transaction")
            
            # Invalidate member cache if it's a member transaction
            if transaction.get('type') == 'member_entry' and self.member_cache_enabled:
                card_number = transaction.get('card_number')
                if card_number:
                    member_cache.invalidate(card_number)
            
            transaction_type = "member" if transaction.get('type') == 'member_entry' else "parking"
            duration_hours = self._calculate_duration_hours(transaction, exit_time)
            
            logger.info("✅ Updated {} transaction status to exited: {} (fee: {})".format(
                transaction_type, transaction['_id'], fee))
            
            return {
                'success': True,
                'message': '{} transaction processed successfully'.format(transaction_type.title()),
                'transaction': transaction,
                'transaction_type': transaction_type,
                'fee': fee,
                'duration_hours': duration_hours,
                'exit_time': exit_time.isoformat()
            }
            
        except Exception as e:
            logger.error("Error updating transaction status: {}".format(str(e)))
            return {
                'success': False,
                'message': 'System error: {}'.format(str(e)),
                'error_code': 'SYSTEM_ERROR'
            }
    
    def process_member_exit_optimized(self, card_number, operator="SYSTEM", gate_id="EXIT_GATE_01"):
        """Process member exit dengan optimized lookup - menggunakan unified update method"""
        try:
            start_time = time.time()
            
            # Find transaction using optimized method
            transaction = self.find_member_transaction_optimized(card_number)
            
            if not transaction:
                return {
                    'success': False,
                    'message': 'Member transaction not found for card: {}'.format(card_number),
                    'error_code': 'TRANSACTION_NOT_FOUND'
                }
            
            # Use unified update method
            result = self.update_transaction_status(transaction, operator, gate_id)
            
            # Add timing information
            elapsed = (time.time() - start_time) * 1000
            result['processing_time_ms'] = elapsed
            
            if result['success']:
                logger.info("✅ Processed member exit: {} ({:.2f}ms)".format(card_number, elapsed))
            
            return result
            
        except Exception as e:
            logger.error("Error processing member exit: {}".format(str(e)))
            return {
                'success': False,
                'message': 'System error: {}'.format(str(e)),
                'error_code': 'SYSTEM_ERROR'
            }
    
    def invalidate_member_cache(self, card_number=None):
        """Invalidate member cache"""
        if self.member_cache_enabled:
            member_cache.invalidate(card_number)
            if card_number:
                logger.info("Invalidated cache for member: {}".format(card_number))
            else:
                logger.info("Invalidated entire member cache")
    
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
    

    def process_vehicle_exit(self, plate_or_barcode, operator_id, gate_id, exit_image_data=None):
        """Comprehensive exit processing method dengan member optimization - menggunakan unified update"""
        try:
            logger.info("Processing vehicle exit for: {}".format(plate_or_barcode))
            
            if not self.local_db:
                return {
                    'success': False,
                    'message': 'Database not connected',
                    'fee': 0,
                    'error_code': 'DB_NOT_CONNECTED'
                }
            
            # Find transaction by different methods
            transaction = None
            search_method = None
            processing_time = 0
            
            start_time = time.time()
            
            # Try barcode search first (untuk parking transactions)
            transaction = self.find_transaction_by_barcode(plate_or_barcode)
            if transaction:
                search_method = 'barcode'
                processing_time = (time.time() - start_time) * 1000
                logger.info("Found transaction by barcode ({:.2f}ms)".format(processing_time))
            else:
                # Try member card search (optimized lookup)
                member_start = time.time()
                transaction = self.find_member_transaction_optimized(plate_or_barcode)
                if transaction:
                    search_method = 'member_card'
                    processing_time = (time.time() - member_start) * 1000
                    logger.info("Found transaction by member card ({:.2f}ms)".format(processing_time))
                else:
                    # Try plate number search
                    plate_start = time.time()
                    transaction = self.find_transaction_by_plate(plate_or_barcode)
                    if transaction:
                        search_method = 'plate'
                        processing_time = (time.time() - plate_start) * 1000
                        logger.info("Found transaction by plate number ({:.2f}ms)".format(processing_time))
            
            total_search_time = (time.time() - start_time) * 1000
            
            if not transaction:
                logger.warning("No transaction found for: {}".format(plate_or_barcode))
                return {
                    'success': False,
                    'message': 'No active transaction found for: {}'.format(plate_or_barcode),
                    'fee': 0,
                    'error_code': 'TRANSACTION_NOT_FOUND',
                    'search_methods_tried': ['barcode', 'member_card', 'plate'],
                    'search_time_ms': total_search_time
                }
            
            # Use unified update method
            update_result = self.update_transaction_status(transaction, operator_id, gate_id, exit_image_data)
            
            total_processing_time = (time.time() - start_time) * 1000
            
            # Add search-specific information to result
            update_result['search_method'] = search_method
            update_result['search_time_ms'] = total_search_time
            update_result['total_processing_time_ms'] = total_processing_time
            update_result['exit_input'] = plate_or_barcode
            update_result['transaction_id'] = transaction['_id']
            
            if update_result['success']:
                logger.info("Vehicle exit processed successfully for: {}".format(plate_or_barcode))
            
            return update_result
            
        except Exception as e:
            total_time = (time.time() - start_time) * 1000 if 'start_time' in locals() else 0
            error_msg = "System error processing exit: {}".format(str(e))
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'fee': 0,
                'error_code': 'SYSTEM_ERROR',
                'exception': str(e),
                'total_processing_time_ms': total_time
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
    
    def create_test_member_entry(self, card_number, plate_number=None, member_name=None):
        """Create a test member entry for debugging dengan optimized pattern"""
        try:
            if not self.local_db:
                logger.error("Database not connected")
                return False
            
            # Generate test member entry with optimized ID pattern
            now = datetime.datetime.now()
            transaction_id = "member_{}".format(card_number)  # Optimized pattern
            
            member_entry = {
                '_id': transaction_id,
                'type': 'member_entry',
                'card_number': card_number,
                'plat_nomor': plate_number or "MEMBER{}".format(card_number[-3:]),
                'id_member': 'MEMBER_TEST_{}'.format(card_number),
                'member_name': member_name or 'Test Member {}'.format(card_number),
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
            
            # Cache the test member
            if self.member_cache_enabled:
                member_cache.put(card_number, member_entry)
            
            logger.info("Created test member entry: {} (optimized pattern)".format(transaction_id))
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
