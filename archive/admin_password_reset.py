#!/usr/bin/env python3
"""
Administrator password reset tool for the Expense Tracker application.

This script demonstrates how an administrator can reset a user's password
by generating a new one and updating the hash in the database.
"""

import sys
import os
import secrets
import string

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'expense_tracker', 'backend')
sys.path.insert(0, backend_path)

from werkzeug.security import generate_password_hash

def generate_secure_password(length=12):
    """
    Generate a secure random password.
    
    Args:
        length (int): Length of the password to generate
        
    Returns:
        str: Generated secure password
    """
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special_chars = "!@#$%^&*"
    
    # Ensure at least one character from each set
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special_chars)
    ]
    
    # Fill the rest randomly
    all_chars = lowercase + uppercase + digits + special_chars
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Shuffle the password list
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)

def update_user_password_hash(user_id, new_password):
    """
    Update a user's password hash in the database.
    
    In a real application, this would:
    1. Connect to the database
    2. Hash the new password
    3. Update the user record
    4. Commit the changes
    
    Args:
        user_id (int): The user's ID
        new_password (str): The new password to set
        
    Returns:
        str: The new password hash
    """
    # Hash the new password
    new_hash = generate_password_hash(new_password)
    
    # In a real application, you would execute a database update here:
    # UPDATE user SET password_hash = ? WHERE id = ?
    
    print(f"Generated new password for user {user_id}: {new_password}")
    print(f"New password hash: {new_hash}")
    print("In a real application, this hash would be stored in the database.")
    
    return new_hash

def main():
    print("Administrator Password Reset Tool")
    print("=" * 35)
    
    # Example usage
    user_id = 1  # Example user ID
    
    print(f"Resetting password for user ID: {user_id}")
    
    # Generate a secure new password
    new_password = generate_secure_password(16)
    
    # Update the user's password hash
    new_hash = update_user_password_hash(user_id, new_password)
    
    print("\nPassword reset complete!")
    print("Provide the new password to the user through a secure channel.")
    print("The user should change it immediately after first login.")
    
    # Demonstrate that we can verify the password
    from werkzeug.security import check_password_hash
    if check_password_hash(new_hash, new_password):
        print("✓ Password verification test passed")
    else:
        print("✗ Password verification test failed")

if __name__ == "__main__":
    main()