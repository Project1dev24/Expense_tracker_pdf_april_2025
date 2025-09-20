"""
Test the single linking functionality after removing auto-link feature
"""

from app import app
from backend.models.user import User
from backend.models.unregistered_participant import UnregisteredParticipant
from backend.models.trip import Trip
from backend.database import db

def test_single_link_functionality():
    """Test the single link functionality"""
    with app.app_context():
        print("=== Testing Single Link Functionality ===")
        
        # Find an unlinked unregistered participant
        unlinked_participant = UnregisteredParticipant.query.filter_by(linked_user_id=None).first()
        
        if not unlinked_participant:
            print("No unlinked participants found")
            return
            
        print(f"Found unlinked participant: {unlinked_participant.name}")
        
        # Find a user to link to
        test_user = User.query.first()
        if not test_user:
            print("No users found")
            return
            
        print(f"Will link to user: {test_user.name} ({test_user.email})")
        
        # Get the trip for this participant
        trip = unlinked_participant.trip
        print(f"Trip: {trip.name} (ID: {trip.id})")
        
        # Test the linking process (simulating what happens in the route)
        print("\n--- Simulating Link Process ---")
        
        # This is what happens in the route:
        # 1. Find user by email (we already have the user)
        # 2. Check if user is participant or admin (skip for test)
        # 3. Call trip.link_participant()
        
        print(f"Calling trip.link_participant('{unlinked_participant.name}', {test_user.id})")
        result = trip.link_participant(unlinked_participant.name, test_user.id)
        
        if result:
            print("✓ Linking successful!")
            
            # Verify the participant is linked
            updated_participant = UnregisteredParticipant.query.get(unlinked_participant.id)
            print(f"  Participant linked_user_id: {updated_participant.linked_user_id}")
            
            # Verify the user's linked_unregistered_names is updated
            linked_names = test_user.get_linked_unregistered_names()
            print(f"  User's linked_unregistered_names: {linked_names}")
            
            if unlinked_participant.name in linked_names:
                print("✓ User's linked_unregistered_names correctly updated")
            else:
                print("✗ User's linked_unregistered_names not updated correctly")
                
            print(f"\nSuccessfully linked '{unlinked_participant.name}' to '{test_user.name}'")
        else:
            print("✗ Linking failed!")

if __name__ == "__main__":
    test_single_link_functionality()