#!/usr/bin/env python3
"""
Test script to verify that linking updates payer_id in expense table
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

def test_link_updates_payer_id():
    """Test that linking updates payer_id in expense table"""
    app = create_app()
    
    with app.app_context():
        print("=== Test Link Updates Payer ID ===")
        
        # Get the first trip
        trip = Trip.query.first()
        if not trip:
            print("No trip found")
            return
        
        print(f"Using trip: {trip.name} (ID: {trip.id})")
        
        # Add an unregistered participant if none exist
        unregistered = trip.get_unregistered_participants()
        if not unregistered:
            print("Adding test unregistered participant...")
            trip.add_unregistered_participant("Test User")
            db.session.commit()
            unregistered = trip.get_unregistered_participants()
        
        print(f"Current unregistered participants: {unregistered}")
        
        if not unregistered:
            print("No unregistered participants found")
            return
        
        # Get the first unregistered participant
        name = unregistered[0]
        print(f"Linking participant: {name}")
        
        # Create an expense with this unregistered participant as payer
        unregistered_id = f"unregistered_{name}"
        print(f"Creating expense with payer_id: {unregistered_id}")
        
        expense = Expense(
            description="Test expense for linking",
            amount=100.0,
            currency="USD",
            date=datetime.now(),
            category="Test",
            payer_id=unregistered_id,
            trip_id=trip.id,
            participants=json.dumps([unregistered_id]),
            shares=json.dumps({unregistered_id: 100.0})
        )
        db.session.add(expense)
        db.session.commit()
        
        print(f"Created expense {expense.id} with payer_id: {expense.payer_id}")
        
        # Find a user to link to (use the trip admin)
        user = User.query.get(trip.admin_id)
        if not user:
            print("No user found to link to")
            return
        
        print(f"Linking to user: {user.name} (ID: {user.id})")
        
        # Link the participant
        result = trip.link_participant(name, user.id)
        print(f"Link result: {result}")
        
        if result:
            print("Linking successful!")
            
            # Check if expense payer_id was updated
            updated_expense = Expense.query.get(expense.id)
            print(f"Updated expense payer_id: {updated_expense.payer_id}")
            
            if updated_expense.payer_id == str(user.id):
                print("SUCCESS: Expense payer_id was correctly updated!")
            else:
                print("ERROR: Expense payer_id was not updated!")
                
            # Check updated unregistered participants
            updated_unregistered = trip.get_unregistered_participants()
            print(f"Updated unregistered participants: {updated_unregistered}")
            
            # Check if participant is now linked in database
            participant = UnregisteredParticipant.query.filter_by(
                name=name, 
                trip_id=trip.id
            ).first()
            
            if participant and participant.linked_user_id == user.id:
                print(f"Participant successfully linked to user {user.id}")
            else:
                print("Participant not properly linked in database")
        else:
            print("Linking failed!")

if __name__ == "__main__":
    import json
    test_link_updates_payer_id()