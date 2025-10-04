#!/usr/bin/env python3
"""
Test script to verify table access
"""

import os
from dotenv import load_dotenv
from supabase import create_client

def test_tables():
    print("Testing Table Access")
    print("=" * 20)
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    # Create client
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        # Test profiles table
        result = supabase.table('profiles').select("*").limit(1).execute()
        print("✓ profiles table accessible")
    except Exception as e:
        print(f"⚠ profiles table: {e}")
    
    try:
        # Test trips table
        result = supabase.table('trips').select("*").limit(1).execute()
        print("✓ trips table accessible")
    except Exception as e:
        print(f"⚠ trips table: {e}")
    
    try:
        # Test expenses table
        result = supabase.table('expenses').select("*").limit(1).execute()
        print("✓ expenses table accessible")
    except Exception as e:
        print(f"⚠ expenses table: {e}")
    
    try:
        # Test unregistered_participants table
        result = supabase.table('unregistered_participants').select("*").limit(1).execute()
        print("✓ unregistered_participants table accessible")
    except Exception as e:
        print(f"⚠ unregistered_participants table: {e}")
    
    print("\n✅ Table access test completed!")

if __name__ == "__main__":
    test_tables()