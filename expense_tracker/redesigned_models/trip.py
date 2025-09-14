from datetime import datetime
from . import db

class Trip(db.Model):
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Admin user who created the trip
    admin_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    participants = db.relationship('TripParticipant', backref='trip', lazy='dynamic', cascade='all, delete-orphan')
    expenses = db.relationship('Expense', backref='trip', lazy='dynamic', cascade='all, delete-orphan')
    unregistered_participants = db.relationship('UnregisteredParticipant', backref='trip', lazy='dynamic', cascade='all, delete-orphan')
    advance_payments = db.relationship('AdvancePayment', backref='trip', lazy='dynamic', cascade='all, delete-orphan')
    general_payments = db.relationship('GeneralPayment', backref='trip', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_registered_participant_ids(self):
        """Get list of registered participant user IDs"""
        return [str(tp.user_id) for tp in self.participants]
    
    def get_unregistered_participants(self):
        """Get list of unregistered participant names that are not yet linked"""
        return [participant.name for participant in self.unregistered_participants.filter_by(linked_user_id=None).all()]
    
    def get_unregistered_participants_display(self):
        """Get unregistered participants with names in title case for display"""
        participants = self.get_unregistered_participants()
        return [name.title() for name in participants]
    
    def get_unregistered_participant_display_name(self, name):
        """Convert a stored lowercase name to title case for display"""
        return name.title()
    
    def add_participant(self, user_id):
        """Add a registered participant to the trip"""
        # Check if participant already exists
        existing = TripParticipant.query.filter_by(
            trip_id=self.id,
            user_id=user_id
        ).first()
        
        if not existing and user_id != self.admin_id:
            participant = TripParticipant(
                trip_id=self.id,
                user_id=user_id
            )
            db.session.add(participant)
            return True
        return False
        
    def add_unregistered_participant(self, name):
        """Add an unregistered participant by name to the trip"""
        # Check if participant already exists
        existing = self.unregistered_participants.filter_by(
            name=name.strip().lower()
        ).first()
        
        if not existing:
            unregistered = UnregisteredParticipant(
                name=name.strip().lower(),
                trip_id=self.id
            )
            db.session.add(unregistered)
            return True
        return False
    
    def remove_participant(self, user_id):
        """Remove a registered participant from the trip"""
        participant = TripParticipant.query.filter_by(
            trip_id=self.id,
            user_id=user_id
        ).first()
        
        if participant:
            db.session.delete(participant)
            return True
        return False
    
    def remove_unregistered_participant(self, name):
        """Remove an unregistered participant from the trip"""
        participant = self.unregistered_participants.filter_by(
            name=name.strip().lower()
        ).first()
        
        if participant:
            db.session.delete(participant)
            return True
        return False
        
    def link_participant(self, name, user_id):
        """Link an unregistered participant to a registered user"""
        # Find the unregistered participant in the database
        participant = self.unregistered_participants.filter_by(
            name=name.strip().lower()
        ).first()
        
        if not participant:
            return False
            
        # Set the linked user ID
        participant.linked_user_id = user_id
        db.session.add(participant)
        
        # Add to registered list (unless user is already admin)
        result = True
        if int(user_id) != self.admin_id:
            result = self.add_participant(user_id)
        
        # Update all expense records to replace the unregistered participant with the registered user
        # Create the unregistered ID that was used in expenses
        unregistered_id = f"unregistered_{participant.name}"
        
        # Update all expenses
        for expense in self.expenses:
            # Update payer_id if it matches the unregistered participant ID
            if expense.payer_id == unregistered_id:
                expense.payer_id = str(user_id)
            
            # Update participants list if it contains the unregistered participant ID
            participants = expense.get_participants_list()
            if unregistered_id in participants:
                participants.remove(unregistered_id)
                participants.append(str(user_id))
                expense.set_participants_list(participants)
            
            # Update shares to replace the unregistered participant with the registered user
            shares = expense.get_shares()
            if unregistered_id in shares:
                amount = shares.pop(unregistered_id)
                shares[str(user_id)] = amount
                expense.set_shares(shares)
        
        # Update advances to replace the unregistered participant with the registered user
        for advance in self.advance_payments:
            if advance.participant_id == unregistered_id:
                advance.participant_id = str(user_id)
        
        # Update general payments to replace the unregistered participant with the registered user
        for payment in self.general_payments:
            if payment.participant_id == unregistered_id:
                payment.participant_id = str(user_id)
        
        # Add the unregistered name to the user's linked list
        from .user import User
        user = User.query.get(user_id)
        if user:
            user.add_linked_unregistered_name(participant.name)
        
        # Commit all changes
        db.session.commit()
        
        # Return the result of add_participant (True if user was added, False if already a participant)
        return result
    
    def calculate_total_expenses(self):
        """Calculate total expenses for this trip"""
        return sum(expense.amount for expense in self.expenses)
    
    def calculate_user_balance(self, user_id):
        """Calculate net balance for a specific user"""
        from .expense import Expense
        
        # Check if this is an unregistered participant
        if isinstance(user_id, str) and user_id.startswith('unregistered_'):
            return self.calculate_unregistered_balance(user_id)
        
        # Total paid by user (expenses they covered)
        total_paid = sum(expense.amount for expense in 
                         self.expenses.filter_by(payer_id=str(user_id)))
        
        # Add general payments made by this user
        total_paid += self.get_participant_general_payments(user_id)
        
        # Add advance payments
        advance_amount = sum(advance.amount for advance in 
                            self.advance_payments.filter_by(participant_id=str(user_id)))
        total_paid += advance_amount
        
        # Total share of user
        total_share = 0
        for expense in self.expenses:
            shares = expense.get_shares()
            if str(user_id) in shares:
                total_share += shares[str(user_id)]
        
        # Positive means user is owed money, negative means user owes money
        return total_paid - total_share
        
    def calculate_unregistered_balance(self, unregistered_id):
        """Calculate balance for an unregistered participant"""
        total_share = 0
        balance = 0
        
        # Get any advance payments for this participant
        advance_amount = sum(advance.amount for advance in 
                            self.advance_payments.filter_by(participant_id=unregistered_id))
        
        # Add general payments made by this participant
        general_payments = self.get_participant_general_payments(unregistered_id)
        
        # Total paid = advances + general payments
        total_paid = advance_amount + general_payments
        
        # Calculate their total share
        for expense in self.expenses:
            shares = expense.get_shares()
            if unregistered_id in shares:
                # If they were included in an expense, add their share
                total_share -= shares[unregistered_id]
                
            # If they paid for an expense (unlikely but possible), add the amount
            if expense.payer_id == unregistered_id:
                balance += expense.amount
        
        # Calculate balance: total paid minus their share
        # Positive means they are owed money, negative means they owe money
        balance += total_share
        return balance
    
    def get_participant_general_payments(self, participant_id):
        """Get total general payments made by a participant"""
        return sum(payment.amount for payment in 
                  self.general_payments.filter_by(participant_id=str(participant_id)))
    
    def calculate_settlements(self):
        """Calculate how to settle debts between participants"""
        try:
            # Get all registered participants including admin
            registered_participants = self.get_registered_participant_ids()
            if str(self.admin_id) not in registered_participants:
                registered_participants.append(str(self.admin_id))
                
            # Get all unregistered participants
            unregistered_participants = self.get_unregistered_participants()
            
            # Calculate balance for each registered participant
            balances = {}
            for participant_id in registered_participants:
                balance = self.calculate_user_balance(participant_id)
                # Only include non-zero balances to optimize memory
                if abs(balance) > 0.01:
                    balances[participant_id] = balance
                    
            # Calculate balance for each unregistered participant
            for name in unregistered_participants:
                # Create a unique ID for the unregistered participant
                unregistered_id = f'unregistered_{name}'
                
                # Calculate their balance across all expenses
                balance = 0
                for expense in self.expenses:
                    shares = expense.get_shares()
                    if unregistered_id in shares:
                        # If they were included in an expense, add their share
                        balance -= shares[unregistered_id]
                        
                    # If they paid for an expense (unlikely but possible), add the amount
                    if expense.payer_id == unregistered_id:
                        balance += expense.amount
                
                # Only include non-zero balances
                if abs(balance) > 0.01:
                    balances[unregistered_id] = balance
            
            # If no significant balances, return empty settlements
            if not balances:
                return []
            
            # Calculate settlements
            settlements = []
            max_iterations = 100  # Prevent infinite loops
            iteration = 0
            
            while balances and iteration < max_iterations:
                iteration += 1
                
                # Find max creditor and max debtor
                max_creditor = max(balances.items(), key=lambda x: x[1]) if balances else None
                max_debtor = min(balances.items(), key=lambda x: x[1]) if balances else None
                
                # If all balances are settled (close to zero), we're done
                if not max_creditor or not max_debtor or abs(max_creditor[1]) < 0.01 or abs(max_debtor[1]) < 0.01:
                    break
                
                # Calculate settlement amount
                amount = min(max_creditor[1], -max_debtor[1])
                
                # Round to 2 decimal places to avoid floating point issues
                amount = round(amount, 2)
                
                if amount <= 0:
                    break  # No more meaningful settlements to make
                
                # Create settlement
                settlements.append({
                    'from_user': max_debtor[0],
                    'to_user': max_creditor[0],
                    'amount': amount
                })
                
                # Update balances
                balances[max_creditor[0]] -= amount
                balances[max_debtor[0]] += amount
                
                # Remove settled balances to save memory
                balances = {k: v for k, v in balances.items() if abs(v) > 0.01}
            
            # Limit the number of settlements to return (memory optimization)
            return settlements[:20]  # Return at most 20 settlements
            
        except Exception as e:
            print(f"Error calculating settlements: {str(e)}")
            import traceback
            traceback.print_exc()
            return []  # Return empty list on error
    
    def __repr__(self):
        return f'<Trip {self.name}: {self.start_date.date()} to {self.end_date.date()}>'


class TripParticipant(db.Model):
    __tablename__ = 'trip_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure a user can't be added to the same trip multiple times
    __table_args__ = (db.UniqueConstraint('trip_id', 'user_id', name='unique_trip_user'),)
    
    def __repr__(self):
        return f'<TripParticipant trip:{self.trip_id} user:{self.user_id}>'