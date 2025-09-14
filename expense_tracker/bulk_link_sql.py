#!/usr/bin/env python3
"""
Direct SQL script to bulk link unregistered participants to registered users
based on matching names, and update all related tables.
This version works with the existing schema that stores unregistered participants 
in the trip table's unregistered_participants column.
"""

import sys
import os
import json
from sqlalchemy import create_engine, text

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def bulk_link_participants_sql(trip_id=None):
    """
    Execute the three-step SQL process to link unregistered participants to registered users:
    
    1. Find unregistered participants in trip.unregistered_participants and match with users by name
    2. Add a column to users table to track linked unregistered names (if not exists)
    3. Update expense table to change payer_id from 'unregistered_{name}' to user ID
    4. Update expense participants and shares to replace unregistered participants with linked users
    """
    
    # Database configuration - use the correct path as specified
    db_path = "/Users/srini/Desktop/projects/backup_everything/Expense_tracker_pdf_april_2025/expense_tracker/backend/app.db"
    database_uri = f'sqlite:///{db_path}'
    
    print(f"Using database: {db_path}")
    
    # Create database engine
    engine = create_engine(database_uri)
    connection = engine.connect()
    
    try:
        print("Starting bulk linking process...")
        
        # Start a transaction
        trans = connection.begin()
        
        # Check if linked_unregistered_names column exists, if not add it
        try:
            check_column_sql = text("""
                SELECT linked_unregistered_names FROM user LIMIT 1
            """)
            connection.execute(check_column_sql)
        except Exception as e:
            # Column doesn't exist, add it
            print("Adding linked_unregistered_names column to user table...")
            try:
                add_column_sql = text("""
                    ALTER TABLE user ADD COLUMN linked_unregistered_names TEXT DEFAULT '[]'
                """)
                connection.execute(add_column_sql)
                print("Successfully added linked_unregistered_names column")
            except Exception as add_error:
                print(f"Error adding column: {add_error}")
                # Continue anyway, we'll work without it
        
        # Step 1: Find unregistered participants and match with users by name
        # Get all trips and their unregistered participants
        if trip_id:
            get_trips_sql = text("""
                SELECT id, unregistered_participants
                FROM trip
                WHERE id = :trip_id
            """)
            trips_result = connection.execute(get_trips_sql, {'trip_id': trip_id})
        else:
            get_trips_sql = text("""
                SELECT id, unregistered_participants
                FROM trip
            """)
            trips_result = connection.execute(get_trips_sql)
        
        trips = trips_result.fetchall()
        
        linked_count = 0
        updated_users_count = 0
        linked_user_mapping = {}  # Store mapping of unregistered names to user IDs
        
        for trip_row in trips:
            current_trip_id = trip_row[0]
            unregistered_json = trip_row[1]
            
            try:
                unregistered_participants = json.loads(unregistered_json) if unregistered_json else []
            except (json.JSONDecodeError, TypeError):
                unregistered_participants = []
            
            print(f"Processing trip {current_trip_id} with {len(unregistered_participants)} unregistered participants")
            
            # For each unregistered participant, check if there's a matching user
            for unregistered_name in unregistered_participants:
                # Find a user with a matching name (case-insensitive)
                get_matching_user_sql = text("""
                    SELECT id, name
                    FROM user
                    WHERE LOWER(name) = LOWER(:unregistered_name)
                """)
                
                user_result = connection.execute(get_matching_user_sql, {'unregistered_name': unregistered_name})
                user_row = user_result.fetchone()
                
                if user_row:
                    user_id = user_row[0]
                    user_name = user_row[1]
                    
                    print(f"Found matching user {user_name} (ID: {user_id}) for unregistered participant '{unregistered_name}'")
                    
                    # Store the mapping for later use
                    linked_user_mapping[unregistered_name] = user_id
                    
                    # Step 2: Update users table to track linked unregistered names
                    try:
                        # Get current linked_unregistered_names for this user
                        get_current_names_sql = text("""
                            SELECT linked_unregistered_names 
                            FROM user 
                            WHERE id = :user_id
                        """)
                        
                        current_names_result = connection.execute(get_current_names_sql, {'user_id': user_id})
                        current_names_row = current_names_result.fetchone()
                        
                        if current_names_row:
                            try:
                                current_linked_names = json.loads(current_names_row[0]) if current_names_row[0] else []
                            except (json.JSONDecodeError, TypeError):
                                current_linked_names = []
                            
                            # Add the unregistered name if not already present
                            if unregistered_name not in current_linked_names:
                                current_linked_names.append(unregistered_name)
                                updated_names_json = json.dumps(current_linked_names)
                                
                                # Update the user's linked_unregistered_names
                                update_user_names_sql = text("""
                                    UPDATE user 
                                    SET linked_unregistered_names = :names_json
                                    WHERE id = :user_id
                                """)
                                
                                connection.execute(update_user_names_sql, {
                                    'names_json': updated_names_json,
                                    'user_id': user_id
                                })
                                updated_users_count += 1
                                print(f"Updated linked_unregistered_names for user {user_id} with '{unregistered_name}'")
                    except Exception as user_update_error:
                        print(f"Error updating user linked names: {user_update_error}")
                    
                    linked_count += 1
        
        # Step 3: Update all expenses to replace unregistered participants with linked users
        print(f"Updating expenses for {len(linked_user_mapping)} linked participants...")
        
        # Get all expenses that might need updating
        if trip_id:
            get_expenses_sql = text("""
                SELECT id, payer_id, participants, shares
                FROM expense 
                WHERE trip_id = :trip_id
            """)
            expenses_result = connection.execute(get_expenses_sql, {'trip_id': trip_id})
        else:
            get_expenses_sql = text("""
                SELECT id, payer_id, participants, shares
                FROM expense
            """)
            expenses_result = connection.execute(get_expenses_sql)
        
        expenses = expenses_result.fetchall()
        updated_expenses_count = 0
        
        for expense_row in expenses:
            expense_id = expense_row[0]
            payer_id = expense_row[1]
            participants_json = expense_row[2]
            shares_json = expense_row[3]
            
            updated = False
            
            try:
                participants = json.loads(participants_json) if participants_json else []
                shares = json.loads(shares_json) if shares_json else {}
            except (json.JSONDecodeError, TypeError):
                participants = []
                shares = {}
            
            # Update payer_id if it matches an unregistered participant
            for unregistered_name, user_id in linked_user_mapping.items():
                unregistered_id = f'unregistered_{unregistered_name}'
                if payer_id == unregistered_id:
                    # Update payer_id
                    update_payer_sql = text("""
                        UPDATE expense 
                        SET payer_id = :user_id
                        WHERE id = :expense_id
                    """)
                    connection.execute(update_payer_sql, {
                        'user_id': str(user_id),
                        'expense_id': expense_id
                    })
                    updated = True
                    print(f"Updated payer_id for expense {expense_id} from '{unregistered_id}' to '{user_id}'")
            
            # Check if any participants need to be updated
            updated_participants = False
            for i, participant_id in enumerate(participants):
                # Check if this participant is an unregistered participant that was linked
                for unregistered_name, user_id in linked_user_mapping.items():
                    unregistered_id = f'unregistered_{unregistered_name}'
                    if participant_id == unregistered_id:
                        # Update participant ID
                        participants[i] = str(user_id)
                        updated_participants = True
                        updated = True
                        print(f"Updated participant in expense {expense_id} from '{unregistered_id}' to '{user_id}'")
            
            # Check if any shares need to be updated
            updated_shares = False
            shares_to_update = list(shares.keys())
            for participant_id in shares_to_update:
                # Check if this share is for an unregistered participant that was linked
                for unregistered_name, user_id in linked_user_mapping.items():
                    unregistered_id = f'unregistered_{unregistered_name}'
                    if participant_id == unregistered_id:
                        # Move the share to the linked user
                        shares[str(user_id)] = shares.pop(participant_id)
                        updated_shares = True
                        updated = True
                        print(f"Updated share in expense {expense_id} from '{unregistered_id}' to '{user_id}'")
            
            # Update the expense if needed
            if updated_participants or updated_shares:
                update_expense_details_sql = text("""
                    UPDATE expense
                    SET participants = :participants_json,
                        shares = :shares_json
                    WHERE id = :expense_id
                """)
                
                connection.execute(update_expense_details_sql, {
                    'participants_json': json.dumps(participants),
                    'shares_json': json.dumps(shares),
                    'expense_id': expense_id
                })
                print(f"Updated participants/shares for expense {expense_id}")
            
            if updated:
                updated_expenses_count += 1
        
        # Commit all changes
        trans.commit()
        print(f"\nBulk linking completed successfully!")
        print(f"- Linked {linked_count} unregistered participants to users")
        print(f"- Updated {updated_users_count} users' linked_unregistered_names")
        print(f"- Updated {updated_expenses_count} expenses")
        
        return True
        
    except Exception as e:
        # Rollback on error
        if 'trans' in locals():
            trans.rollback()
        print(f"Error during bulk linking: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Close the connection
        connection.close()

if __name__ == "__main__":
    # If run directly, execute for all trips or a specific trip
    trip_id = None
    if len(sys.argv) > 1:
        try:
            trip_id = int(sys.argv[1])
            print(f"Running bulk link for trip ID: {trip_id}")
        except ValueError:
            print("Invalid trip ID provided. Running for all trips.")
            trip_id = None
    
    success = bulk_link_participants_sql(trip_id)
    if success:
        print("Bulk linking process completed successfully!")
    else:
        print("Bulk linking process failed!")
        sys.exit(1)