from app import app
from backend.models.user import User
from backend.models.unregistered_participant import UnregisteredParticipant
from backend.models.trip import Trip
from backend.database import db

def fix_linking_consistency():
    """Fix any inconsistencies between linked participants and user tracking"""
    with app.app_context():
        print("Checking linking consistency...")
        
        # Get all linked unregistered participants
        linked_participants = UnregisteredParticipant.query.filter(
            UnregisteredParticipant.linked_user_id.isnot(None)
        ).all()
        
        print(f"Found {len(linked_participants)} linked participants")
        
        # Create a mapping of user_id to list of linked participant names
        user_linked_names = {}
        for participant in linked_participants:
            user_id = participant.linked_user_id
            if user_id not in user_linked_names:
                user_linked_names[user_id] = []
            user_linked_names[user_id].append(participant.name)
        
        # Update each user's linked_unregistered_names field
        updated_users = 0
        for user_id, names in user_linked_names.items():
            user = User.query.get(user_id)
            if user:
                print(f"Updating user {user.name} (ID: {user_id}) with linked names: {names}")
                user.set_linked_unregistered_names(names)
                updated_users += 1
        
        if updated_users > 0:
            db.session.commit()
            print(f"Updated {updated_users} users with correct linked_unregistered_names")
        else:
            print("No inconsistencies found")

def display_linking_status():
    """Display the current linking status"""
    with app.app_context():
        print("\n=== LINKING STATUS REPORT ===")
        
        # Get all users with linked participants
        users_with_linked = User.query.filter(User.linked_unregistered_names != '[]').all()
        
        print(f"Users with linked participants: {len(users_with_linked)}")
        
        for user in users_with_linked:
            linked_names = user.get_linked_unregistered_names()
            print(f"\nUser: {user.name} ({user.email}) - ID: {user.id}")
            print(f"  Linked participants: {', '.join(linked_names)}")
            print(f"  Count: {len(linked_names)}")
        
        # Get all linked unregistered participants
        linked_participants = UnregisteredParticipant.query.filter(
            UnregisteredParticipant.linked_user_id.isnot(None)
        ).all()
        
        print(f"\nTotal linked unregistered participants in database: {len(linked_participants)}")
        
        # Group by user
        user_links = {}
        for participant in linked_participants:
            user_id = participant.linked_user_id
            if user_id not in user_links:
                user_links[user_id] = {
                    'user': User.query.get(user_id),
                    'participants': []
                }
            user_links[user_id]['participants'].append(participant.name)
        
        # Display results
        for user_id, data in user_links.items():
            user = data['user']
            participants = data['participants']
            print(f"\nUser: {user.name} ({user.email}) - ID: {user.id}")
            print(f"  Linked participants: {', '.join(participants)}")
            print(f"  Count: {len(participants)}")

if __name__ == "__main__":
    display_linking_status()
    fix_linking_consistency()
    print("\n" + "="*50)
    display_linking_status()