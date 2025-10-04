#!/usr/bin/env python3
"""
Test database connection using Supabase CLI
"""

import os
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_db_connection():
    """Test database connection"""
    try:
        # Get Supabase credentials
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("Error: SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
            return False
        
        # Extract project ID from URL (everything between // and .)
        project_id = supabase_url.split('//')[1].split('.')[0]
        print(f"Project ID: {project_id}")
        
        # Try to connect using Supabase CLI
        print("Testing database connection...")
        result = subprocess.run([
            'supabase', 'db', 'reset', '--dry-run'
        ], cwd='/Users/srini/Desktop/projects/backup_everything/Expense_tracker_pdf_april_2025/expense_tracker_supabase', 
           capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Database connection successful!")
            print(result.stdout)
            return True
        else:
            print("Database connection failed:")
            print(result.stderr)
            return False
        
    except Exception as e:
        print(f"Error testing database connection: {e}")
        return False

if __name__ == "__main__":
    test_db_connection()