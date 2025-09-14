#!/usr/bin/env python3
"""
Migration script to add linked_unregistered_names column to the user table
"""

import sys
import os
import sqlite3

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def migrate_user_table():
    """Add linked_unregistered_names column to the user table"""
    # Connect directly to the SQLite database
    db_path = os.path.join(project_root, 'backend', 'app.db')
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if the column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'linked_unregistered_names' in columns:
            print("Column 'linked_unregistered_names' already exists in the user table")
            conn.close()
            return
        
        # For SQLite, we need to recreate the table with the new column
        print("SQLite database detected, recreating table with new column...")
        
        # 1. Create new table with the additional column
        cursor.execute('''
            CREATE TABLE user_new (
                id INTEGER NOT NULL PRIMARY KEY,
                email VARCHAR(120) NOT NULL,
                name VARCHAR(100) NOT NULL,
                password_hash VARCHAR(128),
                created_at DATETIME,
                last_seen DATETIME,
                is_admin BOOLEAN DEFAULT 0,
                linked_unregistered_names TEXT NOT NULL DEFAULT '[]'
            )
        ''')
        
        # 2. Copy data from old table to new table
        cursor.execute('''
            INSERT INTO user_new (id, email, name, password_hash, created_at, last_seen, is_admin, linked_unregistered_names)
            SELECT id, email, name, password_hash, created_at, last_seen, is_admin, '[]'
            FROM user
        ''')
        
        # 3. Drop old table
        cursor.execute('DROP TABLE user')
        
        # 4. Rename new table to original name
        cursor.execute('ALTER TABLE user_new RENAME TO user')
        
        # 5. Recreate indexes
        cursor.execute('CREATE UNIQUE INDEX ix_user_email ON user (email)')
        
        # Commit changes
        conn.commit()
        print("Successfully added 'linked_unregistered_names' column to user table")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_user_table()