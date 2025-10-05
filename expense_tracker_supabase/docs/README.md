# Expense Tracker Application

A comprehensive expense tracking application with Supabase authentication.

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd expense_tracker
   ```

2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install packages individually:
   ```bash
   pip install flask flask-login python-dotenv supabase
   ```

### Supabase Setup

1. Create a Supabase account at [https://supabase.com/](https://supabase.com/)
2. Create a new project:
   - Click "New Project"
   - Enter project name (e.g., "expense-tracker")
   - Set a database password
   - Select your region
   - Click "Create Project"
3. Get your API credentials:
   - Once project is ready, go to "Project Settings" → "API"
   - Copy your "Project URL" and "anon" public key
4. Configure environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and replace the placeholder values with your actual Supabase credentials

### Running the Application

```bash
cd backend
python app.py
```

The application will be available at `http://localhost:5004`

## Features

- User authentication (email/password and magic link)
- Expense tracking with categories
- Trip management
- Dashboard with expense analytics
- Responsive design

## Supabase Integration

This application uses Supabase for authentication. The integration includes:

- User registration and login
- Passwordless authentication with magic links
- Email verification
- Session management

## Database

The application uses both:
- SQLite for local data storage (expenses, trips, etc.)
- Supabase for user authentication

For a complete Supabase database setup with all tables, see [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

For a complete migration to Supabase (moving everything to Supabase), see:
- [SUPABASE_COMPLETE_INTEGRATION.md](SUPABASE_COMPLETE_INTEGRATION.md)
- [SUPABASE_PHASED_IMPLEMENTATION.md](SUPABASE_PHASED_IMPLEMENTATION.md)

## Project Structure

```
expense_tracker/
├── backend/
│   ├── app.py              # Application entry point
│   ├── app_factory.py      # Flask app factory
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database initialization
│   ├── models/             # Database models
│   ├── routes/             # Route handlers
│   ├── supabase_client.py  # Supabase client wrapper
│   ├── supabase_schema.sql # Supabase database schema
│   ├── supabase_complete_schema.sql # Complete Supabase schema
│   ├── migrate_to_supabase.py # Data migration script
│   └── templates/          # HTML templates
└── README.md
```

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```
FLASK_APP=app.py
FLASK_DEBUG=True
DATABASE_URL=sqlite:///app.db
PORT=5004

# Supabase Configuration
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_project_api_key_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
```

## Testing

To test the Supabase connection, run:

```bash
cd backend
python test_supabase.py
```

## Complete Supabase Database Setup

For detailed instructions on setting up all tables in Supabase, including:

- Creating all necessary tables (users, trips, expenses, unregistered_participants)
- Setting up Row Level Security (RLS)
- Migrating existing data from SQLite
- Configuring security policies

See the complete guide in [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

## Complete Migration to Supabase

For detailed instructions on moving everything to Supabase, including:

- Phased implementation approach
- Authentication migration
- Data migration
- Feature enhancement
- Deployment considerations

See:
- [SUPABASE_COMPLETE_INTEGRATION.md](SUPABASE_COMPLETE_INTEGRATION.md)
- [SUPABASE_PHASED_IMPLEMENTATION.md](SUPABASE_PHASED_IMPLEMENTATION.md)
