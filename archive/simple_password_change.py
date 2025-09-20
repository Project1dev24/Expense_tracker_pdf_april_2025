#!/usr/bin/env python3
"""
Simple password change example for the Expense Tracker application.

This script demonstrates the proper way to change a user's password
with appropriate security checks, without using interactive input.
"""

import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'expense_tracker', 'backend')
sys.path.insert(0, backend_path)

from werkzeug.security import check_password_hash, generate_password_hash

# Simulated user database (in a real app, this would be an actual database)
users_db = {
    "user1": {
        "email": "user1@example.com",
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
    print("Simple Password Change Example")
    print("=" * 30)
    
    # Example user
    email = "user1@example.com"
    current_password = "current_password"
    new_password = "NewPass123"
    confirm_password = "NewPass123"
    
    print(f"User: {email}")
    print(f"Current password: {current_password}")
    print(f"New password: {new_password}")
    print(f"Confirm password: {confirm_password}")
    
    # Step 1: Verify current password
    print("\nStep 1: Verify current password")
    if verify_current_password(email, current_password):
        print("✓ Current password verified")
    else:
        print("✗ Current password incorrect")
        return
    
    # Step 2: Change the password
    print("\nStep 2: Change password")
    success, message = change_user_password(email, current_password, new_password, confirm_password)
    
    if success:
        print(f"✓ {message}")
    else:
        print(f"✗ {message}")
        return
    
    # Step 3: Verify the change worked
    print("\nStep 3: Verification")
    if verify_current_password(email, new_password):
        print("✓ New password verified successfully")
    else:
        print("✗ New password verification failed")
        
    # Step 4: Verify old password no longer works
    if not verify_current_password(email, current_password):
        print("✓ Old password correctly rejected")
    else:
        print("✗ Old password should have been rejected")

def test_error_cases():
    """
    Test various error cases in password changing.
    """
    print("\n\nError Case Testing")
    print("=" * 18)
    
    # Setup a test user
    test_email = "test@example.com"
    test_password = "TestPass123"
    users_db["test"] = {
        "email": test_email,
        "password_hash": generate_password_hash(test_password)
    }
    
    print(f"Test user: {test_email}")
    print(f"Test password: {test_password}")
    
    # Test case 1: Wrong current password
    print("\nTest 1: Wrong current password")
    success, message = change_user_password(test_email, "wrong_password", "NewPass456", "NewPass456")
    if not success:
        print(f"✓ Correctly rejected: {message}")
    else:
        print("✗ Should have been rejected")
    
    # Test case 2: Passwords don't match
    print("\nTest 2: New password and confirmation don't match")
    success, message = change_user_password(test_email, test_password, "NewPass456", "DifferentPass789")
    if not success:
        print(f"✓ Correctly rejected: {message}")
    else:
        print("✗ Should have been rejected")
    
    # Test case 3: Weak password
    print("\nTest 3: Weak password (too short)")
    success, message = change_user_password(test_email, test_password, "weak", "weak")
    if not success:
        print(f"✓ Correctly rejected: {message}")
    else:
        print("✗ Should have been rejected")
    
    # Test case 4: Weak password (no uppercase)
    print("\nTest 4: Weak password (no uppercase)")
    success, message = change_user_password(test_email, test_password, "weakpass123", "weakpass123")
    if not success:
        print(f"✓ Correctly rejected: {message}")
    else:
        print("✗ Should have been rejected")

if __name__ == "__main__":
    main()
    test_error_cases()