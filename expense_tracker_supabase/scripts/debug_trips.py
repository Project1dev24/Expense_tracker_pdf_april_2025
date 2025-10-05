#!/usr/bin/env python3
"""
Script to debug trips data and identify JSON issues
"""

import os
import json
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

def debug_trips():
    """Debug trips data"""
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
        
        print(f"Found {len(trips)} trips")
        
        for i, trip in enumerate(trips):
            print(f"\n--- Trip {i+1} ---")
            print(f"ID: {trip['id']}")
            print(f"Name: {trip['name']}")
            print(f"Admin ID: {trip['admin_id']}")
            
            # Check participants field
            participants = trip.get('participants', '[]')
            print(f"Participants (raw): {participants}")
            print(f"Participants type: {type(participants)}")
            
            try:
                if isinstance(participants, str):
                    parsed = json.loads(participants)
                    print(f"Participants (parsed): {parsed}")
                else:
                    print(f"Participants (already parsed): {participants}")
            except json.JSONDecodeError as e:
                print(f"ERROR: Invalid JSON in participants: {e}")
                print(f"Problematic value: {repr(participants)}")
        
        return True
        
    except Exception as e:
        print(f"Error debugging trips: {e}")
        return False

if __name__ == "__main__":
    print("Debugging trips data...")
    debug_trips()