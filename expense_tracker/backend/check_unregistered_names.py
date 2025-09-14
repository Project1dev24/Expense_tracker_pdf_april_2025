"""
Check what unregistered participant names are available in the database
"""

from app import app
from backend.models.unregistered_participant import UnregisteredParticipant

def check_unregistered_names():
    """Check unregistered participant names"""
    with app.app_context():
        # Get all unlinked unregistered participants
        unlinked_participants = UnregisteredParticipant.query.filter_by(linked_user_id=None).all()
        
        print("Unlinked unregistered participants:")
        for participant in unlinked_participants:
            print(f"  - {repr(participant.name)} (length: {len(participant.name)})")
            
        # Get all unregistered participants
        all_participants = UnregisteredParticipant.query.all()
        
        print("\nAll unregistered participants:")
        for participant in all_participants:
            status = "Linked" if participant.linked_user_id else "Unlinked"
            print(f"  - {repr(participant.name)} (length: {len(participant.name)}) - {status}")

if __name__ == "__main__":
    check_unregistered_names()