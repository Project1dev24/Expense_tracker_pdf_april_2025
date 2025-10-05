#!/usr/bin/env python3
"""
Test script to verify the new Supabase project structure
"""

import os
import sys

def test_project_structure():
    """Test that the project structure is correct"""
    print("Testing Supabase project structure...")
    print("=" * 40)
    
    # Check required directories
    required_dirs = ['backend', 'backend/models', 'backend/routes', 'backend/templates']
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✓ {directory}")
        else:
            print(f"✗ {directory}")
            return False
    
    # Check required files
    required_files = [
        'README.md',
        'PROGRESS_TRACKER.md',
        'SUPABASE_PHASED_IMPLEMENTATION.md',
        'backend/app.py',
        'backend/supabase_client.py',
        'backend/supabase_schema.sql'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file}")
            return False
    
    print("\n✅ All required files and directories present!")
    return True

def test_imports():
    """Test that we can import the main modules"""
    print("\nTesting imports...")
    print("=" * 20)
    
    try:
        # Add backend to path
        sys.path.insert(0, 'backend')
        
        # Test importing main modules
        from supabase_client import supabase_client
        print("✓ supabase_client import successful")
        
        print("\n✅ All imports successful!")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def main():
    """Main test function"""
    print("Supabase Project Structure Test")
    print("=" * 30)
    
    if not test_project_structure():
        print("\n❌ Project structure test failed!")
        sys.exit(1)
    
    if not test_imports():
        print("\n❌ Import test failed!")
        sys.exit(1)
    
    print("\n🎉 All tests passed!")
    print("\nYour Supabase project is ready for development!")

if __name__ == "__main__":
    main()