#!/usr/bin/env python3

import sys
import os

# Add the backend directory to the path
backend_path = os.path.join(os.path.dirname(__file__), 'expense_tracker', 'backend')
sys.path.insert(0, backend_path)

# Set the Flask app path
os.environ['FLASK_APP'] = os.path.join(backend_path, 'app.py')

from database import db
from models.user import User
from models.trip import Trip
from app_factory import create_app

def test_linking():
    app = create_app()
    
    with app.app_context():
        # Get a test trip
        trip = Trip.query.first()
        if not trip:
            print("No trips found in database")
            return
            
        print(f"Testing with trip: {trip.name} (ID: {trip.id})")
        
        # Get unregistered participants
        unregistered = trip.get_unregistered_participants()
        print(f"Unregistered participants: {unregistered}")
        
        if not unregistered:
            print("No unregistered participants found")
            return
            
        # Get a test user
        user = User.query.first()
        if not user:
            print("No users found in database")
            return
            
        print(f"Testing with user: {user.name} (ID: {user.id}, Email: {user.email})")
        
        # Try to link the first unregistered participant to this user
        name_to_link = unregistered[0]
        print(f"Attempting to link '{name_to_link}' to user {user.id}")
        
        # Check if user is a participant
        participants = trip.get_participants_list()
        print(f"Trip participants: {participants}")
        print(f"Is user {user.id} a participant? {str(user.id) in participants}")
        print(f"Is user {user.id} the admin? {user.id == trip.admin_id}")
        
        # Add user as participant if not already
        if str(user.id) not in participants and user.id != trip.admin_id:
            print("Adding user as participant...")
            trip.add_participant(user.id)
            db.session.commit()
            print("User added as participant")
            
            # Refresh participants list
            participants = trip.get_participants_list()
            print(f"Updated trip participants: {participants}")
        
        # Now try linking
        print(f"Calling link_participant('{name_to_link}', {user.id})")
        result = trip.link_participant(name_to_link, user.id)
        print(f"Link result: {result}")
        
        if result:
            db.session.commit()
            print("Changes committed to database")
            
            # Check the user's linked names
            linked_names = user.get_linked_unregistered_names()
            print(f"User's linked unregistered names: {linked_names}")
        else:
            print("Linking failed")

if __name__ == "__main__":
    test_linking()