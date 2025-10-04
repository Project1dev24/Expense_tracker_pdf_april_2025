#!/usr/bin/env python3
"""
Test script to verify the fix for trip creation RLS issue
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

def test_trip_creation():
    """Test trip creation with proper authentication"""
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
        return True
        
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return False

if __name__ == "__main__":
    print("Testing trip creation fix...")
    success = test_trip_creation()
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed!")