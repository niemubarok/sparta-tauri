#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Member Database Views untuk optimasi performance
CouchDB view definitions untuk member card lookup
"""

from __future__ import absolute_import, print_function, unicode_literals

# Design documents untuk CouchDB views
MEMBER_VIEWS = {
    "_id": "_design/members",
    "views": {
        # View untuk pencarian member berdasarkan card_number
        "by_card_number": {
            "map": """
            function(doc) {
                if (doc.type === 'member_entry' && doc.card_number) {
                    emit(doc.card_number, doc);
                }
            }
            """
        },
        
        # View untuk active member transactions
        "active_members": {
            "map": """
            function(doc) {
                if (doc.type === 'member_entry' && doc.status === 0 && doc.card_number) {
                    emit(doc.card_number, {
                        _id: doc._id,
                        card_number: doc.card_number,
                        plat_nomor: doc.plat_nomor,
                        id_member: doc.id_member,
                        member_name: doc.member_name,
                        waktu_masuk: doc.waktu_masuk,
                        entry_time: doc.entry_time,
                        status: doc.status,
                        type: doc.type
                    });
                }
            }
            """
        },
        
        # View untuk member by plate number
        "by_plate_number": {
            "map": """
            function(doc) {
                if (doc.type === 'member_entry' && doc.plat_nomor) {
                    emit(doc.plat_nomor.toLowerCase(), doc);
                }
            }
            """
        },
        
        # Composite view untuk card_number + status
        "by_card_and_status": {
            "map": """
            function(doc) {
                if (doc.type === 'member_entry' && doc.card_number) {
                    emit([doc.card_number, doc.status], doc);
                }
            }
            """
        },
        
        # View untuk member by ID
        "by_member_id": {
            "map": """
            function(doc) {
                if (doc.type === 'member_entry' && doc.id_member) {
                    emit(doc.id_member, doc);
                }
            }
            """
        }
    }
}

# Enhanced transaction views dengan member support
TRANSACTION_VIEWS_ENHANCED = {
    "_id": "_design/transactions_enhanced",
    "views": {
        # Enhanced identifier view - supports both barcode and card
        "by_identifier": {
            "map": """
            function(doc) {
                if (doc.type === 'parking_transaction' && doc.no_barcode) {
                    emit(doc.no_barcode, doc);
                    emit('barcode_' + doc.no_barcode, doc);
                }
                if (doc.type === 'member_entry' && doc.card_number) {
                    emit(doc.card_number, doc);
                    emit('card_' + doc.card_number, doc);
                }
            }
            """
        },
        
        # Active transactions dengan type indicator
        "active_by_type": {
            "map": """
            function(doc) {
                if (doc.status === 0) {
                    if (doc.type === 'parking_transaction' && doc.no_barcode) {
                        emit(['barcode', doc.no_barcode], doc);
                    }
                    if (doc.type === 'member_entry' && doc.card_number) {
                        emit(['member', doc.card_number], doc);
                    }
                }
            }
            """
        },
        
        # Universal search view - search by any identifier
        "universal_search": {
            "map": """
            function(doc) {
                if (doc.type === 'parking_transaction') {
                    if (doc.no_barcode) emit(['parking', 'barcode', doc.no_barcode], doc);
                    if (doc.no_pol) emit(['parking', 'plate', doc.no_pol.toLowerCase()], doc);
                    if (doc._id) emit(['parking', 'id', doc._id], doc);
                }
                if (doc.type === 'member_entry') {
                    if (doc.card_number) emit(['member', 'card', doc.card_number], doc);
                    if (doc.plat_nomor) emit(['member', 'plate', doc.plat_nomor.toLowerCase()], doc);
                    if (doc.id_member) emit(['member', 'member_id', doc.id_member], doc);
                    if (doc._id) emit(['member', 'id', doc._id], doc);
                }
            }
            """
        }
    }
}

# Index definitions untuk optimasi query
MEMBER_INDEXES = [
    {
        "index": {
            "fields": ["type", "card_number", "status"]
        },
        "name": "member-card-status-index",
        "type": "json"
    },
    {
        "index": {
            "fields": ["type", "plat_nomor", "status"]
        },
        "name": "member-plate-status-index", 
        "type": "json"
    },
    {
        "index": {
            "fields": ["type", "status", "waktu_masuk"]
        },
        "name": "member-status-time-index",
        "type": "json"
    },
    {
        "index": {
            "fields": ["card_number"]
        },
        "name": "card-number-index",
        "type": "json"
    }
]
