#!/usr/bin/env python3
"""
Verification script to confirm that linking updates payer_id correctly
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app_factory import create_app
from backend.models.trip import Trip
from backend.models.unregistered_participant import UnregisteredParticipant
from backend.models.user import User
from backend.models.expense import Expense
from backend.database import db

def verify_payer_id_update():
    """Verify that linking updates payer_id correctly"""
    app = create_app()
    
    with app.app_context():
        print("=== Verify Payer ID Update ===")
        
        # Get the test expense we created
        expense = Expense.query.get(64)
        if not expense:
            print("Test expense not found")
            return
        
        print(f"Expense ID: {expense.id}")
        print(f"Current payer_id: '{expense.payer_id}' (type: {type(expense.payer_id)})")
        
        # Check if this is correctly updated
        if expense.payer_id == "1":
            print("✓ SUCCESS: Expense payer_id was correctly updated to string '1'")
        elif expense.payer_id.startswith("unregistered_"):
            print(f"✗ ERROR: Expense payer_id still shows unregistered participant: {expense.payer_id}")
        else:
            print(f"? INFO: Expense payer_id is '{expense.payer_id}' which is neither '1' nor unregistered")

if __name__ == "__main__":
    verify_payer_id_update()