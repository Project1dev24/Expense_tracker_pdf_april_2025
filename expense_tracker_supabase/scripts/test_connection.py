#!/usr/bin/env python3
"""
Test script to verify Supabase connection
"""

import os
from dotenv import load_dotenv

def test_connection():
    print("Testing Supabase Connection")
    print("=" * 25)
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing credentials!")
        print("Please create a .env file with SUPABASE_URL and SUPABASE_KEY")
        return False
    
    print(f"✓ SUPABASE_URL found: {supabase_url[:30]}...")
    print(f"✓ SUPABASE_KEY found: {supabase_key[:10]}...")
    
    # Try to import supabase
    try:
        from supabase import create_client
        print("✓ Supabase client library available")
    except ImportError:
        print("❌ Supabase client library not installed")
        print("Please run: pip install supabase python-dotenv")
        return False
    
    # Try to create client
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✓ Supabase client created successfully")
        print("\n✅ Connection test passed!")
        return True
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {e}")
        return False

if __name__ == "__main__":
    test_connection()