#!/usr/bin/env python3
"""
Script to help apply the schema manually through the Supabase SQL Editor
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_manual_instructions():
    """Generate manual instructions for applying the schema"""
    try:
        # Read the schema files
        migrations_dir = "/Users/srini/Desktop/projects/backup_everything/Expense_tracker_pdf_april_2025/expense_tracker_supabase/supabase/migrations"
        migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
        
        print("=== Manual Schema Application Instructions ===\n")
        print("To fix the 'supabase_key is required' and RLS policy errors,")
        print("you need to apply the complete schema to your Supabase database manually.\n")
        
        print("Follow these steps:")
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to the SQL Editor")
        print("3. Copy and paste the following SQL statements in order:\n")
        
        for i, migration_file in enumerate(migration_files, 1):
            file_path = os.path.join(migrations_dir, migration_file)
            with open(file_path, 'r') as f:
                content = f.read()
            
            print(f"--- {i}. {migration_file} ---")
            print(content)
            print("\n" + "="*50 + "\n")
        
        print("4. Run each SQL statement in the Supabase SQL Editor")
        print("\nThis will create all the necessary tables (profiles, trips, expenses, unregistered_participants)")
        print("with their proper columns and Row Level Security (RLS) policies.")
        
        return True
        
    except Exception as e:
        print(f"Error generating manual instructions: {e}")
        return False

if __name__ == "__main__":
    generate_manual_instructions()