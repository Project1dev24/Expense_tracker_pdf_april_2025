#!/usr/bin/env python3
"""
Test script to verify trip schema functionality
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Get Supabase credentials
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')

if not supabase_url or not supabase_key:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    exit(1)

# Create Supabase client
supabase = create_client(supabase_url, supabase_key)

def test_trip_creation():
    """Test creating a trip"""
    try:
        # Sample trip data
        trip_data = {
            "name": "Test Trip",
            "description": "A test trip for schema validation",
            "start_date": "2025-10-05T00:00:00Z",
            "end_date": "2025-10-10T00:00:00Z",
            "admin_id": "00000000-0000-0000-0000-000000000000",  # Placeholder UUID
            "participants": ["00000000-0000-0000-0000-000000000000"]
        }
        
        # Try to insert trip
        response = supabase.table('trips').insert(trip_data).execute()
        print("Trip creation test: SUCCESS")
        print(f"Created trip ID: {response.data[0]['id']}")
        
        # Clean up - delete the test trip
        supabase.table('trips').delete().eq('id', response.data[0]['id']).execute()
        print("Cleaned up test trip")
        
    except Exception as e:
        print(f"Trip creation test: FAILED - {e}")

def test_trip_query():
    """Test querying trips"""
    try:
        # Try to query trips
        response = supabase.table('trips').select('*').limit(1).execute()
        print("Trip query test: SUCCESS")
        print(f"Query returned {len(response.data)} trips")
        
    except Exception as e:
        print(f"Trip query test: FAILED - {e}")

if __name__ == "__main__":
    print("Testing trip schema functionality...")
    test_trip_query()
    test_trip_creation()
    print("Test completed.")