#!/usr/bin/env python3
"""
User model for Supabase integration
Note: In Supabase, user authentication is handled by Supabase Auth,
so this model represents application-specific user data rather than
authentication data.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class User:
    """User model for application-specific data"""
    id: str  # Supabase Auth user ID (UUID)
    email: str
    name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    
    @classmethod
    def from_supabase_auth_user(cls, auth_user: Any) -> 'User':
        """Create a User instance from Supabase Auth user data"""
        return cls(
            id=auth_user.id,
            email=auth_user.email,
            created_at=getattr(auth_user, 'created_at', None),
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a User instance from dictionary data"""
        return cls(
            id=data['id'],
            email=data['email'],
            name=data.get('name'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            last_seen=data.get('last_seen'),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert User instance to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
        }
    
    def update_last_seen(self):
        """Update the last seen timestamp"""
        self.last_seen = datetime.utcnow()