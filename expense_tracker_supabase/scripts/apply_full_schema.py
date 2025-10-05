#!/usr/bin/env python3
"""
Script to display instructions for applying the full schema to Supabase
"""

import os

def main():
    print("=== Supabase Schema Application Instructions ===\n")
    
    # Read the schema file
    schema_file = os.path.join(os.path.dirname(__file__), 'backend', 'supabase_schema.sql')
    
    try:
        with open(schema_file, 'r') as f:
            schema_content = f.read()
        
        print("To fix the 'supabase_key is required' and RLS policy errors,")
        print("you need to apply the complete schema to your Supabase database.\n")
        
        print("Follow these steps:")
        print("1. Go to your Supabase project dashboard")
        print("2. Navigate to the SQL Editor")
        print("3. Copy and paste the following schema:")
        print("=" * 50)
        print(schema_content)
        print("=" * 50)
        print("4. Run the SQL commands in the Supabase SQL Editor")
        print("\nThis will create all the necessary tables (profiles, trips, expenses, unregistered_participants)")
        print("with their proper columns and Row Level Security (RLS) policies.")
        
    except FileNotFoundError:
        print(f"Schema file not found: {schema_file}")
        print("Please make sure the supabase_schema.sql file exists in the backend directory.")

if __name__ == "__main__":
    main()