#!/usr/bin/env python3
"""
Comprehensive script to link unregistered participants to registered users
This script will:
1. Get details of unregistered participants from expenses
2. Create or update records in the unregistered_participant table
3. Find matching registered users using multiple matching strategies
4. Update the users table with linked_unregistered_names
5. Update payer_id in expenses from 'unregistered_{name}' to user ID
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

def get_best_matching_user(name, user_name_map):
    """Find the best matching user for an unregistered participant name"""
    # Direct exact match (case-insensitive)
    if name.lower() in user_name_map:
        return user_name_map[name.lower()]
    
    # Partial matching - check if name is contained in user name or vice versa
    for user_name, user in user_name_map.items():
        if len(name) > 2 and (name.lower() in user_name or user_name in name.lower()):
            return user
    
    # Soundex-like matching for common variations
    # Check for common name variations
    name_variations = [
        name.lower(),
        name.lower().replace(' ', ''),
        name.lower().replace('-', ''),
        name.lower().replace('_', ''),
        name.lower().replace('.', '')
    ]
    
    for variation in name_variations:
        if variation in user_name_map:
            return user_name_map[variation]
    
    return None

def link_unregistered_participants_comprehensive():
    """Comprehensive linking of unregistered participants to registered users"""
    app = create_app()
    
    with app.app_context():
        print("=== Comprehensive Unregistered Participant Linking ===")
        
        # Step 1: Get all unregistered participants from expenses
        print("\n1. Scanning expenses for unregistered participants...")
        unregistered_expenses = Expense.query.filter(Expense.payer_id.like('unregistered_%')).all()
        print(f"   Found {len(unregistered_expenses)} expenses with unregistered payers")
        
        # Extract unique unregistered participant names
        unregistered_names = {}
        for expense in unregistered_expenses:
            # Extract name from payer_id (remove 'unregistered_' prefix)
            name = expense.payer_id.replace('unregistered_', '')
            if name not in unregistered_names:
                unregistered_names[name] = []
            unregistered_names[name].append(expense)
        
        print(f"   Found {len(unregistered_names)} unique unregistered participant names")
        
        # Step 2: Get all registered users for matching
        print("\n2. Loading registered users...")
        users = User.query.all()
        print(f"   Found {len(users)} registered users")
        
        # Create comprehensive mapping for matching
        user_name_map = {}
        for user in users:
            # Primary mappings
            user_name_map[user.name.lower()] = user
            user_name_map[user.email.split('@')[0].lower()] = user
            
            # Additional mappings for common variations
            name_parts = user.name.lower().split()
            if len(name_parts) > 1:
                # First name only
                user_name_map[name_parts[0]] = user
                # Last name only
                user_name_map[name_parts[-1]] = user
                # First initial + last name
                if name_parts[0]:
                    user_name_map[f"{name_parts[0][0]}{name_parts[-1]}"] = user
                    user_name_map[f"{name_parts[0][0]}.{name_parts[-1]}"] = user
        
        print(f"   Created comprehensive mapping with {len(user_name_map)} entries")
        
        # Step 3: Process each unregistered participant
        print("\n3. Processing unregistered participants...")
        linked_count = 0
        updated_expenses = 0
        created_records = 0
        updated_records = 0
        
        # Get a default trip for new records
        default_trip = Trip.query.first()
        if not default_trip:
            print("   ERROR: No trips found in database. Cannot create unregistered participant records.")
            return
        
        for name, expenses in unregistered_names.items():
            print(f"\n   Processing '{name}' ({len(expenses)} expenses):")
            
            # Step 4: Check if unregistered participant record exists
            unregistered_record = UnregisteredParticipant.query.filter_by(name=name.lower()).first()
            if not unregistered_record:
                # Create new record
                unregistered_record = UnregisteredParticipant(
                    name=name.lower(),
                    trip_id=default_trip.id
                )
                db.session.add(unregistered_record)
                db.session.flush()  # Get the ID
                created_records += 1
                print(f"     Created new unregistered participant record (ID: {unregistered_record.id})")
            else:
                print(f"     Found existing unregistered participant record (ID: {unregistered_record.id})")
            
            # Step 5: Try to find a matching registered user
            matching_user = get_best_matching_user(name, user_name_map)
            
            if matching_user:
                print(f"     Found matching user: {matching_user.name} (ID: {matching_user.id}, Email: {matching_user.email})")
                
                # Step 6: Update the users table with linked_unregistered_names
                print(f"     Updating user's linked_unregistered_names...")
                if matching_user.add_linked_unregistered_name(name.lower()):
                    print(f"     Successfully added '{name.lower()}' to user's linked names")
                else:
                    print(f"     '{name.lower()}' already in user's linked names")
                
                # Step 7: Update unregistered_participant record
                if not unregistered_record.linked_user_id:
                    unregistered_record.linked_user_id = matching_user.id
                    db.session.add(unregistered_record)
                    updated_records += 1
                    print(f"     Updated unregistered_participant: linked_user_id = {matching_user.id}")
                else:
                    print(f"     Unregistered participant already linked to user {unregistered_record.linked_user_id}")
                
                # Step 8: Update payer_id in expenses from 'unregistered_{name}' to user ID
                print(f"     Updating {len(expenses)} expenses...")
                for expense in expenses:
                    if expense.payer_id == f'unregistered_{name}':
                        old_payer_id = expense.payer_id
                        expense.payer_id = str(matching_user.id)
                        db.session.add(expense)
                        print(f"       Updated expense {expense.id}: {old_payer_id} → {expense.payer_id}")
                        updated_expenses += 1
                    else:
                        print(f"       Expense {expense.id} already updated or different format")
                
                linked_count += 1
            else:
                print(f"     No matching user found for '{name}'")
                # Show some user suggestions for manual matching
                suggestions = []
                name_lower = name.lower()
                for user_name, user in list(user_name_map.items())[:5]:  # Show first 5
                    suggestions.append(f"{user.name} ({user.email})")
                if suggestions:
                    print(f"     Suggested users: {', '.join(suggestions)}")
        
        # Step 9: Commit all changes
        print(f"\n4. Committing all changes...")
        try:
            db.session.commit()
            print("   ✓ Changes committed successfully")
        except Exception as e:
            print(f"   ✗ Error committing changes: {e}")
            db.session.rollback()
            return
        
        print(f"\n=== Linking Process Complete ===")
        print(f"Summary:")
        print(f"  - Processed {len(unregistered_names)} unique unregistered participants")
        print(f"  - Created {created_records} new unregistered participant records")
        print(f"  - Updated {updated_records} existing unregistered participant records")
        print(f"  - Linked {linked_count} unregistered participants to registered users")
        print(f"  - Updated {updated_expenses} expense records")
        print(f"  - Updated users table with linked_unregistered_names")

if __name__ == "__main__":
    link_unregistered_participants_comprehensive()