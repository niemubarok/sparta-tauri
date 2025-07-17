#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for barcode checking and database functionality
"""

from __future__ import print_function
import sys
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection():
    """Test database connection"""
    try:
        from database_service import db_service
        
        print("=" * 50)
        print("TESTING DATABASE CONNECTION")
        print("=" * 50)
        
        # Check connection status
        sync_status = db_service.get_sync_status()
        print("Database connected: {}".format(sync_status['connected']))
        
        if sync_status['connected']:
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed: {}".format(sync_status.get('error_message', 'Unknown error')))
            
        return sync_status['connected']
        
    except Exception as e:
        print("❌ Database connection test failed: {}".format(str(e)))
        return False

def create_test_data():
    """Create test transactions"""
    try:
        from database_service import db_service
        
        print("\n" + "=" * 50)
        print("CREATING TEST DATA")
        print("=" * 50)
        
        # Create test transactions
        test_barcodes = [
            "TEST001",
            "TEST002", 
            "ABC123",
            "XYZ789",
            "MEMBER001"
        ]
        
        success_count = 0
        
        for i, barcode in enumerate(test_barcodes):
            if i < 3:
                # Create parking transactions
                success = db_service.create_test_transaction(barcode, "B{}TEST".format(i+1))
                if success:
                    print("✅ Created test parking transaction: {}".format(barcode))
                    success_count += 1
                else:
                    print("❌ Failed to create test transaction: {}".format(barcode))
            else:
                # Create member entries
                success = db_service.create_test_member_entry(barcode, "M{}TEST".format(i-2))
                if success:
                    print("✅ Created test member entry: {}".format(barcode))
                    success_count += 1
                else:
                    print("❌ Failed to create test member entry: {}".format(barcode))
        
        print("\nCreated {}/{} test transactions".format(success_count, len(test_barcodes)))
        return success_count > 0
        
    except Exception as e:
        print("❌ Test data creation failed: {}".format(str(e)))
        return False

def test_barcode_search():
    """Test barcode search functionality"""
    try:
        from database_service import db_service
        
        print("\n" + "=" * 50)
        print("TESTING BARCODE SEARCH")
        print("=" * 50)
        
        test_barcodes = [
            "TEST001",
            "TEST002", 
            "ABC123",
            "XYZ789",
            "MEMBER001",
            "NOTFOUND"  # This should not be found
        ]
        
        for barcode in test_barcodes:
            print("\nSearching for barcode: {}".format(barcode))
            print("-" * 30)
            
            # Test find_transaction_by_barcode
            transaction = db_service.find_transaction_by_barcode(barcode)
            
            if transaction:
                print("✅ Found transaction:")
                print("  - ID: {}".format(transaction.get('_id')))
                print("  - Type: {}".format(transaction.get('type')))
                print("  - Status: {}".format(transaction.get('status')))
                print("  - Plate: {}".format(transaction.get('no_pol') or transaction.get('plat_nomor')))
                print("  - Entry Time: {}".format(transaction.get('waktu_masuk') or transaction.get('entry_time')))
            else:
                if barcode == "NOTFOUND":
                    print("✅ Correctly found no transaction (expected)")
                else:
                    print("❌ No transaction found")
        
        return True
        
    except Exception as e:
        print("❌ Barcode search test failed: {}".format(str(e)))
        return False

def test_vehicle_exit_processing():
    """Test vehicle exit processing"""
    try:
        from database_service import db_service
        
        print("\n" + "=" * 50)
        print("TESTING VEHICLE EXIT PROCESSING")
        print("=" * 50)
        
        test_cases = [
            "TEST001",  # Should work
            "ABC123",   # Should work
            "MEMBER001", # Should work
            "NOTFOUND"   # Should fail
        ]
        
        for barcode in test_cases:
            print("\nProcessing exit for: {}".format(barcode))
            print("-" * 30)
            
            # Process vehicle exit
            result = db_service.process_vehicle_exit(barcode, "TEST_OPERATOR", "EXIT_GATE_01")
            
            print("Success: {}".format(result['success']))
            print("Message: {}".format(result['message']))
            print("Fee: {}".format(result['fee']))
            
            if result['success']:
                print("✅ Exit processing successful")
                if 'duration_hours' in result:
                    print("  - Duration: {} hours".format(result['duration_hours']))
                if 'transaction_id' in result:
                    print("  - Transaction ID: {}".format(result['transaction_id']))
            else:
                print("❌ Exit processing failed")
                if 'error_code' in result:
                    print("  - Error Code: {}".format(result['error_code']))
        
        return True
        
    except Exception as e:
        print("❌ Vehicle exit processing test failed: {}".format(str(e)))
        return False

def test_duplicate_exit():
    """Test duplicate exit processing"""
    try:
        from database_service import db_service
        
        print("\n" + "=" * 50)
        print("TESTING DUPLICATE EXIT PROCESSING")
        print("=" * 50)
        
        barcode = "TEST002"  # Use a test barcode
        
        print("First exit attempt for: {}".format(barcode))
        result1 = db_service.process_vehicle_exit(barcode, "TEST_OPERATOR", "EXIT_GATE_01")
        print("First attempt success: {}".format(result1['success']))
        
        print("\nSecond exit attempt for: {} (should fail)".format(barcode))
        result2 = db_service.process_vehicle_exit(barcode, "TEST_OPERATOR", "EXIT_GATE_01")
        print("Second attempt success: {}".format(result2['success']))
        print("Message: {}".format(result2['message']))
        
        if result1['success'] and not result2['success']:
            print("✅ Duplicate exit prevention working correctly")
            return True
        else:
            print("❌ Duplicate exit prevention failed")
            return False
        
    except Exception as e:
        print("❌ Duplicate exit test failed: {}".format(str(e)))
        return False

def list_active_transactions():
    """List all active transactions"""
    try:
        from database_service import db_service
        
        print("\n" + "=" * 50)
        print("LISTING ACTIVE TRANSACTIONS")
        print("=" * 50)
        
        transactions = db_service.list_active_transactions(20)
        
        if transactions:
            print("Found {} active transactions:".format(len(transactions)))
            for i, trans in enumerate(transactions, 1):
                print("{}. ID: {} | Barcode: {} | Plate: {} | Test: {}".format(
                    i, 
                    trans['id'], 
                    trans['barcode'], 
                    trans['plate'],
                    trans['test']
                ))
        else:
            print("No active transactions found")
        
        return True
        
    except Exception as e:
        print("❌ Failed to list active transactions: {}".format(str(e)))
        return False

def cleanup_test_data():
    """Clean up test data"""
    try:
        from database_service import db_service
        
        print("\n" + "=" * 50)
        print("CLEANING UP TEST DATA")
        print("=" * 50)
        
        success = db_service.cleanup_test_transactions()
        
        if success:
            print("✅ Test data cleanup completed")
        else:
            print("❌ Test data cleanup failed")
        
        return success
        
    except Exception as e:
        print("❌ Cleanup failed: {}".format(str(e)))
        return False

def interactive_test():
    """Interactive barcode testing"""
    try:
        from database_service import db_service
        
        print("\n" + "=" * 50)
        print("INTERACTIVE BARCODE TEST")
        print("=" * 50)
        print("Enter barcodes to test (type 'exit' to quit):")
        
        while True:
            try:
                barcode = input("\nEnter barcode: ").strip().upper()
                
                if barcode.lower() == 'exit':
                    break
                
                if not barcode:
                    continue
                
                print("\nTesting barcode: {}".format(barcode))
                print("-" * 30)
                
                # Get transaction info
                info = db_service.get_transaction_info(barcode)
                
                if info:
                    print("✅ Transaction found:")
                    for key, value in info.items():
                        if key != 'full_doc':
                            print("  - {}: {}".format(key, value))
                else:
                    print("❌ No transaction found")
                
                # Ask if user wants to process exit
                if info and info.get('status') == 0:
                    process = input("\nProcess exit for this transaction? (y/n): ").strip().lower()
                    if process == 'y':
                        result = db_service.process_vehicle_exit(barcode, "INTERACTIVE_TEST", "EXIT_GATE_01")
                        print("\nExit processing result:")
                        print("Success: {}".format(result['success']))
                        print("Message: {}".format(result['message']))
                        if result['success']:
                            print("Fee: {}".format(result['fee']))
                            print("Duration: {} hours".format(result.get('duration_hours', 0)))
                
            except KeyboardInterrupt:
                print("\n\nExiting interactive test...")
                break
            except Exception as e:
                print("Error in interactive test: {}".format(str(e)))
        
        return True
        
    except Exception as e:
        print("❌ Interactive test failed: {}".format(str(e)))
        return False

def main():
    """Main test function"""
    print("BARCODE DATABASE TEST SUITE")
    print("=" * 50)
    
    try:
        # Test database connection
        if not test_database_connection():
            print("\n❌ Cannot proceed without database connection")
            return
        
        # Run tests
        tests = [
            ("Database Connection", test_database_connection),
            ("Create Test Data", create_test_data),
            ("List Active Transactions", list_active_transactions),
            ("Barcode Search", test_barcode_search),
            ("Vehicle Exit Processing", test_vehicle_exit_processing),
            ("Duplicate Exit Prevention", test_duplicate_exit),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                print("\n")
                success = test_func()
                results[test_name] = success
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print("❌ Test '{}' failed with exception: {}".format(test_name, str(e)))
                results[test_name] = False
        
        # Summary
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results.items():
            status = "PASS" if success else "FAIL"
            icon = "✅" if success else "❌"
            print("{} {}: {}".format(icon, test_name, status))
            if success:
                passed += 1
        
        print("\nOverall: {}/{} tests passed".format(passed, total))
        
        # Ask for interactive test
        print("\n" + "=" * 50)
        interactive = input("Run interactive barcode test? (y/n): ").strip().lower()
        if interactive == 'y':
            interactive_test()
        
        # Ask for cleanup
        cleanup = input("\nClean up test data? (y/n): ").strip().lower()
        if cleanup == 'y':
            cleanup_test_data()
        
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print("\n❌ Test suite failed: {}".format(str(e)))

if __name__ == "__main__":
    main()
