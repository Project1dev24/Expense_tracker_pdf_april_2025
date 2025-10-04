#!/usr/bin/env python3
"""
Script to fix trips data with invalid JSON
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def fix_trips_data():
    """Fix trips data with invalid JSON"""
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
        
        # Get all trips
        response = supabase.table('trips').select('*').execute()
        trips = response.data
        
        print(f"Found {len(trips)} trips to check")
        
        fixed_count = 0
        for trip in trips:
            trip_id = trip['id']
            participants = trip.get('participants', '[]')
            
            # Check if participants field is valid JSON
            try:
                if isinstance(participants, str):
                    json.loads(participants)
                # If it's already a list, convert to JSON string
                elif isinstance(participants, list):
                    supabase.table('trips').update({'participants': json.dumps(participants)}).eq('id', trip_id).execute()
                    fixed_count += 1
                    print(f"Fixed trip {trip_id}: converted list to JSON string")
            except json.JSONDecodeError:
                # Fix invalid JSON
                supabase.table('trips').update({'participants': '[]'}).eq('id', trip_id).execute()
                fixed_count += 1
                print(f"Fixed trip {trip_id}: reset invalid JSON to empty array")
        
        print(f"Fixed {fixed_count} trips with invalid JSON data")
        return True
        
    except Exception as e:
        print(f"Error fixing trips data: {e}")
        return False

if __name__ == "__main__":
    print("Fixing trips data with invalid JSON...")
    success = fix_trips_data()
    if success:
        print("Trips data fix completed successfully!")
    else:
        print("Trips data fix failed!")