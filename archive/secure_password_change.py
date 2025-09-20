#!/usr/bin/env python3
"""
Secure password change tool for the Expense Tracker application.

This script demonstrates the proper way to change a user's password
with appropriate security checks.
"""

import sys
import os
import getpass

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'expense_tracker', 'backend')
sys.path.insert(0, backend_path)

from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

# Simulated user database (in a real app, this would be an actual database)
users_db = {
    "user1": {
        "email": "example@test.com",
        "password_hash": generate_password_hash("current_password")
    }
}

def verify_current_password(email, current_password):
    """
    Verify the user's current password.
    
    Args:
        email (str): User's email address
        current_password (str): Current password to verify
        
    Returns:
        bool: True if password is correct, False otherwise
    """
    for username, user_data in users_db.items():
        if user_data["email"] == email:
            return check_password_hash(user_data["password_hash"], current_password)
    return False

def validate_new_password(new_password):
    """
    Validate that the new password meets security requirements.
    
    Args:
        new_password (str): Password to validate
        
    Returns:
        tuple: (is_valid, message) where is_valid is bool and message is str
    """
    if len(new_password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in new_password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in new_password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in new_password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"

def change_user_password(email, current_password, new_password, confirm_password):
    """
    Change a user's password after proper verification.
    
    Args:
        email (str): User's email address
        current_password (str): Current password for verification
        new_password (str): New password to set
        confirm_password (str): Confirmation of new password
        
    Returns:
        tuple: (success, message) where success is bool and message is str
    """
    # Step 1: Verify the user's current password
    if not verify_current_password(email, current_password):
        return False, "Current password is incorrect"
    
    # Step 2: Verify that new password and confirmation match
    if new_password != confirm_password:
        return False, "New password and confirmation do not match"
    
    # Step 3: Validate the new password
    is_valid, message = validate_new_password(new_password)
    if not is_valid:
        return False, message
    
    # Step 4: Update the password in the database
    for username, user_data in users_db.items():
        if user_data["email"] == email:
            user_data["password_hash"] = generate_password_hash(new_password)
            return True, "Password changed successfully"
    
    return False, "User not found"

def main():
    print("Secure Password Change Tool")
    print("=" * 25)
    
    # In a real application, you would get the logged-in user's email
    # For this example, we'll use a predefined email
    email = "example@test.com"
    print(f"Changing password for: {email}")
    
    # Step 1: Verify current password
    print("\nStep 1: Verify current password")
    current_password = getpass.getpass("Enter current password: ")
    
    # Step 2: Get new password
    print("\nStep 2: Set new password")
    print("Password requirements:")
    print("- At least 8 characters long")
    print("- Contains uppercase and lowercase letters")
    print("- Contains at least one digit")
    
    new_password = getpass.getpass("Enter new password: ")
    confirm_password = getpass.getpass("Confirm new password: ")
    
    # Step 3: Change the password
    success, message = change_user_password(email, current_password, new_password, confirm_password)
    
    if success:
        print(f"\n✓ {message}")
        print("Your password has been updated successfully.")
    else:
        print(f"\n✗ {message}")
        print("Password change failed. Please try again.")
    
    # Demonstrate the change worked
    print("\nStep 4: Verification")
    if verify_current_password(email, new_password):
        print("✓ New password verified successfully")
    else:
        print("✗ New password verification failed")

def interactive_demo():
    """
    Interactive demo showing the complete password change process.
    """
    print("\nInteractive Password Change Demo")
    print("=" * 32)
    
    # Setup a test user
    test_email = "demo@example.com"
    test_password = "DemoPass123"
    users_db["demo"] = {
        "email": test_email,
        "password_hash": generate_password_hash(test_password)
    }
    
    print(f"Demo user created: {test_email}")
    print(f"Current password: {test_password}")
    
    # Simulate the password change process
    print("\n--- Password Change Process ---")
    
    # Get user input (simulated)
    print(f"User: {test_email}")
    current = test_password
    new = "NewSecurePass456"
    confirm = new
    
    print(f"Current password entered: {current}")
    print(f"New password entered: {new}")
    print(f"Confirm password entered: {confirm}")
    
    # Attempt to change password
    success, message = change_user_password(test_email, current, new, confirm)
    
    if success:
        print(f"\n✓ {message}")
        
        # Verify the change worked
        if verify_current_password(test_email, new):
            print("✓ New password verified successfully")
        else:
            print("✗ New password verification failed")
            
        # Verify old password no longer works
        if not verify_current_password(test_email, test_password):
            print("✓ Old password correctly rejected")
        else:
            print("✗ Old password should have been rejected")
    else:
        print(f"\n✗ {message}")

if __name__ == "__main__":
    main()
    interactive_demo()