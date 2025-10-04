#!/usr/bin/env python3
"""
Database service for Supabase integration
"""

import os
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

class SupabaseService:
    """Service class for interacting with Supabase database"""
    
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
        
        self.client = create_client(supabase_url, supabase_key)
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
    
    def _get_client(self):
        """Get the client (always use the service client for server-side operations)"""
        return self.client
    
    # User operations
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            response = self._get_client().table('profiles').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            response = self._get_client().table('profiles').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user data"""
        try:
            response = self._get_client().table('profiles').update(user_data).eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating user: {e}")
            return None
    
    def update_user_name(self, user_id: str, name: str) -> Optional[Dict[str, Any]]:
        """Update user's name"""
        try:
            response = self._get_client().table('profiles').update({'name': name}).eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating user name: {e}")
            return None
    
    # Trip operations
    def get_trip(self, trip_id: str) -> Optional[Dict[str, Any]]:
        """Get trip by ID"""
        try:
            response = self._get_client().table('trips').select('*').eq('id', trip_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting trip: {e}")
            return None
    
    def get_trips_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all trips for a user (as admin or participant)"""
        try:
            # Get trips where user is admin
            admin_response = self._get_client().table('trips').select('*').eq('admin_id', user_id).execute()
            
            # Get trips where user is participant
            # We need to handle JSON parsing errors gracefully
            all_trips = []
            
            # Add admin trips
            for trip in admin_response.data:
                # Validate and fix JSON data if needed
                trip = self._validate_trip_data(trip)
                all_trips.append(trip)
            
            # Add participant trips with a more robust query
            participant_response = self._get_client().table('trips').select('*').execute()
            for trip in participant_response.data:
                # Check if user is in participants list
                try:
                    participants = trip.get('participants', '[]')
                    if isinstance(participants, str):
                        participants_list = json.loads(participants)
                    else:
                        participants_list = participants
                    
                    if user_id in participants_list and trip['id'] not in [t['id'] for t in all_trips]:
                        # Validate and fix JSON data if needed
                        trip = self._validate_trip_data(trip)
                        all_trips.append(trip)
                except (json.JSONDecodeError, TypeError):
                    # Skip trips with invalid JSON data
                    continue
            
            return all_trips
        except Exception as e:
            print(f"Error getting trips: {e}")
            return []
    
    def _validate_trip_data(self, trip_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and fix trip data to ensure proper JSON formatting"""
        try:
            # Fix participants field
            participants = trip_data.get('participants', '[]')
            if isinstance(participants, str):
                try:
                    json.loads(participants)
                except json.JSONDecodeError:
                    # If invalid JSON, reset to empty array
                    trip_data['participants'] = '[]'
            elif isinstance(participants, list):
                trip_data['participants'] = json.dumps(participants)
            else:
                trip_data['participants'] = '[]'
        except Exception:
            trip_data['participants'] = '[]'
        
        return trip_data
    
    def create_trip(self, trip_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new trip"""
        try:
            # Remove columns that don't exist in the current schema
            filtered_trip_data = {
                'name': trip_data['name'],
                'description': trip_data['description'],
                'start_date': trip_data['start_date'],
                'end_date': trip_data['end_date'],
                'admin_id': trip_data['admin_id'],
                'participants': trip_data['participants'] if isinstance(trip_data['participants'], str) else json.dumps(trip_data['participants'])
            }
            
            response = self._get_client().table('trips').insert(filtered_trip_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating trip: {e}")
            return None
    
    def update_trip(self, trip_id: str, trip_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update trip data"""
        try:
            # Remove columns that don't exist in the current schema
            filtered_trip_data = {
                'name': trip_data['name'],
                'description': trip_data['description'],
                'start_date': trip_data['start_date'],
                'end_date': trip_data['end_date'],
                'updated_at': trip_data['updated_at'],
                'participants': trip_data['participants'] if isinstance(trip_data['participants'], str) else json.dumps(trip_data['participants'])
            }
                
            response = self._get_client().table('trips').update(filtered_trip_data).eq('id', trip_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating trip: {e}")
            return None
    
    def delete_trip(self, trip_id: str) -> bool:
        """Delete a trip"""
        try:
            self._get_client().table('trips').delete().eq('id', trip_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting trip: {e}")
            return False
    
    # Expense operations
    def get_expense(self, expense_id: str) -> Optional[Dict[str, Any]]:
        """Get expense by ID"""
        try:
            response = self._get_client().table('expenses').select('*').eq('id', expense_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting expense: {e}")
            return None
    
    def get_expenses_by_trip(self, trip_id: str) -> List[Dict[str, Any]]:
        """Get all expenses for a trip"""
        try:
            response = self._get_client().table('expenses').select('*').eq('trip_id', trip_id).execute()
            return response.data
        except Exception as e:
            print(f"Error getting expenses: {e}")
            return []
    
    def create_expense(self, expense_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new expense"""
        try:
            # Ensure JSON fields are properly formatted
            if 'participants' in expense_data and not isinstance(expense_data['participants'], str):
                expense_data['participants'] = json.dumps(expense_data['participants'])
            if 'shares' in expense_data and not isinstance(expense_data['shares'], str):
                expense_data['shares'] = json.dumps(expense_data['shares'])
            if 'items' in expense_data and not isinstance(expense_data['items'], str):
                expense_data['items'] = json.dumps(expense_data['items'])
            
            response = self._get_client().table('expenses').insert(expense_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating expense: {e}")
            return None
    
    def update_expense(self, expense_id: str, expense_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update expense data"""
        try:
            # Ensure JSON fields are properly formatted
            if 'participants' in expense_data and not isinstance(expense_data['participants'], str):
                expense_data['participants'] = json.dumps(expense_data['participants'])
            if 'shares' in expense_data and not isinstance(expense_data['shares'], str):
                expense_data['shares'] = json.dumps(expense_data['shares'])
            if 'items' in expense_data and not isinstance(expense_data['items'], str):
                expense_data['items'] = json.dumps(expense_data['items'])
                
            response = self._get_client().table('expenses').update(expense_data).eq('id', expense_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating expense: {e}")
            return None
    
    def delete_expense(self, expense_id: str) -> bool:
        """Delete an expense"""
        try:
            self._get_client().table('expenses').delete().eq('id', expense_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting expense: {e}")
            return False
    
    # Unregistered participant operations
    def get_unregistered_participants_by_trip(self, trip_id: str) -> List[Dict[str, Any]]:
        """Get all unregistered participants for a trip"""
        try:
            response = self._get_client().table('unregistered_participants').select('*').eq('trip_id', trip_id).execute()
            return response.data
        except Exception as e:
            print(f"Error getting unregistered participants: {e}")
            return []
    
    def create_unregistered_participant(self, participant_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new unregistered participant"""
        try:
            response = self._get_client().table('unregistered_participants').insert(participant_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating unregistered participant: {e}")
            return None
    
    def update_unregistered_participant(self, participant_id: str, participant_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update unregistered participant data"""
        try:
            response = self._get_client().table('unregistered_participants').update(participant_data).eq('id', participant_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating unregistered participant: {e}")
            return None
    
    def delete_unregistered_participant(self, participant_id: str) -> bool:
        """Delete an unregistered participant"""
        try:
            self._get_client().table('unregistered_participants').delete().eq('id', participant_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting unregistered participant: {e}")
            return False

# Create a global instance
supabase_service = SupabaseService()