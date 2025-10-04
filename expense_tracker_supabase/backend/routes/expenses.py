#!/usr/bin/env python3
"""
Expense routes for Supabase expense tracker
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, flash, jsonify
from datetime import datetime
from ..database import supabase_service
from ..models.user import User
from ..models.trip import Trip
from ..models.expense import Expense
from ..models.unregistered_participant import UnregisteredParticipant

bp = Blueprint('expenses', __name__)

def get_current_user():
    """Get current user from session"""
    user_data = session.get('user')
    if user_data:
        return User.from_dict(user_data)
    return None

@bp.route('/<trip_id>/expenses/create', methods=['GET', 'POST'])
def create_expense(trip_id):
    """Create a new expense"""
    user = get_current_user()
    if not user:
        flash('Please log in to create an expense', 'error')
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
            flash('You do not have permission to add expenses to this trip', 'error')
            return redirect(url_for('trips.view_trip', trip_id=trip_id))
        
        if request.method == 'POST':
            try:
                description = request.form.get('description')
                amount = float(request.form.get('amount', 0))
                currency = request.form.get('currency', 'INR')
                category = request.form.get('category')
                date = request.form.get('date')
                payer_id = request.form.get('payer_id')
                split_method = request.form.get('split_method', 'equal')
                
                if not description or not amount or not payer_id or not date:
                    flash('Required fields are missing', 'error')
                    return render_template('expenses/create.html', trip=trip, user=user)
                
                # Create expense object
                expense = Expense(
                    description=description,
                    amount=amount,
                    currency=currency,
                    category=category,
                    date=datetime.fromisoformat(date),
                    payer_id=payer_id,
                    trip_id=trip_id
                )
                
                # Get participants
                participants = request.form.getlist('participants')
                
                # Get unregistered participants
                unregistered_participants = request.form.getlist('unregistered_participants')
                
                # Update split based on method
                if split_method == 'equal':
                    expense.update_split('equal', participants, unregistered_participants=unregistered_participants)
                elif split_method == 'exact':
                    # Get exact shares from form
                    shares = {}
                    for participant in participants:
                        share_amount = request.form.get(f'share_{participant}')
                        if share_amount:
                            shares[participant] = float(share_amount)
                    
                    # Handle unregistered participants
                    for name in unregistered_participants:
                        share_amount = request.form.get(f'share_unregistered_{name}')
                        if share_amount:
                            shares[f'unregistered_{name}'] = float(share_amount)
                    
                    expense.update_split('exact', participants, shares_data=shares, unregistered_participants=unregistered_participants)
                elif split_method == 'itemized':
                    # For itemized, we'll handle this in a more complex way
                    # For now, we'll just use equal split as a placeholder
                    expense.update_split('equal', participants, unregistered_participants=unregistered_participants)
                
                # Save to Supabase
                expense_data = supabase_service.create_expense(expense.to_dict())
                if expense_data:
                    flash('Expense created successfully!', 'success')
                    return redirect(url_for('trips.view_trip', trip_id=trip_id))
                else:
                    flash('Failed to create expense', 'error')
                    
            except Exception as e:
                flash(f'Error creating expense: {str(e)}', 'error')
        
        # Get unregistered participants for the form
        unregistered_data = supabase_service.get_unregistered_participants_by_trip(trip_id)
        unregistered_participants = [UnregisteredParticipant.from_dict(data) for data in unregistered_data]
        
        return render_template('expenses/create.html', 
                             trip=trip, 
                             user=user,
                             unregistered_participants=unregistered_participants)
                             
    except Exception as e:
        flash(f'Error loading trip: {str(e)}', 'error')
        return redirect(url_for('trips.list_trips'))

@bp.route('/<trip_id>/expenses/<expense_id>/edit', methods=['GET', 'POST'])
def edit_expense(trip_id, expense_id):
    """Edit an expense"""
    user = get_current_user()
    if not user:
        flash('Please log in to edit this expense', 'error')
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
            flash('You do not have permission to edit expenses in this trip', 'error')
            return redirect(url_for('trips.view_trip', trip_id=trip_id))
        
        # Get expense from Supabase
        expense_data = supabase_service.get_expense(expense_id)
        if not expense_data:
            flash('Expense not found', 'error')
            return redirect(url_for('trips.view_trip', trip_id=trip_id))
        
        expense = Expense.from_dict(expense_data)
        
        if request.method == 'POST':
            try:
                description = request.form.get('description')
                amount = float(request.form.get('amount', 0))
                currency = request.form.get('currency', 'INR')
                category = request.form.get('category')
                date = request.form.get('date')
                payer_id = request.form.get('payer_id')
                split_method = request.form.get('split_method', 'equal')
                
                if not description or not amount or not payer_id or not date:
                    flash('Required fields are missing', 'error')
                    return render_template('expenses/edit.html', trip=trip, expense=expense, user=user)
                
                # Update expense object
                expense.description = description
                expense.amount = amount
                expense.currency = currency
                expense.category = category
                expense.date = datetime.fromisoformat(date)
                expense.payer_id = payer_id
                expense.updated_at = datetime.utcnow()
                
                # Get participants
                participants = request.form.getlist('participants')
                
                # Get unregistered participants
                unregistered_participants = request.form.getlist('unregistered_participants')
                
                # Update split based on method
                if split_method == 'equal':
                    expense.update_split('equal', participants, unregistered_participants=unregistered_participants)
                elif split_method == 'exact':
                    # Get exact shares from form
                    shares = {}
                    for participant in participants:
                        share_amount = request.form.get(f'share_{participant}')
                        if share_amount:
                            shares[participant] = float(share_amount)
                    
                    # Handle unregistered participants
                    for name in unregistered_participants:
                        share_amount = request.form.get(f'share_unregistered_{name}')
                        if share_amount:
                            shares[f'unregistered_{name}'] = float(share_amount)
                    
                    expense.update_split('exact', participants, shares_data=shares, unregistered_participants=unregistered_participants)
                elif split_method == 'itemized':
                    # For itemized, we'll handle this in a more complex way
                    # For now, we'll just use equal split as a placeholder
                    expense.update_split('equal', participants, unregistered_participants=unregistered_participants)
                
                # Save to Supabase
                updated_expense_data = supabase_service.update_expense(expense_id, expense.to_dict())
                if updated_expense_data:
                    flash('Expense updated successfully!', 'success')
                    return redirect(url_for('trips.view_trip', trip_id=trip_id))
                else:
                    flash('Failed to update expense', 'error')
                    
            except Exception as e:
                flash(f'Error updating expense: {str(e)}', 'error')
        
        # Get unregistered participants for the form
        unregistered_data = supabase_service.get_unregistered_participants_by_trip(trip_id)
        unregistered_participants = [UnregisteredParticipant.from_dict(data) for data in unregistered_data]
        
        return render_template('expenses/edit.html', 
                             trip=trip, 
                             expense=expense,
                             user=user,
                             unregistered_participants=unregistered_participants)
                             
    except Exception as e:
        flash(f'Error loading expense: {str(e)}', 'error')
        return redirect(url_for('trips.view_trip', trip_id=trip_id))

@bp.route('/<trip_id>/expenses/<expense_id>/delete', methods=['POST'])
def delete_expense(trip_id, expense_id):
    """Delete an expense"""
    user = get_current_user()
    if not user:
        flash('Please log in to delete this expense', 'error')
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
            flash('You do not have permission to delete expenses in this trip', 'error')
            return redirect(url_for('trips.view_trip', trip_id=trip_id))
        
        # Delete from Supabase
        if supabase_service.delete_expense(expense_id):
            flash('Expense deleted successfully!', 'success')
        else:
            flash('Failed to delete expense', 'error')
            
    except Exception as e:
        flash(f'Error deleting expense: {str(e)}', 'error')
    
    return redirect(url_for('trips.view_trip', trip_id=trip_id))