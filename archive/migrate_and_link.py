#!/usr/bin/env python3
"""
Migration script to transfer unregistered participants from expenses to the new UnregisteredParticipant table
and link them to matching registered users
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

def migrate_and_link_unregistered_participants():
    """Migrate unregistered participants from expenses to new table and link to matching users"""
    app = create_app()
    
    with app.app_context():
        print("=== Migration and Linking of Unregistered Participants ===")
        
        # Get all expenses with unregistered payers
        unregistered_expenses = Expense.query.filter(Expense.payer_id.like('unregistered_%')).all()
        print(f"Found {len(unregistered_expenses)} expenses with unregistered payers")
        
        # Extract unique unregistered participant names
        unregistered_names = set()
        for expense in unregistered_expenses:
            name = expense.payer_id.replace('unregistered_', '')
            unregistered_names.add(name)
        
        print(f"Found {len(unregistered_names)} unique unregistered participant names:")
        for name in sorted(unregistered_names):
            print(f"  - {name}")
        
        # Get all users for matching
        users = User.query.all()
        user_map = {user.name.lower(): user for user in users}
        print(f"\nFound {len(users)} registered users")
        
        # Process each unregistered participant
        linked_count = 0
        migrated_count = 0
        
        for name in unregistered_names:
            print(f"\nProcessing '{name}':")
            
            # Check if this unregistered participant already exists in the new table
            existing = UnregisteredParticipant.query.filter_by(name=name.lower()).first()
            if not existing:
                # Create new unregistered participant record
                # We need to find which trip this participant belongs to
                # For now, we'll use the first trip as a placeholder
                first_trip = Trip.query.first()
                if first_trip:
                    unregistered = UnregisteredParticipant(
                        name=name.lower(),
                        trip_id=first_trip.id
                    )
                    db.session.add(unregistered)
                    db.session.flush()  # Get the ID without committing
                    migrated_count += 1
                    print(f"  Created new unregistered participant record (ID: {unregistered.id})")
                else:
                    print(f"  No trips found, skipping migration")
                    continue
            else:
                unregistered = existing
                print(f"  Found existing unregistered participant record (ID: {unregistered.id})")
            
            # Try to find a matching registered user
            matching_user = None
            if name.lower() in user_map:
                matching_user = user_map[name.lower()]
            else:
                # Try case-insensitive partial matching
                for user_name, user in user_map.items():
                    if name.lower() in user_name or user_name in name.lower():
                        matching_user = user
                        break
            
            if matching_user:
                print(f"  Found matching user: {matching_user.name} (ID: {matching_user.id})")
                
                # Link the unregistered participant to the registered user
                unregistered.linked_user_id = matching_user.id
                db.session.add(unregistered)
                
                # Add the unregistered name to the user's linked list
                if matching_user.add_linked_unregistered_name(name.lower()):
                    print(f"  Added '{name.lower()}' to user's linked unregistered names")
                
                # Update all expenses with this unregistered participant as payer
                expenses_to_update = Expense.query.filter_by(payer_id=f'unregistered_{name}').all()
                print(f"  Found {len(expenses_to_update)} expenses to update")
                
                for expense in expenses_to_update:
                    old_payer_id = expense.payer_id
                    expense.payer_id = str(matching_user.id)
                    db.session.add(expense)
                    print(f"    Updated expense {expense.id}: {old_payer_id} -> {expense.payer_id}")
                
                linked_count += 1
            else:
                print(f"  No matching user found for '{name}'")
        
        # Commit all changes
        db.session.commit()
        print(f"\n=== Migration Complete ===")
        print(f"Migrated {migrated_count} unregistered participants")
        print(f"Linked {linked_count} unregistered participants to registered users")

if __name__ == "__main__":
    migrate_and_link_unregistered_participants()