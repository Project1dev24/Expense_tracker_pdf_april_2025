#!/usr/bin/env python3
"""
Trip routes for Supabase expense tracker
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from datetime import datetime
from ..database import supabase_service
from ..models.user import User
from ..models.trip import Trip
from ..models.expense import Expense
from ..models.unregistered_participant import UnregisteredParticipant

bp = Blueprint('trips', __name__)

def get_current_user():
    """Get current user from session"""
    user_data = session.get('user')
    if user_data:
        return User.from_dict(user_data)
    return None

@bp.route('/')
def list_trips():
    """List all trips for the current user"""
    user = get_current_user()
    if not user:
        flash('Please log in to view your trips', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Get trips from Supabase
        trips_data = supabase_service.get_trips_by_user(user.id)
        trips = [Trip.from_dict(trip_data) for trip_data in trips_data]
        
        return render_template('trips/list.html', trips=trips, user=user)
    except Exception as e:
        flash(f'Error loading trips: {str(e)}', 'error')
        return render_template('trips/list.html', trips=[], user=user)

@bp.route('/create', methods=['GET', 'POST'])
def create_trip():
    """Create a new trip"""
    user = get_current_user()
    if not user:
        flash('Please log in to create a trip', 'error')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            
            if not name or not start_date or not end_date:
                flash('All fields are required', 'error')
                return render_template('trips/create.html', user=user)
            
            # Create trip object
            trip = Trip(
                name=name,
                description=description,
                start_date=datetime.fromisoformat(start_date),
                end_date=datetime.fromisoformat(end_date),
                admin_id=user.id
            )
            
            # Save to Supabase
            trip_data = supabase_service.create_trip(trip.to_dict())
            if trip_data:
                flash('Trip created successfully!', 'success')
                return redirect(url_for('trips.list_trips'))
            else:
                flash('Failed to create trip.', 'error')
                
        except Exception as e:
            flash(f'Error creating trip: {str(e)}', 'error')
    
    return render_template('trips/create.html', user=user)

@bp.route('/<trip_id>')
def view_trip(trip_id):
    """View a specific trip"""
    user = get_current_user()
    if not user:
        flash('Please log in to view this trip', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Get trip from Supabase
        trip_data = supabase_service.get_trip(trip_id)
        if not trip_data:
            flash('Trip not found', 'error')
            return redirect(url_for('trips.list_trips'))
        
        trip = Trip.from_dict(trip_data)
        
        # Check if user has access to this trip
        if user.id != trip.admin_id and user.id not in trip.get_participants_list():
            flash('You do not have access to this trip', 'error')
            return redirect(url_for('trips.list_trips'))
        
        # Get expenses for this trip
        expenses_data = supabase_service.get_expenses_by_trip(trip_id)
        expenses = [Expense.from_dict(expense_data) for expense_data in expenses_data]
        
        # Get unregistered participants
        unregistered_data = supabase_service.get_unregistered_participants_by_trip(trip_id)
        unregistered_participants = [UnregisteredParticipant.from_dict(data) for data in unregistered_data]
        
        # Calculate total expenses
        total_expenses = trip.calculate_total_expenses(expenses)
        
        # Calculate balances
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
        
        return render_template('trips/view.html', 
                             trip=trip, 
                             expenses=expenses,
                             unregistered_participants=unregistered_participants,
                             total_expenses=total_expenses,
                             balances=balances,
                             user=user)
                             
    except Exception as e:
        flash(f'Error loading trip: {str(e)}', 'error')
        return redirect(url_for('trips.list_trips'))

@bp.route('/<trip_id>/edit', methods=['GET', 'POST'])
def edit_trip(trip_id):
    """Edit a trip"""
    user = get_current_user()
    if not user:
        flash('Please log in to edit this trip', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Get trip from Supabase
        trip_data = supabase_service.get_trip(trip_id)
        if not trip_data:
            flash('Trip not found', 'error')
            return redirect(url_for('trips.list_trips'))
        
        trip = Trip.from_dict(trip_data)
        
        # Check if user is admin of this trip
        if user.id != trip.admin_id:
            flash('You do not have permission to edit this trip', 'error')
            return redirect(url_for('trips.view_trip', trip_id=trip_id))
        
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            
            if not name or not start_date or not end_date:
                flash('All fields are required', 'error')
                return render_template('trips/edit.html', trip=trip, user=user)
            
            # Update trip
            trip.name = name
            trip.description = description
            trip.start_date = datetime.fromisoformat(start_date)
            trip.end_date = datetime.fromisoformat(end_date)
            trip.updated_at = datetime.utcnow()
            
            # Save to Supabase
            updated_trip_data = supabase_service.update_trip(trip_id, trip.to_dict())
            if updated_trip_data:
                flash('Trip updated successfully!', 'success')
                return redirect(url_for('trips.view_trip', trip_id=trip_id))
            else:
                flash('Failed to update trip', 'error')
        
        return render_template('trips/edit.html', trip=trip, user=user)
        
    except Exception as e:
        flash(f'Error editing trip: {str(e)}', 'error')
        return redirect(url_for('trips.view_trip', trip_id=trip_id))

@bp.route('/<trip_id>/delete', methods=['POST'])
def delete_trip(trip_id):
    """Delete a trip"""
    user = get_current_user()
    if not user:
        flash('Please log in to delete this trip', 'error')
        return redirect(url_for('auth.login'))
    
    try:
        # Get trip from Supabase
        trip_data = supabase_service.get_trip(trip_id)
        if not trip_data:
            flash('Trip not found', 'error')
            return redirect(url_for('trips.list_trips'))
        
        trip = Trip.from_dict(trip_data)
        
        # Check if user is admin of this trip
        if user.id != trip.admin_id:
            flash('You do not have permission to delete this trip', 'error')
            return redirect(url_for('trips.view_trip', trip_id=trip_id))
        
        # Delete from Supabase
        if supabase_service.delete_trip(trip_id):
            flash('Trip deleted successfully!', 'success')
        else:
            flash('Failed to delete trip', 'error')
            
    except Exception as e:
        flash(f'Error deleting trip: {str(e)}', 'error')
    
    return redirect(url_for('trips.list_trips'))