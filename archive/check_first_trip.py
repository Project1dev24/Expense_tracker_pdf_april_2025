from app import app
from backend.models.trip import Trip

with app.app_context():
    trip = Trip.query.first()
    if trip:
        print(f'First trip: {trip.name} (ID: {trip.id})')
    else:
        print('No trips found')