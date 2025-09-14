from app import app
from backend.models.user import User
from backend.database import db

with app.app_context():
    # Check a specific user (let's use the first one)
    user = User.query.first()
    if user:
        print(f'User: {user.name} ({user.email})')
        print(f'Linked unregistered names: {user.get_linked_unregistered_names()}')
        
        # Also check the raw field value
        print(f'Raw linked_unregistered_names field: {user.linked_unregistered_names}')
    else:
        print('No users found')