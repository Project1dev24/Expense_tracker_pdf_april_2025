from datetime import datetime
from . import db

class AdvancePayment(db.Model):
    __tablename__ = 'advance_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    participant_id = db.Column(db.String(100), nullable=False)  # Can be user ID or 'unregistered_name'
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdvancePayment trip:{self.trip_id} participant:{self.participant_id} amount:{self.amount}>'


class GeneralPayment(db.Model):
    __tablename__ = 'general_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    participant_id = db.Column(db.String(100), nullable=False)  # Can be user ID or 'unregistered_name'
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    expense_id = db.Column(db.Integer, db.ForeignKey('expenses.id'), nullable=True)  # Links to the expense this payment is for
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to expense (if linked)
    expense = db.relationship('Expense', backref='general_payments', foreign_keys=[expense_id])
    
    def __repr__(self):
        return f'<GeneralPayment trip:{self.trip_id} participant:{self.participant_id} amount:{self.amount}>'