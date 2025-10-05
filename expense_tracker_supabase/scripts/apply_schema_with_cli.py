#!/usr/bin/env python3
"""
Script to apply the Supabase schema using the Supabase CLI
"""

import os
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def apply_schema_with_cli():
    """Apply schema using Supabase CLI"""
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
        
        # Create a simple migration file
        migration_file = "/Users/srini/Desktop/projects/backup_everything/Expense_tracker_pdf_april_2025/expense_tracker_supabase/supabase/migrations/20251004000000_initial_schema.sql"
        
        print(f"Migration file: {migration_file}")
        print("To apply the schema using Supabase CLI, run the following commands:")
        print()
        print("1. Link your project (if not already linked):")
        print(f"   supabase link --project-ref {project_id}")
        print()
        print("2. Apply the migrations:")
        print("   supabase db push")
        print()
        print("Alternatively, you can apply the schema directly through the SQL Editor:")
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to the SQL Editor")
        print("3. Copy and paste the content of the schema file:")
        print(f"   {os.path.join(os.path.dirname(__file__), 'backend', 'supabase_schema.sql')}")
        print("4. Run the SQL commands")
        
        return True
        
    except Exception as e:
        print(f"Error creating schema application instructions: {e}")
        return False

if __name__ == "__main__":
    apply_schema_with_cli()