#!/usr/bin/env python3
"""
Authentication routes for Supabase integration
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from supabase import create_client
import os
from dotenv import load_dotenv
import secrets
from datetime import datetime
from ..database import supabase_service
from ..models.trip import Trip
from ..models.expense import Expense
from ..models.unregistered_participant import UnregisteredParticipant

# Load environment variables
load_dotenv()

# Create Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase = create_client(supabase_url, supabase_key)

bp = Blueprint('auth', __name__)

def get_current_user():
    """Get current user from Supabase session"""
    try:
        user = supabase.auth.get_user()
        return user.user if user else None
    except:
        return None

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login with email and password"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # Sign in with Supabase Auth
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response:
                # Supabase automatically handles JWT tokens
                # We can store minimal user info in session
                session['user'] = {
                    "id": response.user.id,
                    "email": response.user.email
                }
                # Store access token for database operations
                if hasattr(response, 'session') and response.session:
                    session['access_token'] = response.session.access_token
                flash('Login successful!', 'success')
                return redirect(url_for('auth.dashboard'))
            else:
                flash('Login failed. Please check your credentials.', 'error')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            # Sign up with Supabase Auth, including user metadata
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "name": name
                    }
                }
            })
            
            if response:
                flash('Registration successful! Please check your email to confirm your account.', 'success')
                return redirect(url_for('auth.check_email', email=email))
            else:
                flash('Registration failed.', 'error')
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'error')
    
    return render_template('auth/register.html')

@bp.route('/check-email')
def check_email():
    """Page instructing user to check email for confirmation link"""
    email = request.args.get('email')
    if not email:
        flash('No email provided', 'error')
        return redirect(url_for('auth.register'))
    
    return render_template('auth/check_email.html', email=email)

@bp.route('/login/magic-link', methods=['GET', 'POST'])
def login_magic_link():
    """Login with magic link (passwordless)"""
    if request.method == 'POST':
        email = request.form.get('email')
        
        try:
            # Send magic link via Supabase Auth
            response = supabase.auth.sign_in_with_otp({
                "email": email
            })
            
            if response:
                flash('Magic link sent! Please check your email.', 'success')
                return redirect(url_for('auth.check_email', email=email))
            else:
                flash('Failed to send magic link.', 'error')
        except Exception as e:
            flash(f'Error sending magic link: {str(e)}', 'error')
    
    return render_template('auth/login_magic_link.html')

@bp.route('/register/magic-link', methods=['GET', 'POST'])
def register_magic_link():
    """Register with magic link (passwordless)"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        
        try:
            # For magic link registration, we need to provide a password
            # We'll generate a random one
            temp_password = secrets.token_urlsafe(16)
            
            # Sign up with Supabase Auth using temporary password and user metadata
            response = supabase.auth.sign_up({
                "email": email,
                "password": temp_password,
                "options": {
                    "data": {
                        "name": name
                    }
                }
            })
            
            if response:
                flash('Registration successful! Please check your email for a magic link.', 'success')
                return redirect(url_for('auth.check_email', email=email))
            else:
                flash('Registration failed.', 'error')
        except Exception as e:
            flash(f'Registration error: {str(e)}', 'error')
    
    return render_template('auth/register_magic_link.html')

@bp.route('/auth/callback')
def auth_callback():
    """Handle authentication callbacks from Supabase"""
    try:
        # Get the token from the URL
        code = request.args.get('code')
        if code:
            # Exchange the code for a session
            response = supabase.auth.exchange_code_for_session(code)
            if response:
                # Supabase automatically manages JWT tokens
                # Store user in session
                session['user'] = {
                    "id": response.user.id,
                    "email": response.user.email
                }
                # Store access token for database operations
                if hasattr(response, 'session') and response.session:
                    session['access_token'] = response.session.access_token
                flash('Authentication successful!', 'success')
                return redirect(url_for('auth.dashboard'))
        
        # If no code or exchange failed
        flash('Authentication failed.', 'error')
        return redirect(url_for('auth.login'))
    except Exception as e:
        flash(f'Authentication error: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

@bp.route('/verify')
def verify_email():
    """Handle email verification callbacks"""
    try:
        # Get the token from the URL
        token = request.args.get('token_hash')
        if token:
            # Verify the email
            response = supabase.auth.verify_otp({
                "token_hash": token,
                "type": "email"
            })
            if response:
                # Supabase automatically manages JWT tokens
                # Store user in session
                session['user'] = {
                    "id": response.user.id,
                    "email": response.user.email
                }
                # Store access token for database operations
                if hasattr(response, 'session') and response.session:
                    session['access_token'] = response.session.access_token
                flash('Email verified successfully!', 'success')
                return redirect(url_for('auth.dashboard'))
        
        # If no token or verification failed
        flash('Email verification failed.', 'error')
        return redirect(url_for('auth.login'))
    except Exception as e:
        flash(f'Email verification error: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

@bp.route('/logout')
def logout():
    """Logout the current user"""
    try:
        supabase.auth.sign_out()
        session.pop('user', None)
        session.pop('access_token', None)
        flash('You have been logged out', 'info')
    except Exception as e:
        flash(f'Logout error: {str(e)}', 'error')
    
    return redirect(url_for('auth.login'))

@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """User profile management"""
    # Check if user is authenticated
    supabase_user = get_current_user()
    if not supabase_user:
        flash('Please log in to access your profile', 'error')
        return redirect(url_for('auth.login'))
    
    # Get user profile from database
    user_profile = supabase_service.get_user(supabase_user.id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        if name and user_profile:
            # Update user's name in the database
            updated_profile = supabase_service.update_user_name(supabase_user.id, name)
            if updated_profile:
                flash('Profile updated successfully!', 'success')
                user_profile = updated_profile
            else:
                flash('Failed to update profile.', 'error')
        else:
            flash('Name is required.', 'error')
    
    return render_template('auth/profile.html', user=supabase_user, profile=user_profile)

@bp.route('/settings')
def settings():
    """User settings page"""
    # Check if user is authenticated
    supabase_user = get_current_user()
    if not supabase_user:
        flash('Please log in to access settings', 'error')
        return redirect(url_for('auth.login'))
    
    # Get current theme from localStorage (default to 'classic')
    # In a real implementation, this would come from user preferences in the database
    current_theme = request.cookies.get('theme', 'classic')
    
    return render_template('settings.html', user=supabase_user, current_theme=current_theme)

@bp.route('/dashboard')
def dashboard():
    """User dashboard"""
    # Check if user is authenticated via Supabase
    try:
        supabase_user = get_current_user()
        session_user = session.get('user')
        
        # If we have a session user but no Supabase user, try to refresh
        if session_user and not supabase_user:
            # Try to get user from session
            user = session_user
        elif supabase_user:
            # Use Supabase user and update session
            user = {
                "id": supabase_user.id,
                "email": supabase_user.email
            }
            session['user'] = user
        else:
            # No user authenticated
            flash('Please log in to access the dashboard', 'error')
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        flash('Please log in to access the dashboard', 'error')
        return redirect(url_for('auth.login'))
    
    # Fetch actual data for the dashboard
    try:
        # Get user trips (simplified query to avoid the error)
        trips_response = supabase_service._get_client().table('trips').select('*').eq('admin_id', user["id"]).execute()
        recent_trips = [Trip.from_dict(trip_data) for trip_data in trips_response.data[:5]]  # Limit to 5 recent trips
        
        # Get total trips count
        total_trips = len(trips_response.data)
        
        # Get recent expenses for this user
        expenses_response = supabase_service._get_client().table('expenses').select('*, trips(name, start_date)').eq('payer_id', user["id"]).order('date', desc=True).limit(5).execute()
        recent_expenses = []
        for expense_data in expenses_response.data:
            trip_data = expense_data.pop('trips', {})
            recent_expenses.append({
                'expense': Expense.from_dict(expense_data),
                'trip': Trip.from_dict(trip_data) if trip_data else None
            })
        
        # Calculate total spent
        total_spent = sum(expense.amount for expense in [item['expense'] for item in recent_expenses])
        
        # For balance calculation, we'll set a default value
        total_balance = 0.0
        
        context = {
            'user': user,
            'total_balance': total_balance,
            'total_spent': total_spent,
            'total_trips': total_trips,
            'recent_trips': recent_trips,
            'recent_expenses': recent_expenses,
            'trips': recent_trips,  # For chart filters
            'months_for_filter': [],  # Empty for now
            'category_labels': [],  # Empty for now
            'category_values': [],  # Empty for now
            'line_chart_labels': [],  # Empty for now
            'line_chart_values': []  # Empty for now
        }
        
    except Exception as e:
        # Fallback to default context if data fetching fails
        print(f"Error fetching dashboard data: {e}")
        context = {
            'user': user,
            'total_balance': 0.0,
            'total_spent': 0.0,
            'total_trips': 0,
            'recent_trips': [],
            'recent_expenses': [],
            'trips': [],
            'months_for_filter': [],
            'category_labels': [],
            'category_values': [],
            'line_chart_labels': [],
            'line_chart_values': []
        }
    
    return render_template('dashboard.html', **context)

@bp.route('/api/user')
def api_user():
    """API endpoint to get current user info with JWT validation"""
    try:
        user = get_current_user()
        if user:
            return jsonify({
                "authenticated": True,
                "user": {
                    "id": user.id,
                    "email": user.email
                }
            })
        else:
            return jsonify({
                "authenticated": False,
                "user": None
            })
    except Exception as e:
        return jsonify({
            "authenticated": False,
            "user": None,
            "error": str(e)
        })

@bp.route('/sync-expenses', methods=['POST'])
def sync_expenses():
    """Sync all expenses for trips where user is admin"""
    # Check if user is authenticated via Supabase
    try:
        supabase_user = get_current_user()
        session_user = session.get('user')
        
        # If we have a session user but no Supabase user, try to refresh
        if session_user and not supabase_user:
            # Try to get user from session
            user = session_user
        elif supabase_user:
            # Use Supabase user and update session
            user = {
                "id": supabase_user.id,
                "email": supabase_user.email
            }
            session['user'] = user
        else:
            # Check if this is an AJAX request and try to get user from session
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                # For AJAX requests, rely on session
                session_user = session.get('user')
                if session_user:
                    user = session_user
                else:
                    return jsonify({
                        "success": False,
                        "error": "Please log in to sync expenses"
                    }), 401
            else:
                # No user authenticated
                return jsonify({
                    "success": False,
                    "error": "Please log in to sync expenses"
                }), 401
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Authentication error: " + str(e)
        }), 401
    
    try:
        user_id = user["id"]
        
        # Get all trips where user is admin
        admin_trips_data = supabase_service._get_client().table('trips').select('*').eq('admin_id', user_id).execute()
        admin_trips = [Trip.from_dict(trip_data) for trip_data in admin_trips_data.data]
        
        synced_count = 0
        recalculated_count = 0
        
        # For each admin trip, recalculate and update expenses
        for trip in admin_trips:
            try:
                # Get all expenses for this trip
                expenses_data = supabase_service.get_expenses_by_trip(str(trip.id))
                expenses = [Expense.from_dict(expense_data) for expense_data in expenses_data]
                
                # Get unregistered participants
                unregistered_data = supabase_service.get_unregistered_participants_by_trip(str(trip.id))
                unregistered_participants = [UnregisteredParticipant.from_dict(data) for data in unregistered_data]
                
                # Recalculate balances for all participants
                balances = {}
                participants = trip.get_participants_list()
                if str(trip.admin_id) not in participants:
                    participants.append(str(trip.admin_id))
                
                for participant_id in participants:
                    balances[participant_id] = trip.calculate_user_balance(participant_id, expenses)
                
                # Add unregistered participants to balances
                for unregistered in unregistered_participants:
                    unregistered_id = f'unregistered_{unregistered.name}'
                    # Calculate balance for unregistered participant
                    total_share = 0
                    balance = 0
                    
                    # For now, we'll use simplified balance calculation since we removed advances and general payments
                    # Calculate their total share and what they've paid
                    for expense in expenses:
                        shares = expense.get_shares()
                        if unregistered_id in shares:
                            # If they were included in an expense, add their share (they owe this amount)
                            total_share += shares[unregistered_id]
                            
                        # If they paid for an expense, add the amount (they are owed this amount)
                        if expense.payer_id == unregistered_id:
                            balance += expense.amount
                    
                    # Calculate final balance: what they paid - what they owe
                    # Positive means they are owed money, negative means they owe money
                    final_balance = balance - total_share
                    balances[unregistered_id] = final_balance
                
                # In a real implementation, you might want to:
                # 1. Update any cached values in the trip record
                # 2. Handle any data inconsistencies
                # 3. Store the calculated balances somewhere if needed
                
                # For now, we'll just log that we've processed this trip
                print(f"Synced expenses for trip: {trip.name}")
                synced_count += 1
                
                # Count how many trips had actual expense calculations
                if len(expenses) > 0:
                    recalculated_count += 1
                
            except Exception as trip_error:
                print(f"Error syncing trip {trip.id}: {str(trip_error)}")
                # Continue with other trips even if one fails
        
        return jsonify({
            "success": True,
            "message": f"Successfully synced {synced_count} trips, recalculated expenses for {recalculated_count} trips",
            "synced_count": synced_count,
            "recalculated_count": recalculated_count
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
