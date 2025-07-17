#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Barcode Logic
Test untuk memverifikasi logika barcode dengan pattern transaction_{barcode}
"""

from __future__ import absolute_import, print_function, unicode_literals

import sys
import os
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_service import db_service

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_barcode_pattern():
    """Test barcode pattern: transaction_{barcode}"""
    print("=== TEST BARCODE PATTERN ===")
    
    test_barcodes = ["1234", "5678", "ABCD", "TEST001"]
    
    # Cleanup previous test data
    print("Cleaning up previous test transactions...")
    db_service.cleanup_test_transactions()
    
    # Create test transactions
    print("\nCreating test transactions...")
    for barcode in test_barcodes:
        success = db_service.create_test_transaction(barcode, "PLATE{}".format(barcode))
        if success:
            print("✅ Created transaction for barcode: {}".format(barcode))
            print("   Expected _id: transaction_{}".format(barcode))
            print("   Expected no_barcode: {}".format(barcode))
        else:
            print("❌ Failed to create transaction for barcode: {}".format(barcode))
    
    print("\n" + "="*50)
    
    # Test finding transactions
    print("\nTesting barcode search...")
    for barcode in test_barcodes:
        print("\n--- Testing barcode: {} ---".format(barcode))
        
        # Find transaction
        transaction = db_service.find_transaction_by_barcode(barcode)
        
        if transaction:
            doc_id = transaction.get('_id')
            no_barcode = transaction.get('no_barcode')
            
            print("✅ Found transaction:")
            print("   _id: {}".format(doc_id))
            print("   no_barcode: {}".format(no_barcode))
            
            # Verify pattern
            expected_id = "transaction_{}".format(barcode)
            if doc_id == expected_id and no_barcode == barcode:
                print("✅ Pattern verification: PASSED")
            else:
                print("❌ Pattern verification: FAILED")
                print("   Expected _id: {}".format(expected_id))
                print("   Expected no_barcode: {}".format(barcode))
        else:
            print("❌ Transaction not found for barcode: {}".format(barcode))
    
    print("\n" + "="*50)
    
    # Test get_transaction_info
    print("\nTesting get_transaction_info...")
    for barcode in test_barcodes:
        print("\n--- Transaction info for barcode: {} ---".format(barcode))
        
        info = db_service.get_transaction_info(barcode)
        
        if info and info.get('found'):
            print("✅ Transaction info:")
            print("   ID: {}".format(info.get('id')))
            print("   Barcode field: {}".format(info.get('barcode_field')))
            print("   Extracted barcode: {}".format(info.get('extracted_barcode')))
            print("   Type: {}".format(info.get('type')))
            print("   Status: {}".format(info.get('status')))
            print("   Plate: {}".format(info.get('plate')))
            print("   Test transaction: {}".format(info.get('test')))
        else:
            print("❌ No transaction info found")
    
    print("\n" + "="*50)

def test_vehicle_exit_process():
    """Test vehicle exit process"""
    print("\n=== TEST VEHICLE EXIT PROCESS ===")
    
    test_barcode = "EXIT001"
    
    # Create test transaction
    print("Creating test transaction for exit test...")
    success = db_service.create_test_transaction(test_barcode, "EXITPLATE")
    
    if success:
        print("✅ Test transaction created")
        
        # Process exit
        print("\nProcessing vehicle exit...")
        result = db_service.process_vehicle_exit(test_barcode, "OPERATOR_TEST", "EXIT_GATE_01")
        
        print("Exit process result:")
        print("   Success: {}".format(result.get('success')))
        print("   Message: {}".format(result.get('message')))
        print("   Fee: {}".format(result.get('fee')))
        print("   Duration hours: {}".format(result.get('duration_hours')))
        print("   Search method: {}".format(result.get('search_method')))
        print("   Transaction ID: {}".format(result.get('transaction_id')))
        
        if result.get('success'):
            print("✅ Exit process: SUCCESS")
            
            # Verify transaction status
            info = db_service.get_transaction_info(test_barcode)
            if info and info.get('found'):
                if info.get('full_doc', {}).get('status') == 1:
                    print("✅ Transaction status updated to exited")
                else:
                    print("❌ Transaction status not updated")
            
        else:
            print("❌ Exit process: FAILED")
            print("   Error code: {}".format(result.get('error_code')))
    else:
        print("❌ Failed to create test transaction")

def test_edge_cases():
    """Test edge cases"""
    print("\n=== TEST EDGE CASES ===")
    
    # Test non-existent barcode
    print("\n--- Testing non-existent barcode ---")
    result = db_service.process_vehicle_exit("NONEXISTENT", "OPERATOR", "GATE")
    print("Non-existent barcode result:")
    print("   Success: {}".format(result.get('success')))
    print("   Message: {}".format(result.get('message')))
    print("   Error code: {}".format(result.get('error_code')))
    
    # Test already exited transaction
    print("\n--- Testing already exited transaction ---")
    exited_barcode = "EXITED001"
    
    # Create and immediately exit
    db_service.create_test_transaction(exited_barcode, "EXITEDPLATE")
    db_service.process_vehicle_exit(exited_barcode, "OPERATOR", "GATE")
    
    # Try to exit again
    result = db_service.process_vehicle_exit(exited_barcode, "OPERATOR", "GATE")
    print("Already exited result:")
    print("   Success: {}".format(result.get('success')))
    print("   Message: {}".format(result.get('message')))
    print("   Error code: {}".format(result.get('error_code')))

def test_list_active_transactions():
    """Test listing active transactions"""
    print("\n=== TEST LIST ACTIVE TRANSACTIONS ===")
    
    transactions = db_service.list_active_transactions(limit=20)
    
    print("Active transactions found: {}".format(len(transactions)))
    
    for i, transaction in enumerate(transactions):
        print("\n{}. Transaction:".format(i + 1))
        print("   ID: {}".format(transaction.get('id')))
        print("   Type: {}".format(transaction.get('type')))
        print("   Barcode: {}".format(transaction.get('barcode')))
        print("   Plate: {}".format(transaction.get('plate')))
        print("   Entry time: {}".format(transaction.get('entry_time')))
        print("   Test: {}".format(transaction.get('test')))

def main():
    """Main test function"""
    print("BARCODE LOGIC TEST")
    print("Pattern: _id = transaction_{barcode}, no_barcode = {barcode}")
    print("="*60)
    
    try:
        # Run tests
        test_barcode_pattern()
        test_vehicle_exit_process()
        test_edge_cases()
        test_list_active_transactions()
        
        print("\n" + "="*60)
        print("TEST COMPLETED")
        print("Check the results above to verify barcode logic works correctly.")
        
    except Exception as e:
        print("ERROR during testing: {}".format(str(e)))
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup (optional - comment out if you want to keep test data)
        print("\nCleaning up test transactions...")
        db_service.cleanup_test_transactions()
        print("Cleanup completed.")

if __name__ == "__main__":
    main()
