#!/usr/bin/env python3
"""
Simple test script to verify the server is working correctly.
"""

import requests
import time

def test_server():
    """Test if the server is responding correctly."""
    try:
        # Wait a moment for the server to fully start
        time.sleep(2)
        
        # Test the main page
        response = requests.get('http://localhost:5003/', timeout=5)
        print(f"Server response status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Server is running and responding correctly!")
            print(f"Response content length: {len(response.text)} characters")
            return True
        else:
            print(f"✗ Server returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to server. Make sure it's running on port 5003.")
        return False
    except requests.exceptions.Timeout:
        print("✗ Request timed out. Server might be slow to respond.")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing server connectivity...")
    success = test_server()
    
    if success:
        print("\n🎉 Server test passed!")
        print("The expense tracker application is ready to use.")
        print("Visit http://localhost:5003 in your browser to access it.")
    else:
        print("\n❌ Server test failed!")
        print("Please check the server logs for more information.")