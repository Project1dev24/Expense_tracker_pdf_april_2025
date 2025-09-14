#!/usr/bin/env python3
"""
Script to automatically link unregistered participants to registered users
This script will:
1. Get details of unregistered participants from expenses
2. Find matching registered users
3. Update the users table with linked_unregistered_names
4. Update payer_id in expenses from 'unregistered_{name}' to user ID
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

def link_unregistered_participants():
    """Link unregistered participants to registered users automatically"""
    app = create_app()
    
    with app.app_context():
        print("=== Automatic Linking of Unregistered Participants ===")
        
        # Step 1: Get details of unregistered participants from expenses
        print("\n1. Getting unregistered participants from expenses...")
        unregistered_expenses = Expense.query.filter(Expense.payer_id.like('unregistered_%')).all()
        print(f"   Found {len(unregistered_expenses)} expenses with unregistered payers")
        
        # Extract unique unregistered participant names
        unregistered_names = set()
        for expense in unregistered_expenses:
            # Extract name from payer_id (remove 'unregistered_' prefix)
            name = expense.payer_id.replace('unregistered_', '')
            unregistered_names.add(name)
        
        print(f"   Found {len(unregistered_names)} unique unregistered participant names")
        
        # Step 2: Get all registered users for matching
        print("\n2. Getting registered users for matching...")
        users = User.query.all()
        print(f"   Found {len(users)} registered users")
        
        # Create a mapping for case-insensitive matching
        user_name_map = {}
        for user in users:
            # Map lowercase name to user object
            user_name_map[user.name.lower()] = user
            # Also map email username (part before @) to user object
            email_username = user.email.split('@')[0].lower()
            if email_username not in user_name_map:
                user_name_map[email_username] = user
        
        print(f"   Created mapping for {len(user_name_map)} name variations")
        
        # Step 3: Process each unregistered participant
        print("\n3. Processing unregistered participants...")
        linked_count = 0
        updated_expenses = 0
        
        for name in sorted(unregistered_names):
            print(f"\n   Processing '{name}':")
            
            # Try to find a matching registered user (case-insensitive)
            matching_user = None
            
            # Direct name match (case-insensitive)
            if name.lower() in user_name_map:
                matching_user = user_name_map[name.lower()]
                print(f"     Found direct match: {matching_user.name} (ID: {matching_user.id})")
            
            # Fuzzy matching if no direct match
            if not matching_user:
                for user_name, user in user_name_map.items():
                    # Check if name is contained in user name or vice versa
                    if (name.lower() in user_name or user_name in name.lower()) and len(name) > 2:
                        matching_user = user
                        print(f"     Found fuzzy match: {matching_user.name} (ID: {matching_user.id})")
                        break
            
            if matching_user:
                # Step 4: Update the users table with linked_unregistered_names
                print(f"     Updating user's linked_unregistered_names...")
                if matching_user.add_linked_unregistered_name(name.lower()):
                    print(f"     Successfully added '{name.lower()}' to user's linked names")
                else:
                    print(f"     '{name.lower()}' already in user's linked names")
                
                # Step 5: Update payer_id in expenses from 'unregistered_{name}' to user ID
                print(f"     Updating expenses with payer_id 'unregistered_{name}'...")
                expenses_to_update = Expense.query.filter_by(payer_id=f'unregistered_{name}').all()
                
                for expense in expenses_to_update:
                    old_payer_id = expense.payer_id
                    expense.payer_id = str(matching_user.id)
                    db.session.add(expense)
                    print(f"       Updated expense {expense.id}: {old_payer_id} → {expense.payer_id}")
                    updated_expenses += 1
                
                # Also update the unregistered_participant table if record exists
                unregistered_record = UnregisteredParticipant.query.filter_by(name=name.lower()).first()
                if unregistered_record:
                    unregistered_record.linked_user_id = matching_user.id
                    db.session.add(unregistered_record)
                    print(f"       Updated unregistered_participant record: linked_user_id = {matching_user.id}")
                else:
                    # Create new record if it doesn't exist
                    first_trip = Trip.query.first()
                    if first_trip:
                        new_record = UnregisteredParticipant(
                            name=name.lower(),
                            trip_id=first_trip.id,
                            linked_user_id=matching_user.id
                        )
                        db.session.add(new_record)
                        print(f"       Created new unregistered_participant record with linked_user_id = {matching_user.id}")
                
                linked_count += 1
            else:
                print(f"     No matching user found")
        
        # Commit all changes
        print(f"\n4. Committing changes to database...")
        db.session.commit()
        
        print(f"\n=== Linking Complete ===")
        print(f"Linked {linked_count} unregistered participants to registered users")
        print(f"Updated {updated_expenses} expense records")
        print(f"Users table updated with linked_unregistered_names for matching users")

if __name__ == "__main__":
    link_unregistered_participants()