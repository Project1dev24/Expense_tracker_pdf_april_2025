#!/usr/bin/env python3
"""
Test script to simulate the web interface linking process
This script will test the linking functionality by making requests to the actual web routes
"""

import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app_factory import create_app
from backend.models.trip import Trip
from backend.models.user import User
from backend.models.expense import Expense
from backend.database import db

def test_linking_web():
    """Test the linking functionality through the web interface"""
    print("Testing linking functionality through web interface...")
    
    # Create the Flask app
    app = create_app()
    
    with app.app_context():
        # Get a test trip (assuming trip ID 1 exists)
        trip = Trip.query.get(1)
        if not trip:
            print("No trip found with ID 1")
            return
            
        print(f"Testing with trip: {trip.name}")
        
        # Add a new unregistered participant for testing
        new_unregistered_name = "web_interface_test"
        print(f"\nAdding new unregistered participant: {new_unregistered_name}")
        trip.add_unregistered_participant(new_unregistered_name)
        db.session.commit()
        
        # Get an unregistered participant
        unregistered_participants = trip.get_unregistered_participants_display()
        if not unregistered_participants:
            print("No unregistered participants found")
            return
            
        unregistered_name = unregistered_participants[0]
        print(f"Attempting to link unregistered participant: {unregistered_name}")
        
        # Get a registered user to link to (use a non-admin user)
        registered_users = User.query.filter(User.id != trip.admin_id).all()
        if not registered_users:
            print("No registered users found")
            return
            
        target_user = registered_users[0]
        print(f"Linking to registered user: {target_user.name} ({target_user.email})")
        
        # Test the link_participant method directly first
        print("\n--- Testing link_participant method directly ---")
        result = trip.link_participant(unregistered_name, target_user.id)
        print(f"Direct method result: {result}")
        
        if result:
            print("Direct linking successful!")
            # Check if the participant was removed from unregistered list
            updated_unregistered = trip.get_unregistered_participants_display()
            print(f"Unregistered participants after linking: {updated_unregistered}")
            
            # Check if the user was added to registered participants (unless they're the admin)
            if target_user.id != trip.admin_id:
                updated_registered = trip.get_participants_list()
                print(f"Registered participants after linking: {updated_registered}")
                print(f"Target user ID in registered list: {target_user.id in [int(pid) for pid in updated_registered if pid.isdigit()]}")
        else:
            print("Direct linking failed!")
        
        # Reset for web interface test
        db.session.rollback()
        print("\n--- Resetting for web interface test ---")
        
        # Add the unregistered participant back
        trip.add_unregistered_participant(unregistered_name)
        db.session.commit()
        
        print(f"Reset unregistered participants: {trip.get_unregistered_participants_display()}")
        
        # Now test the web interface route directly
        print("\n--- Testing web interface route ---")
        
        # Create test client
        with app.test_client() as client:
            # Simulate a POST request to the manage_participants route with JSON data
            # We need to set the proper headers to indicate it's a JSON AJAX request
            response = client.post(f'/trips/{trip.id}/manage-participants', 
                                 data=json.dumps({
                                     'action': 'link_participant',
                                     'name': unregistered_name,
                                     'email': target_user.email
                                 }),
                                 content_type='application/json',
                                 headers={'Content-Type': 'application/json'})
            
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_json()}")
            
            if response.status_code == 200:
                print("Web interface linking successful!")
                
                # Check if the participant was removed from unregistered list
                updated_unregistered = trip.get_unregistered_participants_display()
                print(f"Unregistered participants after web linking: {updated_unregistered}")
                
                # Check if the user was added to registered participants
                updated_registered = trip.get_participants_list()
                print(f"Registered participants after web linking: {updated_registered}")
                print(f"Target user ID in registered list: {target_user.id in [int(pid) for pid in updated_registered if pid.isdigit()]}")
            else:
                print("Web interface linking failed!")

if __name__ == "__main__":
    test_linking_web()