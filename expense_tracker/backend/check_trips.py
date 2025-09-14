from app import app
from backend.models.trip import Trip
from backend.database import db

with app.app_context():
    trips = Trip.query.all()
    print('Trips in database:')
    for trip in trips:
        print(f'- {trip.name} (ID: {trip.id}) - Admin: {trip.admin.name if trip.admin else "None"}')
        # Show unregistered participants for this trip
        unregistered = trip.unregistered_participants_list.all()
        if unregistered:
            print(f'  Unregistered participants:')
            for participant in unregistered:
                linked_status = f"Linked to user {participant.linked_user_id}" if participant.linked_user_id else "Not linked"
                print(f'    - {participant.name} - {linked_status}')