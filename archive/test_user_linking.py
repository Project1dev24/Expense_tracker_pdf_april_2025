#!/usr/bin/env python3
"""
Test script to verify user linking functionality
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.app_factory import create_app
from backend.models.user import User
from backend.models.trip import Trip
from backend.database import db

def test_user_linking():
    """Test the user linking functionality"""
    app = create_app()
    
    with app.app_context():
        # Get the first trip and user for testing
        trip = Trip.query.first()
        user = User.query.first()
        
        if not trip or not user:
            print("No trip or user found in database")
            return
        
        print(f"Testing with trip: {trip.name}")
        print(f"Testing with user: {user.name} ({user.email})")
        
        # Check current linked unregistered names
        print(f"Current linked unregistered names: {user.get_linked_unregistered_names()}")
        
        # Add a test unregistered participant
        test_name = "test_unregistered_user"
        trip.add_unregistered_participant(test_name)
        db.session.commit()
        
        print(f"Added unregistered participant: {test_name}")
        
        # Link the unregistered participant to the user
        result = trip.link_participant(test_name, user.id)
        
        if result:
            db.session.commit()
            print(f"Successfully linked {test_name} to user {user.name}")
            
            # Check updated linked unregistered names
            updated_names = user.get_linked_unregistered_names()
            print(f"Updated linked unregistered names: {updated_names}")
            
            if test_name in updated_names:
                print("✅ Test passed: Unregistered name added to user's linked list")
            else:
                print("❌ Test failed: Unregistered name not added to user's linked list")
        else:
            print(f"Failed to link {test_name} to user {user.name}")

if __name__ == "__main__":
    test_user_linking()