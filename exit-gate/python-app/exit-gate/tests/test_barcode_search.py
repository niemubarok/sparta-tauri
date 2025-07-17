#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test barcode search functionality
"""

from database_service import DatabaseService

def test_barcode_search():
    """Test different barcode search scenarios"""
    print("=== Testing Barcode Search ===")
    
    db_service = DatabaseService()
    
    if not db_service.get_sync_status()['connected']:
        print("❌ Database not connected")
        return
    
    print("✅ Database connected")
    
    # Test cases
    test_cases = [
        "IMGTEST971",  # Just the barcode
        "transaction_IMGTEST971",  # Full transaction ID
        "TRANSACTION_IMGTEST971",  # Full ID with different case
    ]
    
    for i, test_barcode in enumerate(test_cases, 1):
        print("\n{}. Testing barcode: '{}'".format(i, test_barcode))
        
        # Test with original method (active only)
        transaction = db_service.find_transaction_by_barcode(test_barcode)
        if transaction:
            print("   ✅ Found with find_transaction_by_barcode:")
            print("      ID: {}".format(transaction['_id']))
            print("      Status: {} ({})".format(
                transaction.get('status'), 
                'Active' if transaction.get('status') == 0 else 'Completed'
            ))
        else:
            print("   ❌ NOT found with find_transaction_by_barcode")
        
        # Test with new method (any status)
        any_transaction = db_service.find_any_transaction_by_barcode(test_barcode)
        if any_transaction:
            print("   ✅ Found with find_any_transaction_by_barcode:")
            print("      ID: {}".format(any_transaction['_id']))
            print("      Status: {} ({})".format(
                any_transaction.get('status'), 
                'Active' if any_transaction.get('status') == 0 else 'Completed'
            ))
        else:
            print("   ❌ NOT found with find_any_transaction_by_barcode")
    
    print("\n" + "="*50)
    print("🔍 Search Method Recommendations:")
    print("✅ find_transaction_by_barcode() - Use for exit processing (active transactions)")
    print("✅ find_any_transaction_by_barcode() - Use for lookup/info (any status)")

if __name__ == "__main__":
    test_barcode_search()
