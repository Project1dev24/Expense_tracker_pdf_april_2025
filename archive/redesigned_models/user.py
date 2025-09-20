from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationships
    trips_created = db.relationship('Trip', backref='admin', lazy='dynamic', foreign_keys='Trip.admin_id')
    trip_participations = db.relationship('TripParticipant', backref='user', lazy='dynamic')
    linked_unregistered_names = db.relationship('UserLinkedName', backref='user', lazy='dynamic')
    unregistered_participants = db.relationship('UnregisteredParticipant', backref='linked_user', lazy='dynamic')
    
    def set_password(self, password):
        """Set the password for the user"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the user's password"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_seen(self):
        """Update the last seen timestamp for the user"""
        self.last_seen = datetime.utcnow()
        db.session.commit()
    
    def get_trips(self):
        """Get all trips where user is a participant or admin"""
        from .trip import Trip
        # Get trips where user is admin
        admin_trips = Trip.query.filter_by(admin_id=self.id).all()
        # Get trips where user is a participant
        participant_trips = [tp.trip for tp in self.trip_participations]
        # Combine and remove duplicates
        all_trips = list(set(admin_trips + participant_trips))
        return all_trips
    
    def get_total_balance(self):
        """Calculate total balance across all trips"""
        trips = self.get_trips()
        total_balance = 0
        for trip in trips:
            total_balance += trip.calculate_user_balance(self.id)
        return total_balance
    
    def get_linked_unregistered_names(self):
        """Get list of unregistered participant names linked to this user"""
        return [link.unregistered_name for link in self.linked_unregistered_names]
    
    def add_linked_unregistered_name(self, name):
        """Add an unregistered participant name to this user's linked list"""
        # Check if already linked
        existing = UserLinkedName.query.filter_by(
            user_id=self.id, 
            unregistered_name=name
        ).first()
        
        if not existing:
            link = UserLinkedName(
                user_id=self.id,
                unregistered_name=name
            )
            db.session.add(link)
            return True
        return False
    
    def remove_linked_unregistered_name(self, name):
        """Remove an unregistered participant name from this user's linked list"""
        link = UserLinkedName.query.filter_by(
            user_id=self.id,
            unregistered_name=name
        ).first()
        
        if link:
            db.session.delete(link)
            return True
        return False

    def __repr__(self):
        return f'<User {self.name}>'


class UserLinkedName(db.Model):
    __tablename__ = 'user_linked_names'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    unregistered_name = db.Column(db.String(100), nullable=False)
    linked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure a user can't link the same unregistered name multiple times
    __table_args__ = (db.UniqueConstraint('user_id', 'unregistered_name', name='unique_user_unregistered_name'),)
    
    def __repr__(self):
        return f'<UserLinkedName {self.user_id}:{self.unregistered_name}>'