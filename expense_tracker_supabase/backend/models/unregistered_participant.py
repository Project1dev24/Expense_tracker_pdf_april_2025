#!/usr/bin/env python3
"""
UnregisteredParticipant model for Supabase integration
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class UnregisteredParticipant:
    """Unregistered participant model for trips"""
    id: Optional[str] = None  # Supabase will generate UUID
    name: str = ""
    trip_id: str = ""
    linked_user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'UnregisteredParticipant':
        """Create an UnregisteredParticipant instance from dictionary data"""
        created_at = datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.utcnow()
        
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            trip_id=data.get('trip_id', ''),
            linked_user_id=data.get('linked_user_id'),
            created_at=created_at
        )
    
    def to_dict(self) -> dict:
        """Convert UnregisteredParticipant instance to dictionary for Supabase storage"""
        return {
            'id': self.id,
            'name': self.name,
            'trip_id': self.trip_id,
            'linked_user_id': self.linked_user_id,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<UnregisteredParticipant {self.name}>'