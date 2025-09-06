import sqlite3
import os
from pathlib import Path

# Find the database file
instance_dir = Path('instance')
if instance_dir.exists():
    db_files = list(instance_dir.glob('*.db'))
    if db_files:
        db_path = db_files[0]
        print(f"Found database: {db_path}")
    else:
        print("No database files found in instance directory")
        exit(1)
else:
    print("Instance directory not found")
    exit(1)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current schema
cursor.execute("PRAGMA table_info(expense)")
columns = cursor.fetchall()
print("Current expense table schema:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# Check if payer_id is already TEXT
payer_id_type = None
for col in columns:
    if col[1] == 'payer_id':
        payer_id_type = col[2]
        break

if payer_id_type == 'TEXT':
    print("payer_id is already TEXT, no migration needed")
    conn.close()
    exit(0)

# Begin transaction
cursor.execute("BEGIN TRANSACTION")

try:
    # Create new table with correct schema
    cursor.execute("""
        CREATE TABLE expense_new (
            id INTEGER PRIMARY KEY,
            description VARCHAR(200) NOT NULL,
            amount FLOAT NOT NULL,
            currency VARCHAR(3),
            date DATETIME,
            created_at DATETIME,
            updated_at DATETIME,
            split_method VARCHAR(20),
            payer_id TEXT NOT NULL,
            trip_id INTEGER NOT NULL,
            participants TEXT NOT NULL,
            shares TEXT NOT NULL,
            items TEXT,
            category TEXT
        )
    """)
    
    # Copy data from old table to new table
    cursor.execute("""
        INSERT INTO expense_new 
        SELECT id, description, amount, currency, date, created_at, updated_at, 
               split_method, CAST(payer_id AS TEXT), trip_id, participants, shares, items, category
        FROM expense
    """)
    
    # Drop old table
    cursor.execute("DROP TABLE expense")
    
    # Rename new table to original name
    cursor.execute("ALTER TABLE expense_new RENAME TO expense")
    
    # Commit transaction
    conn.commit()
    
    print("Successfully migrated payer_id column from INTEGER to TEXT")
    
except Exception as e:
    # Rollback on error
    conn.rollback()
    print(f"Error during migration: {e}")
    
finally:
    # Close connection
    conn.close()