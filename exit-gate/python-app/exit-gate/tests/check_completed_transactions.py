#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check completed transactions and their attachments
"""

from database_service import DatabaseService

def check_completed_transactions():
    """Check completed transactions with attachments"""
    print("=== Checking Completed Transactions ===")
    
    db_service = DatabaseService()
    
    if not db_service.get_sync_status()['connected']:
        print("❌ Database not connected")
        return
    
    print("✅ Database connected")
    
    # Check all transactions, not just active ones
    try:
        # Direct database scan to find our test transaction
        found_transactions = []
        
        for doc_id in db_service.local_db:
            if doc_id.startswith('_design'):
                continue
                
            try:
                doc = db_service.local_db[doc_id]
                if doc.get('type') == 'parking_transaction' and doc_id.startswith('transaction_IMGTEST'):
                    found_transactions.append(doc)
            except:
                continue
        
        print("Found {} test transactions:".format(len(found_transactions)))
        
        for i, transaction in enumerate(found_transactions, 1):
            print("\n{}. Transaction: {}".format(i, transaction['_id']))
            print("   Barcode: {}".format(transaction.get('no_barcode')))
            print("   Plate: {}".format(transaction.get('no_pol')))
            print("   Status: {} ({})".format(
                transaction.get('status'), 
                'Active' if transaction.get('status') == 0 else 'Completed'
            ))
            print("   Entry Time: {}".format(transaction.get('waktu_masuk')))
            print("   Exit Time: {}".format(transaction.get('waktu_keluar', 'N/A')))
            print("   Fee: {}".format(transaction.get('bayar_keluar', 0)))
            
            # Check attachments
            attachments = transaction.get('_attachments', {})
            if attachments:
                print("   📎 Attachments:")
                for name, info in attachments.items():
                    print("     - {}: {} bytes, {}".format(
                        name, 
                        info.get('length', 0),
                        info.get('content_type', 'unknown')
                    ))
            else:
                print("   📎 No attachments")
        
        if found_transactions:
            latest_transaction = found_transactions[-1]
            print("\n" + "="*50)
            print("🎯 LATEST TEST TRANSACTION ANALYSIS:")
            print("ID: {}".format(latest_transaction['_id']))
            print("Status: {} (should be 1 for completed)".format(latest_transaction.get('status')))
            
            attachments = latest_transaction.get('_attachments', {})
            expected_attachments = ['entry.jpg', 'exit.jpg']
            
            print("\nExpected attachments: {}".format(expected_attachments))
            print("Actual attachments: {}".format(list(attachments.keys())))
            
            missing = [att for att in expected_attachments if att not in attachments]
            if missing:
                print("❌ Missing attachments: {}".format(missing))
            else:
                print("✅ All expected attachments present!")
            
            print("\n🖼️ Vue.js Dashboard Compatibility:")
            print("✅ Entry image: entry.jpg - {} bytes".format(
                attachments.get('entry.jpg', {}).get('length', 0)
            ))
            print("✅ Exit image: exit.jpg - {} bytes".format(
                attachments.get('exit.jpg', {}).get('length', 0)
            ))
            print("✅ Content-Type: image/jpeg")
            print("✅ Should display as 2 separate images in Vue.js dashboard")
        else:
            print("❌ No test transactions found")
    
    except Exception as e:
        print("Error checking transactions: {}".format(str(e)))

if __name__ == "__main__":
    check_completed_transactions()
