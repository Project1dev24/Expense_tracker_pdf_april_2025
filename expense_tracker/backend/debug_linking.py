#!/usr/bin/env python3
"""
Debug script to test the linking functionality and identify the issue with missing participant name
"""

from app import app
from backend.models.user import User
from backend.models.unregistered_participant import UnregisteredParticipant
from backend.models.trip import Trip
from backend.database import db

def debug_linking_process():
    """Debug the linking process to identify where the participant name is lost"""
    with app.app_context():
        print("=== Debugging Linking Process ===")
        
        # Find an unlinked unregistered participant
        unlinked_participant = UnregisteredParticipant.query.filter_by(linked_user_id=None).first()
        
        if not unlinked_participant:
            print("No unlinked participants found")
            return
            
        print(f"Found unlinked participant: {unlinked_participant.name}")
        print(f"Participant name type: {type(unlinked_participant.name)}")
        print(f"Participant name length: {len(unlinked_participant.name)}")
        print(f"Participant name repr: {repr(unlinked_participant.name)}")
        
        # Find a user to link to
        test_user = User.query.first()
        if not test_user:
            print("No users found")
            return
            
        print(f"Will link to user: {test_user.name} ({test_user.email})")
        
        # Get the trip for this participant
        trip = unlinked_participant.trip
        print(f"Trip: {trip.name} (ID: {trip.id})")
        
        # Test the linking process with the exact name
        print(f"\nTesting link_participant with name: {repr(unlinked_participant.name)}")
        print(f"Name after strip: {repr(unlinked_participant.name.strip())}")
        print(f"Name after strip and lower: {repr(unlinked_participant.name.strip().lower())}")
        
        # Try to find the participant in the database using the same logic as link_participant
        print("\n--- Testing database query ---")
        participant_query = trip.unregistered_participants_list.filter_by(name=unlinked_participant.name.strip().lower())
        print(f"Query: {participant_query}")
        found_participant = participant_query.first()
        print(f"Found participant: {found_participant}")
        if found_participant:
            print(f"Found participant name: {found_participant.name}")
        else:
            print("Participant not found with this query!")
            
        # Try alternative queries
        print("\n--- Testing alternative queries ---")
        # Try with exact name
        exact_query = trip.unregistered_participants_list.filter_by(name=unlinked_participant.name)
        exact_result = exact_query.first()
        print(f"Exact name query result: {exact_result}")
        
        # Try with stripped name
        stripped_query = trip.unregistered_participants_list.filter_by(name=unlinked_participant.name.strip())
        stripped_result = stripped_query.first()
        print(f"Stripped name query result: {stripped_result}")
        
        # Try with lowercased name
        lower_query = trip.unregistered_participants_list.filter_by(name=unlinked_participant.name.lower())
        lower_result = lower_query.first()
        print(f"Lowercased name query result: {lower_result}")

if __name__ == "__main__":
    debug_linking_process()