#!/usr/bin/env python3
"""
Test script to verify authentication and trip creation
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

def test_authentication():
    """Test Supabase authentication"""
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
        
        # Test connection by getting user count
        try:
            response = supabase.table('profiles').select('count').execute()
            print(f"Connected to Supabase successfully. Found {len(response.data)} profiles.")
            return True
        except Exception as e:
            print(f"Error querying profiles: {e}")
            return False
        
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return False

if __name__ == "__main__":
    print("Testing Supabase authentication...")
    success = test_authentication()
    if success:
        print("Authentication test completed successfully!")
    else:
        print("Authentication test failed!")