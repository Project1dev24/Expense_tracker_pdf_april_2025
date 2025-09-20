#!/usr/bin/env python3
"""
Script to create the database tables with the latest schema.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.app_factory import create_app
from backend.database import db

def create_database_tables():
    """Create all database tables with the latest schema."""
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

if __name__ == "__main__":
    create_database_tables()