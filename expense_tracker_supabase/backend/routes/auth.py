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
    
    return render_template('dashboard.html', user=user)

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