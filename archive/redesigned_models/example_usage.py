"""
Example usage of the redesigned data models
"""

from datetime import datetime
from redesigned_models import db
from redesigned_models.user import User, UserLinkedName
from redesigned_models.trip import Trip, TripParticipant
from redesigned_models.expense import Expense, ExpenseParticipant, ExpenseItem
from redesigned_models.unregistered_participant import UnregisteredParticipant
from redesigned_models.payment import AdvancePayment, GeneralPayment

def create_user(email, name, password):
    """Create a new user"""
    user = User(
        email=email,
        name=name
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def create_trip(name, description, start_date, end_date, admin_user):
    """Create a new trip with an admin user"""
    trip = Trip(
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
        admin_id=admin_user.id
    )
    db.session.add(trip)
    db.session.commit()
    return trip

def add_participant_to_trip(trip, user):
    """Add a registered user as a participant to a trip"""
    # Add user as participant (if not already admin)
    if user.id != trip.admin_id:
        result = trip.add_participant(user.id)
        if result:
            db.session.commit()
            return True
    return False

def add_unregistered_participant_to_trip(trip, name):
    """Add an unregistered participant to a trip"""
    result = trip.add_unregistered_participant(name)
    if result:
        db.session.commit()
        return True
    return False

def create_expense(trip, description, amount, payer, participants, split_method='equal'):
    """Create a new expense for a trip"""
    expense = Expense(
        description=description,
        amount=amount,
        trip_id=trip.id,
        payer_id=str(payer.id) if isinstance(payer, User) else f"unregistered_{payer}",
        split_method=split_method
    )
    db.session.add(expense)
    db.session.flush()  # Get the expense ID
    
    # Add participants
    participant_ids = [str(p.id) if isinstance(p, User) else f"unregistered_{p}" for p in participants]
    expense.set_participants_list(participant_ids)
    
    # Calculate and set shares
    if split_method == 'equal':
        shares = expense.calculate_equal_split()
        expense.set_shares(shares)
    
    db.session.commit()
    return expense

def add_advance_payment(trip, participant, amount):
    """Add an advance payment for a participant"""
    participant_id = str(participant.id) if isinstance(participant, User) else f"unregistered_{participant}"
    
    advance = AdvancePayment(
        trip_id=trip.id,
        participant_id=participant_id,
        amount=amount
    )
    db.session.add(advance)
    db.session.commit()
    return advance

def link_unregistered_participant(trip, unregistered_name, registered_user):
    """Link an unregistered participant to a registered user"""
    result = trip.link_participant(unregistered_name, registered_user.id)
    if result:
        db.session.commit()
        return True
    return False

def calculate_trip_settlements(trip):
    """Calculate settlements for a trip"""
    return trip.calculate_settlements()

# Example usage
if __name__ == "__main__":
    # Create users
    user1 = create_user("alice@example.com", "Alice Smith", "password123")
    user2 = create_user("bob@example.com", "Bob Johnson", "password456")
    user3 = create_user("charlie@example.com", "Charlie Brown", "password789")
    
    # Create a trip
    trip = create_trip(
        "Beach Vacation",
        "Summer vacation at the beach",
        datetime(2025, 6, 1),
        datetime(2025, 6, 10),
        user1  # Alice is the admin
    )
    
    # Add participants
    add_participant_to_trip(trip, user2)  # Bob
    add_participant_to_trip(trip, user3)  # Charlie
    
    # Add unregistered participant
    add_unregistered_participant_to_trip(trip, "david")
    
    # Create expenses
    # Alice pays for dinner, split equally between all participants
    dinner_expense = create_expense(
        trip=trip,
        description="Dinner at seaside restaurant",
        amount=1200.00,
        payer=user1,  # Alice paid
        participants=[user1, user2, user3, "david"],  # All participants
        split_method='equal'
    )
    
    # Bob pays for fuel, with exact amounts
    fuel_expense = create_expense(
        trip=trip,
        description="Fuel for the trip",
        amount=800.00,
        payer=user2,  # Bob paid
        participants=[user1, user2, user3],  # Only registered participants
        split_method='exact'
    )
    
    # Set exact shares for fuel expense
    fuel_shares = {
        str(user1.id): 300.00,  # Alice owes 300
        str(user2.id): 200.00,  # Bob owes 200
        str(user3.id): 300.00   # Charlie owes 300
    }
    fuel_expense.set_shares(fuel_shares)
    
    # Add advance payments
    add_advance_payment(trip, user1, 500.00)  # Alice paid advance
    add_advance_payment(trip, "david", 200.00)  # David paid advance
    
    # Calculate settlements
    settlements = calculate_trip_settlements(trip)
    print("Trip Settlements:")
    for settlement in settlements:
        print(f"  {settlement['from_user']} should pay {settlement['to_user']} ₹{settlement['amount']}")
    
    # Link unregistered participant to registered user
    # Let's say David registers and wants to link his previous expenses
    new_user_david = create_user("david@example.com", "David Wilson", "password000")
    link_unregistered_participant(trip, "david", new_user_david)
    
    # Recalculate settlements after linking
    updated_settlements = calculate_trip_settlements(trip)
    print("\nUpdated Settlements after linking David:")
    for settlement in updated_settlements:
        print(f"  {settlement['from_user']} should pay {settlement['to_user']} ₹{settlement['amount']}")