from app import app
from backend.models.user import User
from backend.models.unregistered_participant import UnregisteredParticipant
from backend.models.expense import Expense
from backend.models.trip import Trip
from backend.database import db
from sqlalchemy import func

def auto_link_remaining_participants():
    """Auto-link remaining unregistered participants to users with matching names"""
    with app.app_context():
        # Get all unregistered participants who are not yet linked
        unregistered_participants = UnregisteredParticipant.query.filter_by(linked_user_id=None).all()
        
        print(f"Found {len(unregistered_participants)} unregistered participants to link")
        
        linked_count = 0
        for participant in unregistered_participants:
            # Look for a user with a matching name (case-insensitive)
            user = User.query.filter(func.lower(User.name) == func.lower(participant.name)).first()
            
            if user:
                print(f"Linking '{participant.name}' to user '{user.name}' (ID: {user.id})")
                
                # Link the participant to the user
                participant.linked_user_id = user.id
                db.session.add(participant)
                
                # Add the participant name to the user's linked_unregistered_names list
                user.add_linked_unregistered_name(participant.name)
                db.session.add(user)
                
                # Update any expenses that were paid by this unregistered participant
                old_payer_id = f"unregistered_{participant.name}"
                expenses = Expense.query.filter_by(payer_id=old_payer_id).all()
                for expense in expenses:
                    expense.payer_id = str(user.id)
                    db.session.add(expense)
                    print(f"  Updated expense ID {expense.id}: payer_id changed from '{old_payer_id}' to '{user.id}'")
                
                linked_count += 1
        
        # Commit all changes
        if linked_count > 0:
            db.session.commit()
            print(f"Successfully linked {linked_count} participants")
        else:
            print("No participants were linked")

if __name__ == "__main__":
    auto_link_remaining_participants()