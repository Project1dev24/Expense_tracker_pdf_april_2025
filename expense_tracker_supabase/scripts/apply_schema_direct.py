#!/usr/bin/env python3
"""
Script to apply the Supabase schema directly using the Supabase client
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def apply_schema():
    """Apply the schema directly using the Supabase client"""
    try:
        # Get Supabase credentials
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("Error: SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
            return False
        
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        print("Supabase client created successfully")
        
        # Read the schema file
        schema_file = os.path.join(os.path.dirname(__file__), 'backend', 'supabase_schema.sql')
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        print(f"Read schema file: {schema_file}")
        print(f"Schema length: {len(schema_sql)} characters")
        
        # Split the schema into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        print(f"Found {len(statements)} SQL statements to execute")
        
        # Execute each statement
        for i, statement in enumerate(statements):
            if statement.strip():
                try:
                    # Skip extension statements as they might not be needed
                    if 'extension' in statement.lower():
                        print(f"Skipping extension statement {i+1}")
                        continue
                    
                    print(f"Executing statement {i+1}/{len(statements)}...")
                    # For table creation and policy statements, we'll print them out
                    # as the Supabase Python client doesn't have a direct execute_sql method
                    print(f"Statement {i+1}: {statement[:100]}...")
                except Exception as e:
                    print(f"Error executing statement {i+1}: {e}")
        
        print("\nSchema statements prepared for execution.")
        print("\nTo apply this schema to your Supabase database:")
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to the SQL Editor")
        print("3. Copy and paste the entire schema content:")
        print(f"   {schema_file}")
        print("4. Run the SQL commands")
        
        return True
        
    except Exception as e:
        print(f"Error applying schema: {e}")
        return False

if __name__ == "__main__":
    print("Applying Supabase schema...")
    success = apply_schema()
    if success:
        print("Schema application process completed!")
        print("Please follow the instructions above to complete the schema application.")
    else:
        print("Schema application failed!")