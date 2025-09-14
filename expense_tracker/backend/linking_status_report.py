from app import app
from backend.models.user import User
from backend.models.unregistered_participant import UnregisteredParticipant
from backend.models.trip import Trip
from backend.database import db

def generate_linking_report():
    """Generate a comprehensive report of linking status"""
    with app.app_context():
        print("=== COMPREHENSIVE LINKING STATUS REPORT ===\n")
        
        # 1. Show all unregistered participants and their linking status
        print("1. ALL UNREGISTERED PARTICIPANTS:")
        print("-" * 50)
        all_participants = UnregisteredParticipant.query.all()
        
        linked_count = 0
        unlinked_count = 0
        
        for participant in all_participants:
            if participant.linked_user_id:
                user = User.query.get(participant.linked_user_id)
                user_info = f"{user.name} ({user.email})" if user else f"User ID {participant.linked_user_id}"
                print(f"  ✓ {participant.name} -> Linked to: {user_info}")
                linked_count += 1
            else:
                print(f"  ○ {participant.name} -> Not linked")
                unlinked_count += 1
        
        print(f"\n  Total: {len(all_participants)} participants")
        print(f"  Linked: {linked_count}")
        print(f"  Unlinked: {unlinked_count}\n")
        
        # 2. Show users and their linked participants
        print("2. REGISTERED USERS WITH LINKED PARTICIPANTS:")
        print("-" * 50)
        users_with_linked = User.query.filter(User.linked_unregistered_names != '[]').all()
        
        for user in users_with_linked:
            linked_names = user.get_linked_unregistered_names()
            print(f"  {user.name} ({user.email}):")
            for name in linked_names:
                print(f"    - {name}")
            print(f"    (Total: {len(linked_names)} linked participants)\n")
        
        # 3. Show unlinked participants that could potentially be linked
        print("3. UNLINKED PARTICIPANTS THAT COULD BE AUTO-LINKED:")
        print("-" * 50)
        unlinked_participants = UnregisteredParticipant.query.filter_by(linked_user_id=None).all()
        auto_linkable = 0
        
        for participant in unlinked_participants:
            # Check if there's a user with a matching name
            matching_user = User.query.filter(
                db.func.lower(User.name) == db.func.lower(participant.name)
            ).first()
            
            if matching_user:
                print(f"  ○ {participant.name} -> Could be linked to {matching_user.name} ({matching_user.email})")
                auto_linkable += 1
            else:
                print(f"  ○ {participant.name} -> No matching user found")
        
        print(f"\n  Total unlinked: {len(unlinked_participants)}")
        print(f"  Auto-linkable: {auto_linkable}")
        print(f"  Need manual linking: {len(unlinked_participants) - auto_linkable}\n")
        
        # 4. Show trips and their participant status
        print("4. TRIP PARTICIPANT STATUS:")
        print("-" * 50)
        trips = Trip.query.all()
        
        for trip in trips:
            print(f"  Trip: {trip.name} (ID: {trip.id})")
            
            # Get unregistered participants for this trip
            unregistered_for_trip = trip.unregistered_participants_list.all()
            linked_in_trip = [p for p in unregistered_for_trip if p.linked_user_id]
            unlinked_in_trip = [p for p in unregistered_for_trip if not p.linked_user_id]
            
            print(f"    Unregistered participants: {len(unregistered_for_trip)}")
            print(f"    Linked: {len(linked_in_trip)}")
            print(f"    Unlinked: {len(unlinked_in_trip)}")
            
            if unlinked_in_trip:
                print("    Unlinked participants:")
                for participant in unlinked_in_trip:
                    matching_user = User.query.filter(
                        db.func.lower(User.name) == db.func.lower(participant.name)
                    ).first()
                    if matching_user:
                        print(f"      ○ {participant.name} (auto-linkable)")
                    else:
                        print(f"      ○ {participant.name}")
            print()

if __name__ == "__main__":
    generate_linking_report()