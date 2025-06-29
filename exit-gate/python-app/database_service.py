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
            self._sync_status['connected'] = False
            self._sync_status['error_message'] = str(e)
    
    def _setup_views(self):
        """Setup CouchDB views for efficient querying"""
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
        """Find transaction by barcode"""
        try:
            # First try direct lookup by transaction ID
            transaction_id = "transaction_{}".format(barcode)
            try:
                doc = self.local_db[transaction_id]
                if doc.get('status') == 0 and doc.get('type') in ['parking_transaction', 'member_entry']:
                    return doc
            except couchdb.ResourceNotFound:
                pass
            
            # Then try barcode view
            try:
                result = self.local_db.view('transactions/by_barcode', key=barcode)
                for row in result:
                    if row.value.get('status') == 0:
                        return row.value
            except:
                pass
            
            # Finally scan all active transactions
            try:
                result = self.local_db.view('transactions/active_transactions')
                for row in result:
                    doc = row.value
                    if (doc.get('_id') == transaction_id or 
                        doc.get('no_barcode') == barcode):
                        return doc
            except:
                pass
            
            return None
            
        except Exception as e:
            logger.error("Error finding transaction by barcode {}: {}".format(barcode, str(e)))
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
    
    def process_vehicle_exit(self, plate_or_barcode, operator_id, gate_id):
        """Comprehensive exit processing method"""
        try:
            # Find transaction
            transaction = self.find_transaction_by_barcode(plate_or_barcode)
            if not transaction:
                transaction = self.find_transaction_by_plate(plate_or_barcode)
            
            if not transaction:
                return {
                    'success': False,
                    'message': 'Transaction not found for: {}'.format(plate_or_barcode),
                    'fee': 0
                }
            
            # Check if already exited
            if transaction.get('status') == 1:
                return {
                    'success': False,
                    'message': 'Vehicle already exited',
                    'fee': 0
                }
            
            # Calculate fee
            exit_time = datetime.datetime.now()
            fee = self.calculate_parking_fee(transaction, exit_time)
            
            # Prepare exit data
            exit_data = {
                'waktu_keluar': exit_time.isoformat(),
                'bayar_keluar': fee,
                'id_pintu_keluar': gate_id,
                'id_op_keluar': operator_id,
                'id_shift_keluar': 'SHIFT_001'  # Default shift
            }
            
            # Update transaction
            success = self.exit_transaction(transaction['_id'], exit_data)
            
            if success:
                return {
                    'success': True,
                    'message': 'Vehicle exit processed successfully',
                    'fee': fee,
                    'transaction': transaction,
                    'duration_hours': self._calculate_duration_hours(transaction, exit_time)
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to update transaction',
                    'fee': fee
                }
            
        except Exception as e:
            logger.error("Error processing vehicle exit: {}".format(str(e)))
            return {
                'success': False,
                'message': 'System error: {}'.format(str(e)),
                'fee': 0
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

# Global database service instance
db_service = DatabaseService()
