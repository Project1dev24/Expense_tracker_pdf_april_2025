# Migration Guide: Old Data Model to Redesigned Data Model

This guide explains how to migrate from the existing data model to the redesigned model.

## Key Changes

1. **Normalized Relationships**: Replaced JSON fields with proper relational tables
2. **Explicit Junction Tables**: Created dedicated tables for many-to-many relationships
3. **Improved Data Integrity**: Added proper constraints and foreign keys
4. **Better Separation of Concerns**: Split functionality into more focused entities

## Migration Steps

### 1. Database Schema Changes

First, create the new tables and relationships:

```sql
-- Create new tables (simplified SQL for illustration)
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    -- ... other fields
);

CREATE TABLE trips (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    admin_id INTEGER REFERENCES users(id),
    -- ... other fields
);

CREATE TABLE trip_participants (
    id INTEGER PRIMARY KEY,
    trip_id INTEGER REFERENCES trips(id),
    user_id INTEGER REFERENCES users(id),
    UNIQUE(trip_id, user_id)
);

-- ... and so on for all new tables
```

### 2. Data Migration Process

#### Users Migration
- Direct copy of existing user data
- No structural changes needed

#### Trips Migration
- Direct copy of existing trip data
- Convert JSON participants list to TripParticipant records

```python
# Example migration code
def migrate_trips():
    # Get all existing trips
    old_trips = OldTrip.query.all()
    
    for old_trip in old_trips:
        # Create new trip with same data
        new_trip = Trip(
            name=old_trip.name,
            description=old_trip.description,
            start_date=old_trip.start_date,
            end_date=old_trip.end_date,
            created_at=old_trip.created_at,
            updated_at=old_trip.updated_at,
            admin_id=old_trip.admin_id
        )
        db.session.add(new_trip)
        db.session.flush()  # Get the new ID
        
        # Convert JSON participants to TripParticipant records
        participant_ids = old_trip.get_participants_list()
        for user_id in participant_ids:
            if int(user_id) != old_trip.admin_id:  # Admin is not stored as participant
                tp = TripParticipant(
                    trip_id=new_trip.id,
                    user_id=int(user_id)
                )
                db.session.add(tp)
```

#### Expenses Migration
- Direct copy of existing expense data
- Convert JSON participants and shares to ExpenseParticipant records

```python
# Example migration code
def migrate_expenses():
    # Get all existing expenses
    old_expenses = OldExpense.query.all()
    
    for old_expense in old_expenses:
        # Create new expense with same data
        new_expense = Expense(
            description=old_expense.description,
            amount=old_expense.amount,
            currency=old_expense.currency,
            category=old_expense.category,
            date=old_expense.date,
            created_at=old_expense.created_at,
            updated_at=old_expense.updated_at,
            split_method=old_expense.split_method,
            payer_id=old_expense.payer_id,
            trip_id=old_expense.trip_id
        )
        db.session.add(new_expense)
        db.session.flush()  # Get the new ID
        
        # Convert JSON participants to ExpenseParticipant records
        participant_ids = old_expense.get_participants_list()
        for participant_id in participant_ids:
            ep = ExpenseParticipant(
                expense_id=new_expense.id,
                participant_id=participant_id
            )
            db.session.add(ep)
        
        # Convert JSON shares to ExpenseParticipant share_amount
        shares = old_expense.get_shares()
        for participant_id, share_amount in shares.items():
            ep = ExpenseParticipant.query.filter_by(
                expense_id=new_expense.id,
                participant_id=participant_id
            ).first()
            if ep:
                ep.share_amount = share_amount
```

#### Payments Migration
- Convert JSON advances to AdvancePayment records
- Convert JSON general payments to GeneralPayment records

```python
# Example migration code for advances
def migrate_advances():
    old_trips = OldTrip.query.all()
    
    for old_trip in old_trips:
        advances = old_trip.get_advances()
        for participant_id, amount in advances.items():
            advance = AdvancePayment(
                trip_id=old_trip.id,
                participant_id=participant_id,
                amount=amount
            )
            db.session.add(advance)

# Example migration code for general payments
def migrate_general_payments():
    old_trips = OldTrip.query.all()
    
    for old_trip in old_trips:
        payments = old_trip.get_general_payments()
        for payment_data in payments:
            payment = GeneralPayment(
                trip_id=old_trip.id,
                participant_id=payment_data['participant_id'],
                amount=payment_data['amount'],
                description=payment_data['description'],
                date=datetime.strptime(payment_data['date'], '%Y-%m-%d') if isinstance(payment_data['date'], str) else payment_data['date'],
                expense_id=payment_data.get('expense_id')
            )
            db.session.add(payment)
```

### 3. Code Updates

Update the application code to use the new model structure:

#### Before (Old Model)
```python
# Adding a participant
trip.participants = json.dumps([...])

# Getting participants
participants = json.loads(trip.participants)

# Adding an expense share
shares = json.loads(expense.shares)
shares['user_id'] = amount
expense.shares = json.dumps(shares)
```

#### After (New Model)
```python
# Adding a participant
participant = TripParticipant(trip_id=trip.id, user_id=user_id)
db.session.add(participant)

# Getting participants
participants = [tp.user_id for tp in trip.participants]

# Adding an expense share
expense_participant = ExpenseParticipant(
    expense_id=expense.id,
    participant_id=user_id,
    share_amount=amount
)
db.session.add(expense_participant)
```

## Benefits of the Redesigned Model

1. **Better Performance**: Proper indexing and relationships
2. **Data Integrity**: Constraints prevent invalid data
3. **Scalability**: Easier to extend and modify
4. **Maintainability**: Clearer code structure
5. **Query Efficiency**: Direct joins instead of JSON parsing

## Testing the Migration

1. Create a backup of the existing database
2. Run the migration scripts on a test database
3. Verify data integrity and relationships
4. Test all application functionality
5. Run performance benchmarks

## Rollback Plan

If issues are found after migration:

1. Restore the database from backup
2. Revert code changes
3. Identify and fix migration issues
4. Retry migration with fixes