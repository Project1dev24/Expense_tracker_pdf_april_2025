#!/usr/bin/env python3
"""
Script to check database tables
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.app_factory import create_app
from backend.database import db

def check_tables():
    """Check what tables exist in the database"""
    app = create_app()
    
    with app.app_context():
        print("Tables in database:")
        # Try different methods to get table names
        try:
            # Method 1: engine.table_names() (deprecated in newer SQLAlchemy versions)
            tables = db.engine.table_names()
            print(tables)
        except AttributeError:
            # Method 2: metadata tables
            tables = [t.name for t in db.metadata.sorted_tables]
            print(tables)
        except Exception as e:
            print(f"Error getting tables: {e}")

if __name__ == "__main__":
    check_tables()