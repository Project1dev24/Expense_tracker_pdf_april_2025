#!/usr/bin/env python3
"""
Script to help update the .env file with the correct Supabase service role key
"""

def update_env_instructions():
    """Print instructions for updating the .env file"""
    print("=== Supabase API Key Update Instructions ===\n")
    
    print("The current error 'Invalid API key' indicates you're using an anon key.")
    print("For server-side operations, you need a service_role key.\n")
    
    print("Please follow these steps:")
    print("1. Go to your Supabase project dashboard")
    print("2. Navigate to Project Settings > API")
    print("3. Find the 'service_role' key (click to reveal it)")
    print("4. Copy the service_role key")
    print("5. Update your .env file:")
    print("   - Open /Users/srini/Desktop/projects/backup_everything/Expense_tracker_pdf_april_2025/expense_tracker_supabase/.env")
    print("   - Replace the SUPABASE_KEY value with the service_role key")
    print("   - Save the file")
    print("\nExample .env update:")
    print("# Supabase Configuration")
    print("SUPABASE_URL=https://rmaynigdfqdxcjayvfpg.supabase.co")
    print("SUPABASE_KEY=YOUR_SERVICE_ROLE_KEY_HERE")
    print("\nAfter updating the .env file, restart your Flask application.")

if __name__ == "__main__":
    update_env_instructions()