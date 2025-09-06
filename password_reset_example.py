#!/usr/bin/env python3
"""
Example of proper password reset mechanism for the Expense Tracker application.

This demonstrates the secure way to handle forgotten passwords.
"""

import sys
import os
import secrets

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'expense_tracker', 'backend')
sys.path.insert(0, backend_path)

from werkzeug.security import check_password_hash, generate_password_hash

# Simulated user database
users_db = {
    "user1": {
        "email": "user1@example.com",
        "password_hash": generate_password_hash("original_password"),
        "reset_token": None
    }
}

def generate_reset_token():
    """Generate a secure random token for password reset."""
    return secrets.token_urlsafe(32)

def request_password_reset(email):
    """
    Request a password reset for a user.
    
    In a real application, this would:
    1. Verify the email exists in the database
    2. Generate a secure reset token
    3. Store the token with an expiration time
    4. Send an email with a link containing the token
    """
    for username, user_data in users_db.items():
        if user_data["email"] == email:
            token = generate_reset_token()
            user_data["reset_token"] = token
            print(f"Password reset token generated for {email}")
            print(f"Token: {token}")
            print("In a real app, this token would be sent via email.")
            return token
    print(f"No user found with email: {email}")
    return None

def reset_password_with_token(token, new_password):
    """
    Reset a user's password using a valid reset token.
    
    In a real application, this would:
    1. Verify the token exists and hasn't expired
    2. Hash the new password
    3. Update the user's password hash in the database
    4. Invalidate the reset token
    """
    for username, user_data in users_db.items():
        if user_data["reset_token"] == token:
            user_data["password_hash"] = generate_password_hash(new_password)
            user_data["reset_token"] = None
            print(f"Password successfully reset for {user_data['email']}")
            return True
    print("Invalid or expired reset token")
    return False

def verify_user_password(email, password):
    """
    Verify a user's password (normal login process).
    """
    for username, user_data in users_db.items():
        if user_data["email"] == email:
            return check_password_hash(user_data["password_hash"], password)
    return False

def main():
    print("Expense Tracker Password Reset Example")
    print("=" * 40)
    
    # Example user
    email = "user1@example.com"
    original_password = "original_password"
    
    print(f"Example user: {email}")
    print(f"Original password: {original_password}")
    print(f"Stored hash: {users_db['user1']['password_hash']}")
    
    # Demonstrate normal login verification
    print("\n1. Normal password verification:")
    if verify_user_password(email, original_password):
        print("✓ Login successful with correct password")
    else:
        print("✗ Login failed")
    
    if not verify_user_password(email, "wrong_password"):
        print("✓ Login correctly rejected with wrong password")
    else:
        print("✗ This should not happen")
    
    print("\n2. Password reset process:")
    # Request password reset
    token = request_password_reset(email)
    
    if token:
        # Reset password with token
        new_password = "new_secure_password"
        print(f"Setting new password: {new_password}")
        if reset_password_with_token(token, new_password):
            print("✓ Password reset successful")
            
            # Verify new password works
            if verify_user_password(email, new_password):
                print("✓ New password verified successfully")
            else:
                print("✗ New password verification failed")
                
            # Verify old password no longer works
            if not verify_user_password(email, original_password):
                print("✓ Old password correctly rejected")
            else:
                print("✗ Old password should have been rejected")

if __name__ == "__main__":
    main()