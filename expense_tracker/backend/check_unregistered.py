from app import app
from backend.models.unregistered_participant import UnregisteredParticipant
from backend.database import db

with app.app_context():
    unregistered = UnregisteredParticipant.query.all()
    print('Unregistered participants in database:')
    for participant in unregistered:
        linked_status = f"Linked to user {participant.linked_user_id}" if participant.linked_user_id else "Not linked"
        print(f'- {participant.name} - {linked_status}')