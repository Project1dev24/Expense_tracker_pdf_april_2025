from sqlalchemy import func
from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import current_user, login_required
from datetime import date, timedelta, datetime
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

    # Get the 10 most recent expenses paid by the user across all their trips
    trip_ids = [trip.id for trip in trips]
    paid_expenses_query = []
    if trip_ids:
        paid_expenses_query = Expense.query.filter(
            Expense.trip_id.in_(trip_ids),
            Expense.payer_id == current_user.id
        ).order_by(Expense.date.desc()).limit(10).all()

    # Create a dictionary to quickly map trip_id to trip object
    trips_by_id = {trip.id: trip for trip in trips}

    user_paid_expenses = []
    for expense in paid_expenses_query:
        trip_for_expense = trips_by_id.get(expense.trip_id)
        if trip_for_expense:
            user_paid_expenses.append({
                'expense': expense,
                'trip': trip_for_expense,
                'payer_name': current_user.name
            })


    # Prepare month filter data
    months_for_filter = []
    current_date = today
    for _ in range(12):
        months_for_filter.append({
            'value': current_date.strftime('%Y-%m'),
            'text': current_date.strftime('%B %Y')
        })
        current_date = (current_date.replace(day=1) - timedelta(days=1))

    # --- Chart Data Preparation ---

    # 1. Spending by Category (Pie Chart)
    category_spending = db.session.query(
        Expense.category, func.sum(Expense.amount)
    ).filter(
        Expense.trip_id.in_(trip_ids)
    ).group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).all() if trip_ids else []

    category_labels = [item[0] or 'Uncategorized' for item in category_spending]
    category_values = [float(item[1]) for item in category_spending]

    # 2. Spending Over Time (Line Chart for last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_spending = db.session.query(
        func.date(Expense.date),
        func.sum(Expense.amount)
    ).filter(
        Expense.trip_id.in_(trip_ids),
        Expense.date >= thirty_days_ago
    ).group_by(func.date(Expense.date)).order_by(func.date(Expense.date)).all() if trip_ids else []

    spending_data_map = {item[0]: float(item[1]) for item in daily_spending}
    line_chart_labels = [(datetime.utcnow().date() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]
    line_chart_values = [spending_data_map.get(day, 0) for day in line_chart_labels]


    return render_template('main/dashboard.html',
                           recent_trips=recent_trips,
                           recent_expenses=user_paid_expenses,
                           total_balance=total_balance,
                           total_trips=total_trips,
                           total_spent=total_spent,
                           today=today,
                           older_trips=older_trips,
                           months_for_filter=months_for_filter,
                           category_labels=category_labels,
                           category_values=category_values,
                           line_chart_labels=line_chart_labels,
                           line_chart_values=line_chart_values)


@bp.route('/api/dashboard_data')
@login_required
def api_dashboard_data():
    trip_id = request.args.get('trip_id', type=int)
    month = request.args.get('month') # YYYY-MM format

    # Base query for user's expenses
    user_trips = current_user.get_trips()
    trip_ids = [trip.id for trip in user_trips]

    if not trip_ids:
        return jsonify({})

    # --- Main Query for all expenses to be filtered ---
    base_query = Expense.query.filter(Expense.trip_id.in_(trip_ids))

    if trip_id:
        if trip_id in trip_ids: # Security check
            base_query = base_query.filter(Expense.trip_id == trip_id)
        else:
            return jsonify({'error': 'Invalid trip_id'}), 403

    if month:
        try:
            year, month_num = map(int, month.split('-'))
            start_date = datetime(year, month_num, 1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            base_query = base_query.filter(Expense.date >= start_date, Expense.date <= end_date)
        except ValueError:
            return jsonify({'error': 'Invalid month format. Use YYYY-MM'}), 400

    # 1. Spending by Category (Pie Chart)
    category_spending = db.session.query(
        Expense.category, func.sum(Expense.amount)
    ).select_from(base_query.subquery()).group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).all()

    category_labels = [item[0] or 'Uncategorized' for item in category_spending]
    category_values = [float(item[1]) for item in category_spending]

    # 2. Spending Over Time (Line Chart)
    if month: # If filtering by month, show daily spending
        date_format_str = '%Y-%m-%d'
        daily_spending = db.session.query(
            func.date(Expense.date), func.sum(Expense.amount)
        ).select_from(base_query.subquery()).group_by(func.date(Expense.date)).order_by(func.date(Expense.date)).all()

        spending_data_map = {item[0]: float(item[1]) for item in daily_spending}
        line_chart_labels = [(start_date.date() + timedelta(days=i)).strftime(date_format_str) for i in range((end_date.date() - start_date.date()).days + 1)]
        line_chart_values = [spending_data_map.get(day, 0) for day in line_chart_labels]

    else: # If no month filter, show monthly spending for last 12 months
        date_format_str = '%Y-%m'
        twelve_months_ago = (datetime.utcnow().replace(day=1) - timedelta(days=365)).replace(day=1)
        monthly_spending_query = base_query.filter(Expense.date >= twelve_months_ago)

        monthly_spending = db.session.query(
            func.strftime(date_format_str, Expense.date), func.sum(Expense.amount)
        ).select_from(monthly_spending_query.subquery()).group_by(func.strftime(date_format_str, Expense.date)).order_by(func.strftime(date_format_str, Expense.date)).all()

        spending_data_map = {item[0]: float(item[1]) for item in monthly_spending}
        line_chart_labels = [((datetime.utcnow() - timedelta(days=30*i)).strftime(date_format_str)) for i in range(11, -1, -1)]
        line_chart_values = [spending_data_map.get(month_label, 0) for month_label in line_chart_labels]

    return jsonify({
        'category_labels': category_labels,
        'category_values': category_values,
        'line_chart_labels': line_chart_labels,
        'line_chart_values': line_chart_values
    })
