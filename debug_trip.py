#!/usr/bin/env python3
"""
Debug script to check trip 16 balance calculations
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'expense_tracker'))

from backend.app_factory import create_app
from backend.models.trip import Trip
from backend.models.unregistered_participant import UnregisteredParticipant
from backend.models.user import User
from backend.models.expense import Expense
from backend.database import db

def debug_trip_balances():
    """Debug trip 16 balance calculations"""
    app = create_app()
    
    with app.app_context():
        # Get trip 16
        trip = Trip.query.get(16)
        if not trip:
            print("Trip 16 not found")
            return
        
        print(f"Trip: {trip.name}")
        print(f"Participants: {trip.get_participants_list()}")
        print(f"Admin ID: {trip.admin_id}")
        
        # Get user names
        user_ids = [22, 27, 28, 29, 30] + [trip.admin_id]
        users = User.query.filter(User.id.in_(user_ids)).all()
        user_map = {user.id: user.name for user in users}
        print(f"User map: {user_map}")
        
        # Get advances
        advances = trip.get_advances()
        print(f"Advances: {advances}")
        
        # Get general payments
        general_payments = trip.get_general_payments()
        print(f"General payments: {general_payments}")
        
        # Get all expenses
        expenses = Expense.query.filter_by(trip_id=16).all()
        print(f"\nFound {len(expenses)} expenses:")
        
        for expense in expenses:
            print(f"  Expense {expense.id}: {expense.description} - {expense.amount}")
            print(f"    Payer: {expense.payer_id}")
            print(f"    Participants: {expense.get_participants_list()}")
            print(f"    Shares: {expense.get_shares()}")
            print(f"    Items: {expense.items}")
        
        print("\n--- Balance Calculations ---")
        
        # Calculate balances for each participant
        registered_participants = trip.get_participants_list()
        if str(trip.admin_id) not in registered_participants:
            registered_participants.append(str(trip.admin_id))
        
        print(f"Registered participants: {registered_participants}")
        
        for participant_id in registered_participants:
            balance = trip.calculate_user_balance(participant_id)
            user_name = user_map.get(int(participant_id), f"User {participant_id}")
            print(f"  {user_name} (ID: {participant_id}): {balance}")
        
        # Recalculate all balances
        print("\n--- Recalculating All Balances ---")
        all_balances = trip.recalculate_all_balances()
        for user_id, balance in all_balances.items():
            if user_id.startswith('unregistered_'):
                print(f"  {user_id}: {balance}")
            else:
                user_name = user_map.get(int(user_id), f"User {user_id}")
                print(f"  {user_name} (ID: {user_id}): {balance}")
        
        print("\n--- Settlements ---")
        settlements = trip.calculate_settlements()
        for settlement in settlements:
            from_user = settlement['from_user']
            to_user = settlement['to_user']
            amount = settlement['amount']
            
            if from_user.startswith('unregistered_'):
                from_name = from_user.replace('unregistered_', '')
            else:
                from_name = user_map.get(int(from_user), f"User {from_user}")
                
            if to_user.startswith('unregistered_'):
                to_name = to_user.replace('unregistered_', '')
            else:
                to_name = user_map.get(int(to_user), f"User {to_user}")
                
            print(f"  {from_name} pays {to_name} ₹{amount}")

if __name__ == "__main__":
    debug_trip_balances()