"""
Link Participant Workflow - How the "Link to User" functionality works

This script demonstrates the complete workflow when a user clicks "Link to User":
1. User selects an unregistered participant from the list
2. User clicks "Link to User" which opens the modal
3. User enters an email address or selects a user from the list
4. System finds the user by email
5. System links the participant to the user
6. System updates all related data
7. System adds the participant to registered participants
"""

from app import app
from backend.models.user import User
from backend.models.unregistered_participant import UnregisteredParticipant
from backend.models.trip import Trip
from backend.database import db
from sqlalchemy import func

def link_participant_workflow(unregistered_name, user_email):
    """
    Complete workflow for linking an unregistered participant to a registered user
    
    Args:
        unregistered_name (str): Name of the unregistered participant
        user_email (str): Email of the registered user to link to
    """
    with app.app_context():
        print("=== LINK PARTICIPANT WORKFLOW ===")
        print(f"Linking '{unregistered_name}' to user with email '{user_email}'")
        print()
        
        # Step 1: Find the unregistered participant
        print("Step 1: Finding unregistered participant...")
        participant = UnregisteredParticipant.query.filter_by(name=unregistered_name.strip().lower()).first()
        if not participant:
            print(f"ERROR: Participant '{unregistered_name}' not found")
            return False
        print(f"✓ Found participant: {participant.name}")
        print()
        
        # Step 2: Find the registered user by email (case-insensitive)
        print("Step 2: Finding registered user by email...")
        user = User.query.filter(func.lower(User.email) == func.lower(user_email)).first()
        if not user:
            print(f"ERROR: User with email '{user_email}' not found")
            return False
        print(f"✓ Found user: {user.name} ({user.email})")
        print()
        
        # Step 3: Get the trip for this participant
        print("Step 3: Getting trip information...")
        trip = participant.trip
        if not trip:
            print("ERROR: Trip not found for participant")
            return False
        print(f"✓ Trip: {trip.name} (ID: {trip.id})")
        print()
        
        # Step 4: Link the participant to the user
        print("Step 4: Linking participant to user...")
        result = trip.link_participant(participant.name, user.id)
        if not result:
            print("ERROR: Failed to link participant to user")
            return False
        print("✓ Participant successfully linked to user")
        print(f"  - Participant linked_user_id set to: {participant.linked_user_id}")
        print()
        
        # Step 5: Verify the linking was successful
        print("Step 5: Verifying linking results...")
        # Check that the participant is now linked
        updated_participant = UnregisteredParticipant.query.get(participant.id)
        if updated_participant.linked_user_id != user.id:
            print("ERROR: Participant linking verification failed")
            return False
        print("✓ Participant linking verified")
        
        # Check that the user's linked_unregistered_names was updated
        linked_names = user.get_linked_unregistered_names()
        if participant.name not in linked_names:
            print("ERROR: User linked_unregistered_names not updated")
            return False
        print("✓ User linked_unregistered_names updated")
        print(f"  - User now has linked participants: {linked_names}")
        print()
        
        # Step 6: Verify the participant was added to registered participants
        print("Step 6: Verifying participant added to registered participants...")
        participant_ids = trip.get_participants_list()
        if str(user.id) not in participant_ids:
            print("Note: User was not automatically added to trip participants (may be admin)")
        else:
            print("✓ User added to trip participants")
        print()
        
        print("=== LINKING COMPLETE ===")
        print(f"Successfully linked '{participant.name}' to '{user.name}'")
        return True

def demonstrate_workflow():
    """Demonstrate the linking workflow with a real example"""
    with app.app_context():
        # Find an unlinked participant
        unlinked_participant = UnregisteredParticipant.query.filter_by(linked_user_id=None).first()
        if not unlinked_participant:
            print("No unlinked participants found")
            return
            
        # Find a user to link to (using the first user as an example)
        user = User.query.first()
        if not user:
            print("No users found")
            return
            
        print(f"Demonstrating workflow with:")
        print(f"  Unregistered participant: {unlinked_participant.name}")
        print(f"  Registered user: {user.name} ({user.email})")
        print()
        
        # Run the workflow
        link_participant_workflow(unlinked_participant.name, user.email)

if __name__ == "__main__":
    demonstrate_workflow()