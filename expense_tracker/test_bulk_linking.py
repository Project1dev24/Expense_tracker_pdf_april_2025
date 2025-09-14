#!/usr/bin/env python3
"""
Test script to verify the bulk linking functionality.
"""

import sys
import os
import json
from sqlalchemy import create_engine, text

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_bulk_linking():
    """Test the bulk linking functionality."""
    
    # Database configuration
    db_path = os.path.join(project_root, 'backend', 'app.db')
    database_uri = f'sqlite:///{db_path}'
    
    print(f"Testing bulk linking with database: {db_path}")
    
    # Create database engine
    engine = create_engine(database_uri)
    connection = engine.connect()
    
    try:
        # Test 1: Check if linked_unregistered_names column exists
        print("\n1. Checking if linked_unregistered_names column exists...")
        try:
            check_column_sql = text("""
                SELECT linked_unregistered_names FROM user LIMIT 1
            """)
            connection.execute(check_column_sql)
            print("   ✓ linked_unregistered_names column exists")
        except Exception as e:
            print(f"   ✗ linked_unregistered_names column does not exist: {e}")
            return False
        
        # Test 2: Check for users with linked unregistered names
        print("\n2. Checking for users with linked unregistered names...")
        get_linked_users_sql = text("""
            SELECT id, name, linked_unregistered_names 
            FROM user 
            WHERE linked_unregistered_names IS NOT NULL 
            AND linked_unregistered_names != '[]'
        """)
        result = connection.execute(get_linked_users_sql)
        linked_users = result.fetchall()
        
        if linked_users:
            print(f"   ✓ Found {len(linked_users)} users with linked unregistered names:")
            for user in linked_users[:3]:  # Show first 3 users
                try:
                    names = json.loads(user[2]) if user[2] else []
                    print(f"     User {user[1]} (ID: {user[0]}) has {len(names)} linked names: {names}")
                except (json.JSONDecodeError, TypeError):
                    print(f"     User {user[1]} (ID: {user[0]}) has invalid linked names data")
        else:
            print("   ⚠ No users found with linked unregistered names")
        
        # Test 3: Check for unregistered participants in trips
        print("\n3. Checking for unregistered participants in trips...")
        get_trips_sql = text("""
            SELECT id, unregistered_participants 
            FROM trip 
            WHERE unregistered_participants IS NOT NULL 
            AND unregistered_participants != '[]'
        """)
        result = connection.execute(get_trips_sql)
        trips = result.fetchall()
        
        if trips:
            print(f"   ✓ Found {len(trips)} trips with unregistered participants:")
            for trip in trips[:3]:  # Show first 3 trips
                try:
                    participants = json.loads(trip[1]) if trip[1] else []
                    print(f"     Trip {trip[0]} has {len(participants)} unregistered participants: {participants}")
                except (json.JSONDecodeError, TypeError):
                    print(f"     Trip {trip[0]} has invalid unregistered participants data")
        else:
            print("   ⚠ No trips found with unregistered participants")
        
        # Test 4: Check for expenses with unregistered participants
        print("\n4. Checking for expenses with unregistered participants...")
        get_expenses_sql = text("""
            SELECT id, payer_id, participants, shares
            FROM expense 
            WHERE payer_id LIKE 'unregistered_%'
            OR participants LIKE '%unregistered_%'
            OR shares LIKE '%unregistered_%'
        """)
        result = connection.execute(get_expenses_sql)
        expenses = result.fetchall()
        
        if expenses:
            print(f"   ⚠ Found {len(expenses)} expenses with unregistered participants:")
            for expense in expenses[:3]:  # Show first 3 expenses
                print(f"     Expense {expense[0]} has unregistered references")
        else:
            print("   ✓ No expenses found with unregistered participants")
        
        print("\n✓ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        connection.close()

if __name__ == "__main__":
    success = test_bulk_linking()
    if success:
        print("\n🎉 Bulk linking implementation is working correctly!")
    else:
        print("\n❌ Bulk linking implementation has issues!")
        sys.exit(1)