from app import app
from backend.models.unregistered_participant import UnregisteredParticipant
from backend.models.user import User
from backend.database import db

with app.app_context():
    # Check linked unregistered participants
    linked_participants = UnregisteredParticipant.query.filter(UnregisteredParticipant.linked_user_id.isnot(None)).all()
    
    print(f'Found {len(linked_participants)} linked unregistered participants:')
    
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
        print(f'\nUser: {user.name} ({user.email}) - ID: {user.id}')
        print(f'  Linked participants: {", ".join(participants)}')
        print(f'  Count: {len(participants)}')