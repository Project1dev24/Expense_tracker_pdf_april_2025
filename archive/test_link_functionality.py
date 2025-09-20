from app import app
from backend.models.user import User
from backend.models.unregistered_participant import UnregisteredParticipant
from backend.models.trip import Trip
from backend.database import db

def test_link_functionality():
    """Test the link functionality by linking an unregistered participant to a registered user"""
    with app.app_context():
        # Find an unlinked unregistered participant
        unlinked_participant = UnregisteredParticipant.query.filter_by(linked_user_id=None).first()
        
        if not unlinked_participant:
            print("No unlinked participants found")
            return
            
        print(f"Found unlinked participant: {unlinked_participant.name}")
        
        # Find a user with a matching name
        matching_user = User.query.filter(
            db.func.lower(User.name) == db.func.lower(unlinked_participant.name)
        ).first()
        
        if not matching_user:
            print(f"No matching user found for '{unlinked_participant.name}'")
            # Let's try linking to a specific user for testing
            test_user = User.query.first()
            print(f"Will link to test user: {test_user.name} ({test_user.email})")
            matching_user = test_user
        
        print(f"Linking '{unlinked_participant.name}' to '{matching_user.name}' (ID: {matching_user.id})")
        
        # Get the trip for this participant
        trip = unlinked_participant.trip
        print(f"Trip: {trip.name} (ID: {trip.id})")
        
        # Link the participant
        result = trip.link_participant(unlinked_participant.name, matching_user.id)
        
        if result:
            print("Linking successful!")
            print(f"Participant linked_user_id: {unlinked_participant.linked_user_id}")
            
            # Check the user's linked_unregistered_names
            linked_names = matching_user.get_linked_unregistered_names()
            print(f"User's linked_unregistered_names: {linked_names}")
        else:
            print("Linking failed!")

if __name__ == "__main__":
    test_link_functionality()