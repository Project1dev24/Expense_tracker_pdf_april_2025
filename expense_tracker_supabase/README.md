# Expense Tracker with Supabase Integration

A modern expense tracking application built with Flask and Supabase, featuring user authentication, trip management, and expense tracking.

## Features

✅ **User Authentication**
- Email/password registration and login
- Magic link (passwordless) authentication
- User profile management with real names

✅ **Trip Management**
- Create and manage trips
- Add participants to trips
- View trip details and expenses

✅ **Expense Tracking**
- Add expenses to trips
- Split expenses among participants
- Track balances and settlements

✅ **Dashboard Features**
- User profile management
- Sync expenses button to recalculate all expenses for admin trips

## Project Structure

```
expense_tracker_supabase/
├── backend/              # Main application code
│   ├── app.py           # Flask application entry point
│   ├── database.py      # Supabase database service
│   ├── models/          # Data models
│   ├── routes/          # API routes
│   └── templates/       # HTML templates
├── docs/                # Documentation
├── scripts/             # Utility scripts
└── supabase/            # Supabase configuration and migrations
```

## Getting Started

### Prerequisites

- Python 3.8+
- Supabase account and project

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```env
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_service_role_key
   SECRET_KEY=your_flask_secret_key
   ```

4. Apply database schema:
   ```bash
   cd supabase
   supabase link --project-ref your_project_id
   supabase db push
   ```

5. Run the application:
   ```bash
   cd backend
   python app.py
   ```

## Current Status

✅ **Phase 1 Complete:**
- User authentication (email/password and magic link)
- Trip creation and management
- Basic expense tracking
- Dashboard with sync functionality

## Next Steps

🔜 **Phase 2 Planned:**
- Advanced expense features
- Settlement calculations
- Enhanced dashboard
- Data visualization

## Documentation

See `docs/` folder for detailed documentation:
- [Supabase Integration Guide](docs/SUPABASE_INTEGRATION.md)
- [Setup Instructions](docs/SUPABASE_SETUP.md)
- [Phased Implementation Plan](docs/SUPABASE_PHASED_IMPLEMENTATION.md)

## Scripts

Utility scripts are available in the `scripts/` folder for:
- Database schema management
- Testing and debugging
- Setup and configuration

## License

This project is for educational purposes.