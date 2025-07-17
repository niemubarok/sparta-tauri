#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script untuk verifikasi image attachment functionality
"""

from database_service import DatabaseService
import time

def test_image_attachments():
    """Test image attachment functionality"""
    print("=== Testing Image Attachment Functionality ===")
    
    # Initialize database service
    db_service = DatabaseService()
    
    if not db_service.get_sync_status()['connected']:
        print("❌ Database not connected")
        return
    
    print("✅ Database connected")
    
    # Test 1: Create transaction with entry image
    test_barcode = "IMGTEST{}".format(int(time.time()) % 1000)
    print("\n1. Testing transaction creation with entry image...")
    print("Test barcode:", test_barcode)
    
    # Generate sample entry image
    entry_image = db_service.generate_sample_image_data('entry')
    if entry_image:
        print("✅ Sample entry image generated")
    else:
        print("❌ Failed to generate sample entry image")
        return
    
    # Create test transaction
    success = db_service.create_test_transaction(test_barcode, "IMGTEST", entry_image)
    if success:
        print("✅ Test transaction created with entry image")
    else:
        print("❌ Failed to create test transaction")
        return
    
    # Test 2: Verify transaction exists and has attachment
    print("\n2. Verifying transaction and attachment...")
    transaction = db_service.find_transaction_by_barcode(test_barcode)
    if transaction:
        print("✅ Transaction found:", transaction['_id'])
        
        # Check for attachments
        attachments = transaction.get('_attachments', {})
        if attachments:
            print("✅ Attachments found:", list(attachments.keys()))
            
            if 'entry.jpg' in attachments:
                print("✅ entry.jpg attachment exists")
                entry_info = attachments['entry.jpg']
                print("   - Content type:", entry_info.get('content_type'))
                print("   - Length:", entry_info.get('length', 'Unknown'))
            else:
                print("❌ entry.jpg attachment missing")
        else:
            print("❌ No attachments found")
    else:
        print("❌ Transaction not found")
        return
    
    # Test 3: Process exit with exit image
    print("\n3. Testing exit processing with exit image...")
    
    # Generate sample exit image
    exit_image = db_service.generate_sample_image_data('exit')
    if exit_image:
        print("✅ Sample exit image generated")
    else:
        print("❌ Failed to generate sample exit image")
        return
    
    # Process exit
    result = db_service.process_vehicle_exit(test_barcode, "TEST_OPERATOR", "EXIT_GATE_01", exit_image)
    if result.get('success'):
        print("✅ Exit processing successful")
        print("   - Fee:", result.get('fee'))
        print("   - Duration:", result.get('duration_hours'), "hours")
    else:
        print("❌ Exit processing failed:", result.get('message'))
        return
    
    # Test 4: Verify exit image attachment
    print("\n4. Verifying exit image attachment...")
    transaction = db_service.find_transaction_by_barcode(test_barcode)
    if transaction:
        attachments = transaction.get('_attachments', {})
        if 'exit.jpg' in attachments:
            print("✅ exit.jpg attachment exists")
            exit_info = attachments['exit.jpg']
            print("   - Content type:", exit_info.get('content_type'))
            print("   - Length:", exit_info.get('length', 'Unknown'))
        else:
            print("❌ exit.jpg attachment missing")
            
        # Summary
        all_attachments = list(attachments.keys())
        print("📁 All attachments:", all_attachments)
        print("📊 Total attachments:", len(all_attachments))
    else:
        print("❌ Transaction not found after exit")
    
    print("\n=== Test Summary ===")
    print("Transaction ID:", "transaction_{}".format(test_barcode))
    print("Expected attachments: entry.jpg, exit.jpg")
    print("Vue.js dashboard should display 2 images for this transaction")
    print("\n✅ Image attachment test completed!")

if __name__ == "__main__":
    test_image_attachments()
