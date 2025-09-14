from app import app
from backend.models.user import User
from backend.database import db

with app.app_context():
    users = User.query.all()
    print('Users in database:')
    for user in users:
        print(f'- {user.name} ({user.email})')