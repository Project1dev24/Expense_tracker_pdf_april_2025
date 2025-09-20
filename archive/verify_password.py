#!/usr/bin/env python3
"""
Password verification script for the Expense Tracker application.

This script demonstrates how to verify a password against its hash.
Note that passwords are HASHED, not encrypted, so they cannot be "decrypted".
Instead, we hash the input password and compare it with the stored hash.
"""

import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'expense_tracker', 'backend')
sys.path.insert(0, backend_path)

from werkzeug.security import check_password_hash, generate_password_hash

def verify_password(stored_hash, password):
    """
    Verify a password against its hash.
    
    Args:
        stored_hash (str): The stored password hash
        password (str): The password to verify
        
    Returns:
        bool: True if password matches the hash, False otherwise
    """
    return check_password_hash(stored_hash, password)

def hash_password(password):
    """
    Hash a password using the same method as the application.
    
    Args:
        password (str): The password to hash
        
    Returns:
        str: The hashed password
    """
    return generate_password_hash(password)

def main():
    print("Expense Tracker Password Verification Tool")
    print("=" * 40)
    
    # Example usage
    print("\n1. Hash a new password:")
    password = input("Enter a password to hash: ")
    hashed = hash_password(password)
    print(f"Hashed password: {hashed}")
    
    print("\n2. Verify a password against a hash:")
    stored_hash = input("Enter the stored hash: ")
    password_to_check = input("Enter the password to verify: ")
    
    if verify_password(stored_hash, password_to_check):
        print("✓ Password is correct!")
    else:
        print("✗ Password is incorrect!")
    
    print("\n3. Demonstration with example:")
    # Create an example hash
    example_password = "my_secret_password"
    example_hash = hash_password(example_password)
    print(f"Example password: {example_password}")
    print(f"Example hash: {example_hash}")
    
    # Verify correct password
    if verify_password(example_hash, example_password):
        print("✓ Example verification successful!")
    else:
        print("✗ Example verification failed!")
    
    # Verify incorrect password
    if verify_password(example_hash, "wrong_password"):
        print("✗ This should not happen!")
    else:
        print("✓ Incorrect password correctly rejected!")

if __name__ == "__main__":
    main()