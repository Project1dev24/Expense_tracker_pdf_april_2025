#!/usr/bin/env python3
"""
Debug script to test linking unregistered participants to registered users
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from expense_tracker.backend.app_factory import create_app
from expense_tracker.backend.models.trip import Trip
from expense_tracker.backend.models.user import User
from expense_tracker.backend.models.expense import Expense
from expense_tracker.backend.database import db

def debug_linking():
    """Debug the linking process with detailed output"""
    app = create_app()
    
    with app.app_context():
        print("=== Debug Linking Process ===")
        
        # Get all trips
        trips = Trip.query.all()
        print(f"Found {len(trips)} trips")
        
        if not trips:
            print("No trips found in database")
            return
            
        # Select the first trip for testing
        trip = trips[0]
        print(f"Testing with trip: {trip.name} (ID: {trip.id})")
        
        # Show current unregistered participants
        unregistered = trip.get_unregistered_participants()
        print(f"Current unregistered participants: {unregistered}")
        
        # Show current registered participants
        registered_ids = trip.get_participants_list()
        print(f"Current registered participant IDs: {registered_ids}")
        
        # Show all users
        users = User.query.all()
        print(f"Available users:")
        for user in users:
            print(f"  - ID: {user.id}, Name: {user.name}, Email: {user.email}")
            
        # Show expenses for this trip
        expenses = Expense.query.filter_by(trip_id=trip.id).all()
        print(f"Expenses for this trip: {len(expenses)}")
        for expense in expenses:
            print(f"  Expense ID: {expense.id}")
            print(f"    Description: {expense.description}")
            print(f"    Payer ID: {expense.payer_id}")
            print(f"    Participants: {expense.get_participants_list()}")
            print(f"    Shares: {expense.get_shares()}")
            
        # Show advances
        advances = trip.get_advances()
        print(f"Advances: {advances}")
        
        # Show general payments
        payments = trip.get_general_payments()
        print(f"General payments: {payments}")
        
        # Test linking if we have unregistered participants
        if unregistered:
            name_to_link = unregistered[0]  # Use the first unregistered participant
            print(f"\nAttempting to link unregistered participant: '{name_to_link}'")
            
            # Find a registered user to link to (use the trip admin for testing)
            user_to_link = User.query.get(trip.admin_id)
            if user_to_link:
                print(f"Linking to user: {user_to_link.name} (ID: {user_to_link.id}, Email: {user_to_link.email})")
                
                # Before linking - check what unregistered_id would be used
                unregistered_id_stored = f"unregistered_{name_to_link}"
                print(f"Stored unregistered ID would be: {unregistered_id_stored}")
                
                # Try to link
                print("\nCalling link_participant...")
                result = trip.link_participant(name_to_link, user_to_link.id)
                print(f"Link result: {result}")
                
                if result:
                    print("Linking successful!")
                    db.session.commit()
                    
                    # Show updated data
                    print("\nAfter linking:")
                    updated_unregistered = trip.get_unregistered_participants()
                    print(f"Updated unregistered participants: {updated_unregistered}")
                    
                    updated_registered = trip.get_participants_list()
                    print(f"Updated registered participants: {updated_registered}")
                    
                    # Check if user was added to registered participants (unless they're the admin)
                    if str(user_to_link.id) in updated_registered:
                        print("User successfully added to registered participants")
                    else:
                        print("User not added to registered participants (might be admin)")
                        
                    # Check expenses again
                    updated_expenses = Expense.query.filter_by(trip_id=trip.id).all()
                    print(f"\nUpdated expenses:")
                    for expense in updated_expenses:
                        print(f"  Expense ID: {expense.id}")
                        print(f"    Payer ID: {expense.payer_id}")
                        print(f"    Participants: {expense.get_participants_list()}")
                        print(f"    Shares: {expense.get_shares()}")
                        
                    # Check advances
                    updated_advances = trip.get_advances()
                    print(f"Updated advances: {updated_advances}")
                    
                    # Check general payments
                    updated_payments = trip.get_general_payments()
                    print(f"Updated general payments: {updated_payments}")
                else:
                    print("Linking failed!")
            else:
                print("No user found to link to")
        else:
            print("No unregistered participants to link")

if __name__ == "__main__":
    debug_linking()