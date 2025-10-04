#!/usr/bin/env python3
"""
Helper script to set up Supabase credentials
"""

def main():
    print("Supabase Credentials Setup")
    print("=" * 25)
    print("\nPlease follow these steps to get your Supabase credentials:")
    print("\n1. Go to your Supabase project dashboard")
    print("2. In the left sidebar, click the gear icon (Project Settings)")
    print("3. Click on 'API' in the settings menu")
    print("4. Copy the following information:")
    print("   - Project URL (starts with https://)")
    print("   - anon key (the long string under Project API keys)")
    print("\n5. Create a .env file in the backend directory with this content:")
    print("\n   SUPABASE_URL=your_project_url_here")
    print("   SUPABASE_KEY=your_anon_key_here")
    print("   SECRET_KEY=your_flask_secret_key_here")
    print("\nOnce you have your credentials, we can proceed to test the connection.")

if __name__ == "__main__":
    main()