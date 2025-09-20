#!/usr/bin/env python3
"""
Test script to add an unregistered participant to a trip
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

def test_unregistered_participant():
    """Test adding an unregistered participant to a trip"""
    app = create_app()
    
    with app.app_context():
        print("=== Test Unregistered Participant ===")
        
        # Create a test trip if none exists
        trip = Trip.query.first()
        if not trip:
            print("Creating a test trip...")
            trip = Trip(
                name="Test Trip",
                description="Test trip for unregistered participants",
                start_date=datetime.now(),
                end_date=datetime.now(),
                admin_id=1,  # Assuming user with ID 1 exists
                participants='[]'
            )
            db.session.add(trip)
            db.session.commit()
            print(f"Created trip: {trip.name} (ID: {trip.id})")
        else:
            print(f"Using existing trip: {trip.name} (ID: {trip.id})")
        
        # Add an unregistered participant
        name = "John Doe"
        print(f"\nAdding unregistered participant: {name}")
        
        # Use the new method to add unregistered participant
        result = trip.add_unregistered_participant(name)
        if result:
            print(f"Successfully added {name} to trip")
        else:
            print(f"Failed to add {name} to trip")
        
        # Check if participant was added
        unregistered = trip.get_unregistered_participants()
        print(f"Current unregistered participants: {unregistered}")
        
        # Verify in database
        participants = UnregisteredParticipant.query.filter_by(trip_id=trip.id).all()
        print(f"Participants in database: {[p.name for p in participants]}")
        
        db.session.commit()

if __name__ == "__main__":
    test_unregistered_participant()