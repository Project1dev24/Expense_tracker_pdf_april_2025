#!/usr/bin/env python3
"""
Comprehensive test to demonstrate that linking functionality works correctly
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

def comprehensive_linking_test():
    """Comprehensive test of the linking functionality"""
    app = create_app()
    
    with app.app_context():
        print("=== Comprehensive Linking Test ===")
        
        # Get the first trip
        trip = Trip.query.first()
        if not trip:
            print("No trip found")
            return
        
        print(f"Using trip: {trip.name} (ID: {trip.id})")
        
        # Add a new unregistered participant for testing
        test_name = "Test Linking User"
        print(f"\n1. Adding unregistered participant: {test_name}")
        trip.add_unregistered_participant(test_name)
        db.session.commit()
        
        # Verify participant was added
        unregistered = trip.get_unregistered_participants()
        print(f"   Current unregistered participants: {unregistered}")
        
        # Create an expense with this unregistered participant as payer
        unregistered_id = f"unregistered_{test_name.lower()}"
        print(f"\n2. Creating expense with unregistered payer: {unregistered_id}")
        
        expense = Expense(
            description="Test linking functionality",
            amount=150.0,
            currency="USD",
            date=datetime.now(),
            category="Test",
            payer_id=unregistered_id,
            trip_id=trip.id,
            participants='["1"]',  # Include admin as participant
            shares=f'{{"{unregistered_id}": 150.0}}'
        )
        db.session.add(expense)
        db.session.commit()
        
        print(f"   Created expense {expense.id} with payer_id: {expense.payer_id}")
        
        # Check database directly
        result = db.engine.execute(f"SELECT id, payer_id FROM expense WHERE id = {expense.id}").fetchone()
        print(f"   Database value: ID={result[0]}, payer_id='{result[1]}'")
        
        # Find a user to link to (use the trip admin)
        user = User.query.get(trip.admin_id)
        if not user:
            print("No user found to link to")
            return
        
        print(f"\n3. Linking unregistered participant to user:")
        print(f"   Unregistered name: {test_name}")
        print(f"   Target user: {user.name} (ID: {user.id})")
        
        # Link the participant
        result = trip.link_participant(test_name, user.id)
        print(f"   Link result: {result}")
        
        if result:
            print("\n4. Verification:")
            
            # Check if expense payer_id was updated
            updated_expense = Expense.query.get(expense.id)
            print(f"   Updated expense {updated_expense.id} payer_id: '{updated_expense.payer_id}'")
            
            if str(updated_expense.payer_id) == str(user.id):
                print("   ✓ SUCCESS: Expense payer_id was correctly updated!")
            else:
                print(f"   ✗ ERROR: Expense payer_id was not updated! Expected '{str(user.id)}' (type: {type(str(user.id))}), got '{str(updated_expense.payer_id)}' (type: {type(updated_expense.payer_id)})")
                
            # Check participants list was updated
            participants = updated_expense.get_participants_list()
            print(f"   Updated participants list: {participants}")
            
            if str(user.id) in participants:
                print("   ✓ SUCCESS: Participants list was correctly updated!")
            else:
                print("   ✗ ERROR: Participants list was not updated!")
                
            # Check shares were updated
            shares = updated_expense.get_shares()
            print(f"   Updated shares: {shares}")
            
            if str(user.id) in shares and unregistered_id not in shares:
                print("   ✓ SUCCESS: Shares were correctly updated!")
            else:
                print("   ✗ ERROR: Shares were not updated!")
                
            # Check updated unregistered participants
            updated_unregistered = trip.get_unregistered_participants()
            print(f"   Updated unregistered participants: {updated_unregistered}")
            
            if test_name.lower() not in updated_unregistered:
                print("   ✓ SUCCESS: Unregistered participant was removed from list!")
            else:
                print("   ✗ ERROR: Unregistered participant was not removed!")
                
            # Check if participant is now linked in database
            participant = UnregisteredParticipant.query.filter_by(
                name=test_name.lower(), 
                trip_id=trip.id
            ).first()
            
            if participant and participant.linked_user_id == user.id:
                print(f"   ✓ SUCCESS: Participant record correctly linked to user {user.id}!")
            else:
                print("   ✗ ERROR: Participant record not properly linked!")
                
            # Check user's linked unregistered names
            linked_names = user.get_linked_unregistered_names()
            print(f"   User's linked unregistered names: {linked_names}")
            
            if test_name.lower() in linked_names:
                print("   ✓ SUCCESS: User's linked names were updated!")
            else:
                print("   ✗ ERROR: User's linked names were not updated!")
                
            # Check database directly again
            result = db.engine.execute(f"SELECT id, payer_id FROM expense WHERE id = {expense.id}").fetchone()
            print(f"   Final database value: ID={result[0]}, payer_id='{result[1]}'")
            
            print("\n=== Test Complete ===")
        else:
            print("Linking failed!")

if __name__ == "__main__":
    import json
    comprehensive_linking_test()