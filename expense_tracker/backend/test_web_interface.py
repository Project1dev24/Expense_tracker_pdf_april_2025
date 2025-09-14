#!/usr/bin/env python3
"""
Test script to simulate the exact web interface linking process
"""

import sys
import os
import json

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app_factory import create_app
from backend.models.trip import Trip
from backend.models.user import User
from backend.database import db

def test_web_interface():
    """Test the exact web interface linking process"""
    print("Testing exact web interface linking process...")
    
    # Create the Flask app
    app = create_app()
    
    # Set up a test client
    with app.test_client() as client:
        # Create a test context
        with app.app_context():
            # Get a test trip (assuming trip ID 1 exists)
            trip = Trip.query.get(1)
            if not trip:
                print("No trip found with ID 1")
                return
                
            print(f"Testing with trip: {trip.name}")
            
            # Add a new unregistered participant for testing
            new_unregistered_name = "web_interface_test_user"
            print(f"\nAdding new unregistered participant: {new_unregistered_name}")
            trip.add_unregistered_participant(new_unregistered_name)
            db.session.commit()
            
            # Get the unregistered participant (in display format)
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
            
            # Simulate the exact AJAX request that the web interface makes
            print("\n--- Simulating web interface AJAX request ---")
            
            # The web interface sends a JSON POST request with:
            # {
            #     "action": "link_participant",
            #     "name": "Unregistered Participant Name",
            #     "email": "user@example.com"
            # }
            
            response = client.post(f'/trips/{trip.id}/manage-participants',
                                 data=json.dumps({
                                     'action': 'link_participant',
                                     'name': unregistered_name,  # This is the display name
                                     'email': target_user.email
                                 }),
                                 content_type='application/json',
                                 headers={'Content-Type': 'application/json'})
            
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_json()}")
            
            # Check if the linking was successful
            if response.status_code == 200:
                response_data = response.get_json()
                if response_data and response_data.get('success'):
                    print("Web interface linking successful!")
                    
                    # Verify the changes in the database
                    updated_unregistered = trip.get_unregistered_participants_display()
                    print(f"Unregistered participants after linking: {updated_unregistered}")
                    
                    updated_registered = trip.get_participants_list()
                    print(f"Registered participants after linking: {updated_registered}")
                    print(f"Target user ID in registered list: {target_user.id in [int(pid) for pid in updated_registered if pid.isdigit()]}")
                else:
                    print("Web interface linking failed!")
                    if response_data:
                        print(f"Error message: {response_data.get('message', 'Unknown error')}")
            else:
                print("Web interface request failed!")
                print(f"Response: {response.data.decode('utf-8')}")

if __name__ == "__main__":
    test_web_interface()