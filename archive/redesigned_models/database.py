"""
Database initialization for redesigned models
"""

from flask_sqlalchemy import SQLAlchemy

# Create SQLAlchemy instance
db = SQLAlchemy()

def init_db(app):
    """Initialize the SQLAlchemy app"""
    db.init_app(app)
    return db

def create_tables(app):
    """Create all database tables"""
    with app.app_context():
        db.create_all()