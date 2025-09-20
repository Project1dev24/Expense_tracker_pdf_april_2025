#!/usr/bin/env python3
"""
Migration script to transfer unregistered participants from JSON field to UnregisteredParticipant table
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app_factory import create_app
from backend.models.trip import Trip
from backend.models.unregistered_participant import UnregisteredParticipant
from backend.database import db

def migrate_unregistered_participants():
    """Migrate unregistered participants from JSON field to new table"""
    app = create_app()
    
    with app.app_context():
        print("=== Starting Migration ===")
        
        # Get all trips
        trips = Trip.query.all()
        print(f"Found {len(trips)} trips")
        
        total_migrated = 0
        
        for trip in trips:
            print(f"\nProcessing trip: {trip.name} (ID: {trip.id})")
            
            # Get current unregistered participants from JSON field
            unregistered_names = trip.get_unregistered_participants()
            print(f"Current unregistered participants: {unregistered_names}")
            
            # Migrate each unregistered participant to the new table
            for name in unregistered_names:
                # Check if participant already exists in new table
                existing = UnregisteredParticipant.query.filter_by(
                    name=name, 
                    trip_id=trip.id
                ).first()
                
                if not existing:
                    # Create new unregistered participant
                    unregistered = UnregisteredParticipant(
                        name=name,
                        trip_id=trip.id
                    )
                    db.session.add(unregistered)
                    print(f"  Migrated '{name}' to new table")
                    total_migrated += 1
                else:
                    print(f"  '{name}' already exists in new table")
        
        # Commit all changes
        db.session.commit()
        print(f"\n=== Migration Complete ===")
        print(f"Total participants migrated: {total_migrated}")

if __name__ == "__main__":
    migrate_unregistered_participants()