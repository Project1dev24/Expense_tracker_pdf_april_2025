#!/usr/bin/env python3
"""
Debug script to test linking unregistered participants to registered users
This script creates a test scenario with an expense that includes an unregistered participant
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app_factory import create_app
from backend.models.trip import Trip
from backend.models.user import User
from backend.models.expense import Expense
from backend.database import db

def debug_linking_complete():
    """Debug the linking process with a complete test scenario"""
    app = create_app()
    
    with app.app_context():
        print("=== Debug Linking Process - Complete Test ===")
        
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
        
        # Add a new unregistered participant for testing
        new_unregistered_name = "debug_test_user"
        print(f"\nAdding new unregistered participant: {new_unregistered_name}")
        trip.add_unregistered_participant(new_unregistered_name)
        db.session.commit()
        
        # Show updated unregistered participants
        updated_unregistered = trip.get_unregistered_participants()
        print(f"Updated unregistered participants: {updated_unregistered}")
        
        # Show current registered participants
        registered_ids = trip.get_participants_list()
        print(f"Current registered participant IDs: {registered_ids}")
        
        # Show all users
        users = User.query.all()
        print(f"Available users:")
        for user in users:
            print(f"  - ID: {user.id}, Name: {user.name}, Email: {user.email}")
            
        # Create a test expense with the unregistered participant
        print(f"\nCreating test expense with unregistered participant: {new_unregistered_name}")
        
        # Create expense with unregistered participant as payer
        test_expense = Expense(
            description="Test expense for linking debug",
            amount=100.0,
            date=datetime.now(),
            payer_id=f"unregistered_{new_unregistered_name}",  # Unregistered participant as payer
            trip_id=trip.id,
            split_method="equal"
        )
        
        # Add the unregistered participant to the expense
        test_expense.update_split("equal", [], unregistered_participants=[new_unregistered_name])
        
        db.session.add(test_expense)
        db.session.commit()
        
        print(f"Created test expense ID: {test_expense.id}")
        print(f"  Payer ID: {test_expense.payer_id}")
        print(f"  Participants: {test_expense.get_participants_list()}")
        print(f"  Shares: {test_expense.get_shares()}")
        
        # Show all expenses for this trip
        expenses = Expense.query.filter_by(trip_id=trip.id).all()
        print(f"\nAll expenses for this trip: {len(expenses)}")
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
        
        # Test linking the unregistered participant
        print(f"\nAttempting to link unregistered participant: '{new_unregistered_name}'")
        
        # Find a registered user to link to (use the trip admin for testing)
        user_to_link = User.query.get(trip.admin_id)
        if user_to_link:
            print(f"Linking to user: {user_to_link.name} (ID: {user_to_link.id}, Email: {user_to_link.email})")
            
            # Before linking - check what unregistered_id would be used
            unregistered_id_stored = f"unregistered_{new_unregistered_name}"
            print(f"Stored unregistered ID would be: {unregistered_id_stored}")
            
            # Try to link
            print("\nCalling link_participant...")
            result = trip.link_participant(new_unregistered_name, user_to_link.id)
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
                    print(f"    Description: {expense.description}")
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

if __name__ == "__main__":
    debug_linking_complete()