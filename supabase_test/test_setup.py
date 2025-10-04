#!/usr/bin/env python3
"""
Test script to verify Supabase setup
"""

import os
from dotenv import load_dotenv

def test_environment():
    """Test environment setup"""
    print("Testing Environment Setup")
    print("=" * 30)
    
    # Load environment variables
    load_dotenv()
    
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if supabase_url and supabase_key:
        print("✓ Environment variables loaded")
        print(f"  SUPABASE_URL: {supabase_url[:30]}...")
        print(f"  SUPABASE_KEY: {supabase_key[:10]}...")
    else:
        print("✗ Missing environment variables")
        print("  Please create a .env file with SUPABASE_URL and SUPABASE_KEY")
        return False
    
    return True

def test_dependencies():
    """Test Python dependencies"""
    print("\nTesting Python Dependencies")
    print("=" * 30)
    
    try:
        from flask import Flask
        print("✓ Flask installed")
    except ImportError:
        print("✗ Flask not installed")
        return False
    
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv installed")
    except ImportError:
        print("✗ python-dotenv not installed")
        return False
    
    try:
        from supabase import create_client
        print("✓ Supabase client installed")
    except ImportError:
        print("✗ Supabase client not installed")
        return False
    
    return True

def main():
    """Main test function"""
    print("Supabase Test Setup Verification")
    print("=" * 40)
    
    env_ok = test_environment()
    deps_ok = test_dependencies()
    
    if env_ok and deps_ok:
        print("\n✓ All tests passed!")
        print("\nTo run the test application:")
        print("1. Create a .env file with your Supabase credentials")
        print("2. Run: pip install -r requirements.txt")
        print("3. Run: python app.py")
        print("4. Visit http://localhost:5005 in your browser")
        return 0
    else:
        print("\n✗ Some tests failed!")
        print("\nPlease fix the issues above and try again.")
        return 1

if __name__ == "__main__":
    exit(main())