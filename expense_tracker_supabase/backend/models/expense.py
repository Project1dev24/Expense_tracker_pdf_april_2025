#!/usr/bin/env python3
"""
Expense model for Supabase integration
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

@dataclass
class Expense:
    """Expense model for tracking trip expenses"""
    id: Optional[str] = None  # Supabase will generate UUID
    description: str = ""
    amount: float = 0.0
    currency: str = "INR"
    category: Optional[str] = None
    date: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    # Split method: 'equal', 'exact', 'itemized'
    split_method: str = "equal"
    
    # Relationships
    payer_id: str = ""  # Can be user ID or 'unregistered_name'
    trip_id: str = ""
    
    # Lists and dictionaries to store participant data
    participants: List[str] = field(default_factory=list)
    shares: Dict[str, float] = field(default_factory=dict)
    items: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def is_payer_registered(self) -> bool:
        """Check if payer is registered or unregistered"""
        return not self.payer_id.startswith('unregistered_')
    
    def get_participants_list(self) -> List[str]:
        """Get list of participant IDs"""
        return self.participants
    
    def set_participants_list(self, participants: List[str]):
        """Set list of participant IDs"""
        self.participants = participants
    
    def get_shares(self) -> Dict[str, float]:
        """Get dict of shares"""
        return self.shares
    
    def set_shares(self, shares: Dict[str, float]):
        """Set dict of shares"""
        self.shares = shares
    
    def get_items(self) -> List[Dict[str, Any]]:
        """Get list of items"""
        return self.items
    
    def set_items(self, items: List[Dict[str, Any]]):
        """Set list of items"""
        self.items = items
    
    def calculate_equal_split(self, unregistered_participants: Optional[List[str]] = None) -> Dict[str, float]:
        """Calculate equal shares for all participants including unregistered ones"""
        participants = self.get_participants_list()
        
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
        for name in unregistered_participants or []:
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
    
    def calculate_exact_split(self, shares_input: Dict[str, float], 
                            unregistered_participants: Optional[List[str]] = None) -> Dict[str, float]:
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
    
    def calculate_itemized_split(self, items_input: List[Dict[str, Any]], 
                               unregistered_participants: Optional[List[str]] = None) -> Dict[str, float]:
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
            
            # Add shares for unregistered participants
            for name in item_unregistered:
                unregistered_id = f'unregistered_{name}'
                if unregistered_id in shares:
                    shares[unregistered_id] = round(shares[unregistered_id] + per_person, 2)
                else:
                    shares[unregistered_id] = per_person
        
        # Validate that sum of shares equals the expense amount
        total = sum(shares.values())
        if abs(total - self.amount) > 0.01:  # Allow for small rounding errors
            # Adjust the first participant's share to match the total
            diff = round(self.amount - total, 2)
            first_participant = list(shares.keys())[0]
            shares[first_participant] = round(shares[first_participant] + diff, 2)
        
        return shares
    
    def update_split(self, split_method: str, participants: List[str], 
                    shares_data: Optional[Dict[str, float]] = None,
                    items_data: Optional[List[Dict[str, Any]]] = None,
                    unregistered_participants: Optional[List[str]] = None):
        """Update the expense split based on the selected method"""
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
        return calculated_shares
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Expense':
        """Create an Expense instance from dictionary data"""
        # Parse dates
        date = datetime.fromisoformat(data['date']) if data.get('date') else datetime.utcnow()
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow()
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.utcnow()
        
        # Parse JSON fields - handle both string and dict/list cases
        try:
            participants = json.loads(data.get('participants', '[]')) if isinstance(data.get('participants', '[]'), str) else data.get('participants', [])
        except (json.JSONDecodeError, TypeError):
            participants = []
            
        try:
            shares = json.loads(data.get('shares', '{}')) if isinstance(data.get('shares', '{}'), str) else data.get('shares', {})
        except (json.JSONDecodeError, TypeError):
            shares = {}
            
        try:
            items = json.loads(data.get('items', '[]')) if isinstance(data.get('items', '[]'), str) else data.get('items', [])
        except (json.JSONDecodeError, TypeError):
            items = []
        
        return cls(
            id=data.get('id'),
            description=data.get('description', ''),
            amount=float(data.get('amount', 0.0)),
            currency=data.get('currency', 'INR'),
            category=data.get('category'),
            date=date,
            created_at=created_at,
            updated_at=updated_at,
            split_method=data.get('split_method', 'equal'),
            payer_id=data.get('payer_id', ''),
            trip_id=data.get('trip_id', ''),
            participants=participants,
            shares=shares,
            items=items
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Expense instance to dictionary for Supabase storage"""
        return {
            'id': self.id,
            'description': self.description,
            'amount': self.amount,
            'currency': self.currency,
            'category': self.category,
            'date': self.date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'split_method': self.split_method,
            'payer_id': self.payer_id,
            'trip_id': self.trip_id,
            'participants': json.dumps(self.participants) if self.participants else '[]',
            'shares': json.dumps(self.shares) if self.shares else '{}',
            'items': json.dumps(self.items) if self.items else '[]'
        }
    
    def __repr__(self):
        return f'<Expense {self.description}: {self.currency} {self.amount}>'