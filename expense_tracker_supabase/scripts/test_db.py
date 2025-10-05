#!/usr/bin/env python3
"""
Test script to verify database connection and schema
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Create Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    exit(1)

supabase = create_client(supabase_url, supabase_key)

try:
    # Test inserting a trip with only the available columns
    print("Testing trip insertion with available columns...")
    trip_data = {
        'name': 'Test Trip',
        'description': 'A test trip with available columns only',
        'start_date': '2025-01-01T00:00:00',
        'end_date': '2025-01-05T00:00:00',
        'admin_id': 'd123e99b-1d9a-4e3a-9a56-63ed943892ba',  # Using a valid UUID format
        'participants': '[]'
    }
    
    print(f"Inserting trip data: {trip_data}")
    try:
        insert_response = supabase.table('trips').insert(trip_data).execute()
        print(f"Insert successful: {insert_response.data}")
    except Exception as e:
        print(f"Insert failed: {e}")
    
except Exception as e:
    print(f"Error: {e}")