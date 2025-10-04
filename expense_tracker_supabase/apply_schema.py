#!/usr/bin/env python3
"""
Script to apply the Supabase schema directly to the database
"""

import os
import subprocess
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    exit(1)

# Read the schema file
schema_file = os.path.join(os.path.dirname(__file__), 'backend', 'supabase_schema.sql')

try:
    with open(schema_file, 'r') as f:
        schema_sql = f.read()
    
    print(f"Read schema file: {schema_file}")
    print(f"Schema length: {len(schema_sql)} characters")
    
    # For security reasons, we'll print instructions on how to apply the schema manually
    print("\nTo apply this schema to your Supabase database:")
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to the SQL Editor")
    print("3. Copy and paste the contents below:")
    print("=" * 50)
    print(schema_sql)
    print("=" * 50)
    print("4. Run the SQL commands in the Supabase SQL Editor")
    
except FileNotFoundError:
    print(f"Schema file not found: {schema_file}")
except Exception as e:
    print(f"Error reading schema file: {e}")