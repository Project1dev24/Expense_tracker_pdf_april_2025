from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from datetime import date, timedelta
from backend.models.trip import Trip
from backend.models.expense import Expense
from backend.models.user import User
from backend.database import db

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    # Get all trips for the user
    trips = current_user.get_trips()
    
    # Get recent trips (for display in the trips section) - sorted by start date (most recent first)
    recent_trips = sorted(trips, key=lambda t: t.start_date, reverse=True)[:5]
    
    # Get older trips (completed trips that are more than 30 days old)
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    older_trips = []
    for trip in trips:
        if trip.end_date.date() < today and trip.end_date.date() < thirty_days_ago:
            older_trips.append(trip)
    # Sort older trips by end date (oldest first)
    older_trips = sorted(older_trips, key=lambda t: t.end_date, reverse=True)
    
    # Get total number of trips
    total_trips = len(trips)
    
    # Get total balance across all trips
    total_balance = current_user.get_total_balance()
    
    # Calculate total amount spent (sum of all expenses paid by the user)
    total_spent = 0
    for trip in trips:
        expenses = Expense.query.filter_by(trip_id=trip.id, payer_id=current_user.id).all()
        for expense in expenses:
            total_spent += expense.amount
    
    # Get user's paid expenses (better approach for dashboard display)
    user_paid_expenses = []
    
    # Collect all expenses paid by the current user across all their trips
    for trip in trips:
        # Get expenses paid by the current user in this trip
        expenses = Expense.query.filter_by(trip_id=trip.id, payer_id=current_user.id).order_by(Expense.date.desc()).limit(10).all()
        for expense in expenses:
            user_paid_expenses.append({
                'expense': expense,
                'trip': trip,
                'payer_name': current_user.name
            })
    
    # Sort user's paid expenses by date and take the most recent 10
    user_paid_expenses = sorted(user_paid_expenses, key=lambda e: e['expense'].date, reverse=True)[:10]
    
    # If no user-paid expenses found, fall back to general recent expenses
    if not user_paid_expenses:
        recent_expenses = []
        for trip in recent_trips:
            expenses = Expense.query.filter_by(trip_id=trip.id).order_by(Expense.date.desc()).limit(3).all()
            for expense in expenses:
                # Get payer information
                payer_name = None
                payer_id_str = str(expense.payer_id)
                
                if not payer_id_str.startswith('unregistered_'):
                    try:
                        payer = User.query.get(int(payer_id_str))
                        if payer:
                            payer_name = payer.name
                    except (ValueError, TypeError):
                        pass
                
                recent_expenses.append({
                    'expense': expense,
                    'trip': trip,
                    'payer_name': payer_name
                })
        
        # Sort by date
        recent_expenses = sorted(recent_expenses, key=lambda e: e['expense'].date, reverse=True)[:5]
        user_paid_expenses = recent_expenses
    
    return render_template('main/dashboard.html', 
                          recent_trips=recent_trips,
                          recent_expenses=user_paid_expenses,
                          total_balance=total_balance,
                          total_trips=total_trips,
                          total_spent=total_spent,
                          today=today,
                          older_trips=older_trips)