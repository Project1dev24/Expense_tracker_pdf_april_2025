#!/usr/bin/env python3
"""
Test script to link an unregistered participant to a registered user
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app_factory import create_app
from backend.models.trip import Trip
from backend.models.unregistered_participant import UnregisteredParticipant
from backend.models.user import User
from backend.database import db

def test_link_participant():
    """Test linking an unregistered participant to a registered user"""
    app = create_app()
    
    with app.app_context():
        print("=== Test Link Participant ===")
        
        # Get the first trip
        trip = Trip.query.first()
        if not trip:
            print("No trip found")
            return
        
        print(f"Using trip: {trip.name} (ID: {trip.id})")
        
        # Check current unregistered participants
        unregistered = trip.get_unregistered_participants()
        print(f"Current unregistered participants: {unregistered}")
        
        if not unregistered:
            print("No unregistered participants found")
            return
        
        # Get the first unregistered participant
        name = unregistered[0]
        print(f"Linking participant: {name}")
        
        # Find a user to link to (use the trip admin)
        user = User.query.get(trip.admin_id)
        if not user:
            print("No user found to link to")
            return
        
        print(f"Linking to user: {user.name} (ID: {user.id})")
        
        # Link the participant
        result = trip.link_participant(name, user.id)
        print(f"Link result: {result}")
        
        if result:
            db.session.commit()
            print("Linking successful!")
            
            # Check updated unregistered participants
            updated_unregistered = trip.get_unregistered_participants()
            print(f"Updated unregistered participants: {updated_unregistered}")
            
            # Check if participant is now linked in database
            participant = UnregisteredParticipant.query.filter_by(
                name=name, 
                trip_id=trip.id
            ).first()
            
            if participant and participant.linked_user_id == user.id:
                print(f"Participant successfully linked to user {user.id}")
            else:
                print("Participant not properly linked in database")
        else:
            print("Linking failed!")

if __name__ == "__main__":
    test_link_participant()