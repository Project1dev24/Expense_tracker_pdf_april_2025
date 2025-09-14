#!/usr/bin/env python3
"""
Script to implement the requested linking logic:
1. Add unregistered users to unregistered_participant table
2. When linking, check if linked_user_id is null
3. If null, map the unregistered participant to a registered user
4. Update the user's linked_unregistered_names
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app_factory import create_app
from backend.models.trip import Trip
from backend.models.unregistered_participant import UnregisteredParticipant
from backend.models.user import User
from backend.models.expense import Expense
from backend.database import db

def add_unregistered_user_to_table(name, trip_id):
    """Add an unregistered user to the unregistered_participant table"""
    app = create_app()
    
    with app.app_context():
        print(f"Adding unregistered user '{name}' to table...")
        
        # Check if participant already exists
        existing = UnregisteredParticipant.query.filter_by(
            name=name.lower(), 
            trip_id=trip_id
        ).first()
        
        if existing:
            print(f"  Participant already exists (ID: {existing.id})")
            return existing
        else:
            # Create new unregistered participant
            unregistered = UnregisteredParticipant(
                name=name.lower(),
                trip_id=trip_id
            )
            db.session.add(unregistered)
            db.session.commit()
            print(f"  Created new participant (ID: {unregistered.id})")
            return unregistered

def link_user_if_null(unregistered_name, trip_id, target_user_id):
    """Link unregistered user to registered user if linked_user_id is null"""
    app = create_app()
    
    with app.app_context():
        print(f"\nChecking linking for unregistered user '{unregistered_name}'...")
        
        # Find the unregistered participant
        unregistered = UnregisteredParticipant.query.filter_by(
            name=unregistered_name.lower(),
            trip_id=trip_id
        ).first()
        
        if not unregistered:
            print(f"  Unregistered participant '{unregistered_name}' not found")
            return False
        
        print(f"  Found unregistered participant (ID: {unregistered.id})")
        print(f"  Current linked_user_id: {unregistered.linked_user_id}")
        
        # Check if linked_user_id is null
        if unregistered.linked_user_id is not None:
            print(f"  Already linked to user {unregistered.linked_user_id}")
            return False
        
        # If linked_user_id is null, proceed with linking
        print(f"  linked_user_id is null, proceeding with linking...")
        
        # Get the target user
        target_user = User.query.get(target_user_id)
        if not target_user:
            print(f"  Target user ID {target_user_id} not found")
            return False
        
        print(f"  Target user: {target_user.name} (ID: {target_user.id})")
        
        # Update the linked_user_id
        unregistered.linked_user_id = target_user_id
        db.session.add(unregistered)
        
        # Update the user's linked_unregistered_names
        print(f"  Updating user's linked_unregistered_names...")
        if target_user.add_linked_unregistered_name(unregistered_name.lower()):
            print(f"  Successfully added '{unregistered_name.lower()}' to user's linked names")
        else:
            print(f"  '{unregistered_name.lower()}' already in user's linked names")
        
        # Update all expenses with this unregistered participant as payer
        unregistered_id = f"unregistered_{unregistered_name.lower()}"
        expenses_to_update = Expense.query.filter_by(payer_id=unregistered_id).all()
        print(f"  Found {len(expenses_to_update)} expenses to update")
        
        for expense in expenses_to_update:
            old_payer_id = expense.payer_id
            expense.payer_id = str(target_user_id)
            db.session.add(expense)
            print(f"    Updated expense {expense.id}: {old_payer_id} → {expense.payer_id}")
        
        # Commit all changes
        db.session.commit()
        print(f"  ✓ Linking completed successfully!")
        
        return True

def demonstrate_requested_logic():
    """Demonstrate the exact logic you requested"""
    app = create_app()
    
    with app.app_context():
        print("=== Demonstrating Requested Linking Logic ===")
        
        # Get a trip to work with
        trip = Trip.query.first()
        if not trip:
            print("No trips found in database")
            return
        
        print(f"Using trip: {trip.name} (ID: {trip.id})")
        
        # Step 1: Add an unregistered user to the table
        print("\n1. Adding unregistered user to table...")
        unregistered_name = "Test Participant"
        unregistered_record = add_unregistered_user_to_table(unregistered_name, trip.id)
        
        # Step 2: Simulate admin clicking "Link to User"
        print("\n2. Simulating admin clicking 'Link to User'...")
        
        # First, let's check if we can link (linked_user_id should be null)
        print(f"   Checking if linked_user_id is null...")
        if unregistered_record.linked_user_id is None:
            print(f"   ✓ linked_user_id is null, ready to link")
            
            # Get a user to link to (using admin for this example)
            target_user = User.query.get(trip.admin_id)
            if target_user:
                print(f"   Target user: {target_user.name} (ID: {target_user.id})")
                
                # Step 3: Link the user
                print(f"\n3. Linking unregistered participant to registered user...")
                result = link_user_if_null(unregistered_name, trip.id, target_user.id)
                
                if result:
                    print(f"\n✓ SUCCESS: Linking logic implemented correctly!")
                    print(f"  - Unregistered participant added to table")
                    print(f"  - Checked that linked_user_id was null")
                    print(f"  - Mapped unregistered participant to registered user")
                    print(f"  - Updated user's linked_unregistered_names")
                else:
                    print(f"\n✗ Linking failed")
            else:
                print(f"   No target user found")
        else:
            print(f"   ✗ linked_user_id is not null ({unregistered_record.linked_user_id})")

if __name__ == "__main__":
    demonstrate_requested_logic()