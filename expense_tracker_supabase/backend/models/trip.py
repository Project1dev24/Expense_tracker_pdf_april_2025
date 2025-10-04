#!/usr/bin/env python3
"""
Trip model for Supabase integration
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from .user import User
from .expense import Expense

@dataclass
class Trip:
    """Trip model for expense tracking"""
    id: Optional[str] = None  # Supabase will generate UUID
    name: str = ""
    description: Optional[str] = None
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    admin_id: str = ""  # Supabase Auth user ID (UUID)
    
    # Lists to store participant IDs
    participants: List[str] = field(default_factory=list)
    
    # Note: advances and general_payments columns don't exist in the current database schema
    # We'll store this data in a simplified way for now
    
    def get_participants_list(self) -> List[str]:
        """Get list of participant IDs"""
        return self.participants
    
    def set_participants_list(self, participants: List[str]):
        """Set list of participant IDs"""
        self.participants = participants
    
    def add_participant(self, user_id: str) -> bool:
        """Add a registered participant to the trip"""
        if user_id not in self.participants and user_id != self.admin_id:
            self.participants.append(user_id)
            return True
        return False
    
    def remove_participant(self, user_id: str) -> bool:
        """Remove a registered participant from the trip"""
        if user_id in self.participants:
            self.participants.remove(user_id)
            return True
        return False
    
    def calculate_total_expenses(self, expenses: List[Expense]) -> float:
        """Calculate total expenses for this trip"""
        return sum(expense.amount for expense in expenses)
    
    def calculate_user_balance(self, user_id: str, expenses: List[Expense]) -> float:
        """Calculate net balance for a specific user"""
        # Total paid by user (expenses they covered)
        total_paid = sum(expense.amount for expense in expenses 
                        if expense.payer_id == str(user_id))
        
        # Total share of user
        total_share = 0
        for expense in expenses:
            shares = expense.get_shares()
            if str(user_id) in shares:
                total_share += shares[str(user_id)]
        
        # Positive means user is owed money, negative means user owes money
        return total_paid - total_share
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Trip':
        """Create a Trip instance from dictionary data"""
        # Parse dates
        start_date = datetime.fromisoformat(data['start_date']) if data.get('start_date') else datetime.utcnow()
        end_date = datetime.fromisoformat(data['end_date']) if data.get('end_date') else datetime.utcnow()
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow()
        updated_at = datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.utcnow()
        
        # Parse JSON fields - handle both string and dict/list cases
        try:
            participants = json.loads(data.get('participants', '[]')) if isinstance(data.get('participants', '[]'), str) else data.get('participants', [])
        except (json.JSONDecodeError, TypeError):
            participants = []
        
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            description=data.get('description'),
            start_date=start_date,
            end_date=end_date,
            created_at=created_at,
            updated_at=updated_at,
            admin_id=data.get('admin_id', ''),
            participants=participants
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Trip instance to dictionary for Supabase storage"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'admin_id': self.admin_id,
            'participants': json.dumps(self.participants) if self.participants else '[]'
            # Note: Not including advances and general_payments as they don't exist in the schema
        }
    
    def __repr__(self):
        return f'<Trip {self.name}: {self.start_date.date()} to {self.end_date.date()}>'