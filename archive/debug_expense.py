#!/usr/bin/env python3
"""
Debug script to check expense payer_id after linking
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

def debug_expense_payer_id():
    """Debug expense payer_id after linking"""
    app = create_app()
    
    with app.app_context():
        print("=== Debug Expense Payer ID ===")
        
        # Get the test expense we created
        expense = Expense.query.get(64)
        if not expense:
            print("Test expense not found")
            return
        
        print(f"Expense ID: {expense.id}")
        print(f"Current payer_id: {expense.payer_id}")
        print(f"Current participants: {expense.get_participants_list()}")
        print(f"Current shares: {expense.get_shares()}")
        
        # Check if this matches what we expect
        if expense.payer_id == "1":
            print("SUCCESS: payer_id is correctly set to '1'")
        else:
            print(f"ERROR: payer_id is '{expense.payer_id}' but expected '1'")

if __name__ == "__main__":
    debug_expense_payer_id()