from datetime import datetime
from . import db

class UnregisteredParticipant(db.Model):
    __tablename__ = 'unregistered_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    linked_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    trip = db.relationship('Trip', backref=db.backref('unregistered_participants_list', lazy='dynamic'))
    linked_user = db.relationship('User', backref='linked_unregistered_participants', foreign_keys=[linked_user_id])
    
    def __repr__(self):
        return f'<UnregisteredParticipant {self.name}>'