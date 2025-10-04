#!/usr/bin/env python3
"""
Setup script for Supabase integration
"""

import os
import sys

def setup_environment():
    """Setup the environment for Supabase integration"""
    print("Setting up Supabase integration environment...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('backend'):
        print("Error: Please run this script from the expense_tracker_supabase directory")
        return False
    
    # Check if .env file exists
    env_path = os.path.join('backend', '.env')
    if not os.path.exists(env_path):
        print("Creating .env file...")
        with open(env_path, 'w') as f:
            f.write("""FLASK_APP=app.py
FLASK_DEBUG=True
DATABASE_URL=sqlite:///app.db
PORT=5004

# Supabase Configuration
# TODO: Replace with your actual Supabase credentials
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_project_api_key_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
""")
        print("✓ Created .env file")
    else:
        print("✓ .env file already exists")
    
    # Check if requirements are installed
    try:
        import supabase
        import dotenv
        print("✓ Required Python packages already installed")
    except ImportError:
        print("Installing required Python packages...")
        os.system("pip install supabase python-dotenv")
    
    print("\nSetup complete!")
    print("\nNext steps:")
    print("1. Create a Supabase account at https://supabase.com/")
    print("2. Create a new project")
    print("3. Get your API credentials")
    print("4. Update the .env file with your Supabase credentials")
    print("5. Run the database schema in Supabase SQL Editor")
    
    return True

def main():
    """Main function"""
    if setup_environment():
        print("\n✅ Environment setup completed successfully!")
    else:
        print("\n❌ Environment setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()