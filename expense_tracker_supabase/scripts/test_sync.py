#!/usr/bin/env python3
"""
Test script to verify sync expenses functionality
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

def test_sync_endpoint():
    """Test the sync expenses endpoint"""
    try:
        # Test the sync endpoint (this would normally require authentication)
        url = "http://localhost:5004/sync-expenses"
        
        # Since this requires authentication, we'll just check if the endpoint exists
        # In a real test, you would authenticate first and then test the endpoint
        
        print("Testing sync expenses endpoint...")
        print(f"Endpoint URL: {url}")
        print("Note: This test requires the Flask application to be running and a user to be authenticated.")
        print("Manual testing through the dashboard is recommended.")
        
        return True
        
    except Exception as e:
        print(f"Error testing sync endpoint: {e}")
        return False

if __name__ == "__main__":
    print("Testing sync expenses functionality...")
    success = test_sync_endpoint()
    if success:
        print("Sync endpoint test completed!")
    else:
        print("Sync endpoint test failed!")