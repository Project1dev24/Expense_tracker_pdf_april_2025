#!/usr/bin/env python3
"""
Test script to verify all routes are working
"""

import requests

def test_routes():
    """Test all routes"""
    base_url = "http://192.168.1.104:5005"
    
    routes = [
        "/",
        "/register",
        "/register/magic-link",
        "/login",
        "/login/magic-link",
        "/check-email?email=test@example.com"
    ]
    
    print("Testing Routes")
    print("=" * 30)
    
    for route in routes:
        try:
            url = base_url + route
            response = requests.get(url)
            if response.status_code == 200:
                print(f"✓ {route}")
            else:
                print(f"✗ {route} - Status: {response.status_code}")
        except Exception as e:
            print(f"✗ {route} - Error: {e}")
    
    print("\nAll routes tested!")
    print(f"Visit {base_url} in your browser to test the authentication flows.")

if __name__ == "__main__":
    test_routes()