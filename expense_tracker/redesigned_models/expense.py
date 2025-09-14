from datetime import datetime
import json
from . import db

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='INR')
    category = db.Column(db.String(50), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Split method: 'equal', 'exact', 'itemized'
    split_method = db.Column(db.String(20), default='equal')
    
    # Relationships
    payer_id = db.Column(db.String(100), nullable=False)  # Can be user ID or 'unregistered_name'
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    
    # Define a property to check if payer is registered or unregistered
    @property
    def is_payer_registered(self):
        return not self.payer_id.startswith('unregistered_')
    
    # Relationships for participants and items
    participants_list = db.relationship('ExpenseParticipant', backref='expense', lazy='dynamic', cascade='all, delete-orphan')
    items_list = db.relationship('ExpenseItem', backref='expense', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_participants_list(self):
        """Get list of participant IDs"""
        return [str(ep.participant_id) for ep in self.participants_list]
    
    def set_participants_list(self, participants):
        """Set the participants list by creating ExpenseParticipant records"""
        # Remove existing participants
        for ep in self.participants_list:
            db.session.delete(ep)
        
        # Add new participants
        for participant_id in participants:
            ep = ExpenseParticipant(
                expense_id=self.id,
                participant_id=participant_id
            )
            db.session.add(ep)
    
    def get_shares(self):
        """Get dict of participant shares"""
        shares = {}
        for ep in self.participants_list:
            shares[ep.participant_id] = ep.share_amount
        return shares
    
    def set_shares(self, shares):
        """Set participant shares by updating ExpenseParticipant records"""
        for participant_id, share_amount in shares.items():
            # Find existing participant or create new one
            ep = ExpenseParticipant.query.filter_by(
                expense_id=self.id,
                participant_id=participant_id
            ).first()
            
            if ep:
                ep.share_amount = share_amount
            else:
                ep = ExpenseParticipant(
                    expense_id=self.id,
                    participant_id=participant_id,
                    share_amount=share_amount
                )
                db.session.add(ep)
    
    def get_items(self):
        """Get list of expense items"""
        items = []
        for item in self.items_list:
            items.append({
                'id': item.id,
                'name': item.name,
                'price': item.price,
                'participant_ids': json.loads(item.participant_ids) if item.participant_ids else []
            })
        return items
    
    def set_items(self, items):
        """Set expense items by creating ExpenseItem records"""
        # Remove existing items
        for item in self.items_list:
            db.session.delete(item)
        
        # Add new items
        for item_data in items:
            item = ExpenseItem(
                expense_id=self.id,
                name=item_data['name'],
                price=item_data['price'],
                participant_ids=json.dumps(item_data.get('participant_ids', []))
            )
            db.session.add(item)
        
    def get_unregistered_participants(self):
        """Get unregistered participants from the items data"""
        try:
            unregistered = set()
            for item in self.items_list:
                participants = json.loads(item.participant_ids) if item.participant_ids else []
                for participant_id in participants:
                    if participant_id.startswith('unregistered_'):
                        name = participant_id.replace('unregistered_', '')
                        unregistered.add(name)
            return list(unregistered)
        except Exception as e:
            print(f"Error getting unregistered participants: {str(e)}")
            return []
    
    def calculate_equal_split(self, unregistered_participants=None):
        """Calculate equal shares for all participants including unregistered ones"""
        participants = self.get_participants_list()
        
        # If unregistered_participants parameter is None, try to get it from the expense
        if unregistered_participants is None:
            unregistered_participants = self.get_unregistered_participants()
        
        # Include unregistered participants in the calculation
        total_participants = len(participants)
        if unregistered_participants:
            total_participants += len(unregistered_participants)
        
        if total_participants == 0:
            return {}
        
        # Calculate equal share for each participant
        share = round(self.amount / total_participants, 2)
        
        # Create shares dictionary for registered participants
        shares = {participant: share for participant in participants}
        
        # Add shares for unregistered participants
        for name in unregistered_participants:
            shares[f'unregistered_{name}'] = share
        
        # Adjust for rounding errors
        total = sum(shares.values())
        expected_total = self.amount
        
        if abs(total - expected_total) > 0.01 and shares:  # Only adjust if we have participants and there's a difference
            # Add the difference to the first participant
            first_participant = next(iter(shares.keys()))
            diff = round(expected_total - total, 2)
            shares[first_participant] = round(shares[first_participant] + diff, 2)
        
        return shares
    
    def calculate_exact_split(self, shares_input, unregistered_participants=None):
        """Calculate exact shares based on input, including unregistered participants"""
        if not shares_input:
            return {}
        
        # Convert all values to float for calculation
        processed_shares = {user_id: float(amount) for user_id, amount in shares_input.items()}
        
        # Calculate total of registered participants' shares
        registered_total = sum(processed_shares.values())
        
        # If the total doesn't match the expense amount and we have unregistered participants,
        # it's likely because the unregistered participants' shares aren't included in shares_input
        if abs(registered_total - self.amount) > 0.01 and unregistered_participants:
            # We don't need to raise an error as the unregistered participants' shares are stored separately
            pass
        elif abs(registered_total - self.amount) > 0.01:
            # If no unregistered participants, the totals should match
            # Adjust the first participant's share to make up the difference
            if processed_shares:
                first_key = next(iter(processed_shares))
                diff = round(self.amount - registered_total, 2)
                processed_shares[first_key] = round(processed_shares[first_key] + diff, 2)
        
        return processed_shares
    
    def calculate_itemized_split(self, items_input, unregistered_participants=None):
        """Calculate shares based on items consumed by each participant, including unregistered ones"""
        if not items_input:
            return {}
        
        # Initialize shares for all participants
        shares = {}
        for item in items_input:
            item_price = float(item['price'])
            item_participants = item['participants']
            item_unregistered = item.get('unregistered', [])
            
            # Count total participants for this item (both registered and unregistered)
            total_item_participants = len(item_participants) + len(item_unregistered)
            if total_item_participants == 0:
                continue
                
            # Split item price equally among all item participants
            per_person = round(item_price / total_item_participants, 2)
            
            # Add shares for registered participants
            for participant in item_participants:
                if participant in shares:
                    shares[participant] = round(shares[participant] + per_person, 2)
                else:
                    shares[participant] = per_person
        
        # Validate that sum of shares equals the expense amount
        total = sum(shares.values())
        if abs(total - self.amount) > 0.01:  # Allow for small rounding errors
            # Adjust the first participant's share to match the total
            if shares:  # Only adjust if there are shares
                diff = round(self.amount - total, 2)
                first_participant = list(shares.keys())[0]
                shares[first_participant] = round(shares[first_participant] + diff, 2)
        
        return shares
    
    def update_split(self, split_method, participants, shares_data=None, items_data=None, unregistered_participants=None):
        """Update the expense split based on the selected method"""
        try:
            # Set the split method
            self.split_method = split_method
            
            # Save the registered participants list
            if participants is not None:
                self.set_participants_list(participants)
            
            # Calculate shares based on split method
            if split_method == 'equal':
                # For equal split, include unregistered participants in the calculation
                calculated_shares = self.calculate_equal_split(unregistered_participants)
            elif split_method == 'exact':
                # For exact split, use the provided shares data
                if not shares_data:
                    shares_data = {}
                calculated_shares = self.calculate_exact_split(shares_data, unregistered_participants)
            elif split_method == 'itemized':
                # For itemized split, use the provided items data
                if not items_data:
                    items_data = []
                calculated_shares = self.calculate_itemized_split(items_data, unregistered_participants)
            else:
                raise ValueError(f"Invalid split method: {split_method}")
            
            # Save the calculated shares
            self.set_shares(calculated_shares)
            
            # If we have items data, save it
            if items_data and isinstance(items_data, list):
                self.set_items(items_data)
            
            return calculated_shares
        except Exception as e:
            import traceback
            print(f"Error in update_split: {str(e)}")
            traceback.print_exc()
            raise
    
    def __repr__(self):
        return f'<Expense {self.description}: {self.currency} {self.amount}>'


class ExpenseParticipant(db.Model):
    __tablename__ = 'expense_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=False)
    participant_id = db.Column(db.String(100), nullable=False)  # Can be user ID or 'unregistered_name'
    share_amount = db.Column(db.Float, default=0.0)
    
    # Ensure a participant can't be added to the same expense multiple times
    __table_args__ = (db.UniqueConstraint('expense_id', 'participant_id', name='unique_expense_participant'),)
    
    def __repr__(self):
        return f'<ExpenseParticipant expense:{self.expense_id} participant:{self.participant_id}>'


class ExpenseItem(db.Model):
    __tablename__ = 'expense_items'
    
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    participant_ids = db.Column(db.Text, nullable=True)  # JSON array of participant IDs
    
    def __repr__(self):
        return f'<ExpenseItem {self.name}: {self.price}>'