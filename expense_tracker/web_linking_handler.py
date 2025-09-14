#!/usr/bin/env python3
"""
Web interface implementation for the linking logic
This script contains the functions that would be called when an admin clicks "Link to User"
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

def handle_link_to_user_request(unregistered_name, target_user_email, trip_id):
    """
    Handle the "Link to User" request from the web interface
    
    This function implements the exact logic you requested:
    1. Check if the unregistered participant exists in the table
    2. Check if linked_user_id is null
    3. If null, map the unregistered participant to the registered user
    4. Update the user's linked_unregistered_names
    """
    app = create_app()
    
    with app.app_context():
        print(f"=== Handling Link to User Request ===")
        print(f"Unregistered name: '{unregistered_name}'")
        print(f"Target user email: '{target_user_email}'")
        print(f"Trip ID: {trip_id}")
        
        # Step 1: Find the unregistered participant in the table
        unregistered = UnregisteredParticipant.query.filter_by(
            name=unregistered_name.lower(),
            trip_id=trip_id
        ).first()
        
        if not unregistered:
            print(f"❌ Unregistered participant '{unregistered_name}' not found in table")
            return {
                'success': False,
                'message': f"Unregistered participant '{unregistered_name}' not found"
            }
        
        print(f"✅ Found unregistered participant (ID: {unregistered.id})")
        
        # Step 2: Check if linked_user_id is null
        if unregistered.linked_user_id is not None:
            print(f"❌ Already linked to user {unregistered.linked_user_id}")
            return {
                'success': False,
                'message': f"Participant already linked to user {unregistered.linked_user_id}"
            }
        
        print(f"✅ linked_user_id is null, ready to link")
        
        # Step 3: Find the target registered user by email
        target_user = User.query.filter_by(email=target_user_email).first()
        if not target_user:
            print(f"❌ Target user with email '{target_user_email}' not found")
            return {
                'success': False,
                'message': f"User with email '{target_user_email}' not found"
            }
        
        print(f"✅ Found target user: {target_user.name} (ID: {target_user.id})")
        
        # Step 4: Link the unregistered participant to the registered user
        print(f"🔗 Linking unregistered participant to registered user...")
        
        # Update the linked_user_id
        old_linked_user_id = unregistered.linked_user_id
        unregistered.linked_user_id = target_user.id
        db.session.add(unregistered)
        
        # Update the user's linked_unregistered_names
        print(f"📝 Updating user's linked_unregistered_names...")
        if target_user.add_linked_unregistered_name(unregistered_name.lower()):
            print(f"✅ Successfully added '{unregistered_name.lower()}' to user's linked names")
        else:
            print(f"ℹ️  '{unregistered_name.lower()}' already in user's linked names")
        
        # Update all expenses with this unregistered participant as payer
        unregistered_id = f"unregistered_{unregistered_name.lower()}"
        expenses_to_update = Expense.query.filter_by(payer_id=unregistered_id).all()
        print(f"💰 Found {len(expenses_to_update)} expenses to update")
        
        updated_expenses = []
        for expense in expenses_to_update:
            old_payer_id = expense.payer_id
            expense.payer_id = str(target_user.id)
            db.session.add(expense)
            updated_expenses.append(expense.id)
            print(f"  💸 Updated expense {expense.id}: {old_payer_id} → {expense.payer_id}")
        
        # Commit all changes
        db.session.commit()
        print(f"💾 All changes committed to database")
        
        return {
            'success': True,
            'message': f"Successfully linked '{unregistered_name}' to user '{target_user.name}'",
            'linked_user_id': target_user.id,
            'updated_expenses': updated_expenses
        }

def web_interface_linking_demo():
    """Demonstrate how this would work in the web interface"""
    app = create_app()
    
    with app.app_context():
        print("=== Web Interface Linking Demo ===")
        
        # Simulate what happens when admin clicks "Link to User"
        # In the real web interface, these values would come from the form
        
        # Get a trip to work with
        trip = Trip.query.first()
        if not trip:
            print("❌ No trips found")
            return
        
        print(f"Using trip: {trip.name} (ID: {trip.id})")
        
        # Example request data (as if from AJAX POST)
        request_data = {
            'unregistered_name': 'Demo User',
            'target_user_email': 'test1@mail.com',  # Admin user
            'trip_id': trip.id
        }
        
        print(f"\n📥 Request data:")
        print(f"   Unregistered name: {request_data['unregistered_name']}")
        print(f"   Target user email: {request_data['target_user_email']}")
        print(f"   Trip ID: {request_data['trip_id']}")
        
        # First, add the unregistered user to the table (simulating prior step)
        print(f"\n📋 Adding unregistered user to table...")
        unregistered = UnregisteredParticipant(
            name=request_data['unregistered_name'].lower(),
            trip_id=request_data['trip_id']
        )
        db.session.add(unregistered)
        db.session.commit()
        print(f"✅ Added unregistered user (ID: {unregistered.id})")
        
        # Now handle the linking request
        print(f"\n⚡ Handling link request...")
        result = handle_link_to_user_request(
            request_data['unregistered_name'],
            request_data['target_user_email'],
            request_data['trip_id']
        )
        
        print(f"\n📤 Response:")
        if result['success']:
            print(f"   ✅ Success: {result['message']}")
            print(f"   🆔 Linked user ID: {result['linked_user_id']}")
            print(f"   💰 Updated expenses: {result['updated_expenses']}")
        else:
            print(f"   ❌ Error: {result['message']}")

if __name__ == "__main__":
    web_interface_linking_demo()