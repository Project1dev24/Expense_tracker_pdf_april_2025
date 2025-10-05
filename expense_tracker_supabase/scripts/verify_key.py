#!/usr/bin/env python3
"""
Script to verify Supabase API key permissions
"""

import os
import base64
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def decode_jwt_payload(token):
    """Decode JWT payload to check the role"""
    try:
        # Split the token and get the payload part
        payload = token.split('.')[1]
        
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        # Decode the payload
        decoded = base64.b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"Error decoding JWT: {e}")
        return None

def verify_api_key():
    """Verify the Supabase API key"""
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_key:
        print("Error: SUPABASE_KEY not found in environment variables")
        return False
    
    print(f"Current SUPABASE_KEY: {supabase_key[:10]}...{supabase_key[-10:]}")
    
    # Decode the JWT to check the role
    payload = decode_jwt_payload(supabase_key)
    if payload:
        role = payload.get('role', 'unknown')
        print(f"API Key Role: {role}")
        
        if role == 'service_role':
            print("✅ Correct! Using service_role key - full permissions available")
            return True
        elif role == 'anon':
            print("⚠️  Warning: Using anon key - limited permissions")
            print("   Please update to service_role key for full functionality")
            return False
        else:
            print(f"❓ Unknown role: {role}")
            return False
    else:
        print("❌ Error: Could not decode API key")
        return False

if __name__ == "__main__":
    print("Verifying Supabase API Key...")
    verify_api_key()