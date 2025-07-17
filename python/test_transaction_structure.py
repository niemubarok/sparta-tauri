#!/usr/bin/env python3
"""
Test script for new transaction structure
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.config import Config
from shared.database import DatabaseService

def test_new_transaction_structure():
    """Test the new transaction structure"""
    print("Testing new transaction structure...")
    
    # Initialize services
    config = Config()
    db = DatabaseService(config)
    
    # Test entry transaction
    entry_data = {
        "license_plate": "B1234TEST",
        "vehicle_type": "Car",
        "is_member": False,
        "member_card": None,
        "transaction_type": "entry",
        "gate_id": "ENTRY_GATE_01",
        "operator_id": "SYSTEM",
        "shift_id": "S1",
        "entry_fee": 2000,
        "system_type": "PREPAID"
    }
    
    try:
        # Save transaction
        doc_id = db.save_transaction(entry_data)
        print(f"✅ Entry transaction saved: {doc_id}")
        
        # Retrieve and display
        transaction = db.get_transaction(doc_id)
        if transaction:
            print(f"✅ Transaction retrieved successfully")
            print(f"   ID: {transaction.get('id')}")
            print(f"   Plate: {transaction.get('no_pol')}")
            print(f"   Vehicle Type ID: {transaction.get('id_kendaraan')}")
            print(f"   Category: {transaction.get('kategori')}")
            print(f"   Entry Fee: {transaction.get('bayar_masuk')}")
            print(f"   Entry Time: {transaction.get('waktu_masuk')}")
            print(f"   Type: {transaction.get('type')}")
        else:
            print("❌ Failed to retrieve transaction")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test exit transaction
    print("\nTesting exit transaction...")
    exit_data = {
        "license_plate": "B1234TEST",
        "vehicle_type": "Car",
        "is_member": False,
        "transaction_type": "exit",
        "exit_gate_id": "EXIT_GATE_01",
        "exit_operator_id": "SYSTEM",
        "exit_shift_id": "SHIFT_001",
        "exit_fee": 5000,
        "exit_method": "alpr",
        "exit_input": "B1234TEST"
    }
    
    try:
        doc_id = db.save_transaction(exit_data)
        print(f"✅ Exit transaction saved: {doc_id}")
        
        transaction = db.get_transaction(doc_id)
        if transaction:
            print(f"✅ Exit transaction structure:")
            print(f"   Exit Time: {transaction.get('waktu_keluar')}")
            print(f"   Exit Fee: {transaction.get('bayar_keluar')}")
            print(f"   Exit Method: {transaction.get('exit_method')}")
            print(f"   Status: {transaction.get('status_transaksi')}")
        
    except Exception as e:
        print(f"❌ Exit transaction error: {e}")

if __name__ == "__main__":
    test_new_transaction_structure()
