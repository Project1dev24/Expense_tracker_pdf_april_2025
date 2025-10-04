# Complete Supabase Setup Guide

This guide will help you set up a complete Supabase database for your Expense Tracker application, including all tables and data migration. The schema integrates with Supabase Auth and matches your existing SQLite database structure.

## Prerequisites

1. A Supabase account (free at https://supabase.com/)
2. Python 3.7+
3. Required Python packages:
   ```bash
   pip install supabase python-dotenv
   ```

## Step 1: Create Supabase Project

1. Go to [https://supabase.com/](https://supabase.com/) and sign up
2. Click "New Project"
3. Fill in project details:
   - Name: `expense-tracker`
   - Database password: Create a strong password
   - Region: Select closest to you
4. Click "Create Project" (may take 2-3 minutes)

## Step 2: Get API Credentials

1. Once created, go to "Project Settings" → "API"
2. Copy:
   - Project URL (starts with `https://`)
   - anon public key (long string)

## Step 3: Configure Environment Variables

1. Update your `.env` file with actual credentials:
   ```bash
   SUPABASE_URL=your_actual_project_url_here
   SUPABASE_KEY=your_actual_api_key_here
   ```

## Step 4: Create Database Tables

1. In your Supabase dashboard, go to "SQL Editor"
2. Copy the contents of `supabase_schema.sql` and paste it into the editor
3. Click "Run" to execute the schema

This will create all necessary tables that integrate with Supabase Auth:
- `profiles` (extends auth.users for user profile data)
- `trips` (matches your SQLite "trip" table)
- `expenses` (matches your SQLite "expense" table)
- `unregistered_participants` (matches your SQLite "unregistered_participant" table)

## Step 5: Set Up Row Level Security (RLS)

The schema includes RLS policies that ensure users can only access their own data. These are automatically applied when you run the schema.

## Step 6: Test the Connection

Run the test script to verify everything works:
```bash
cd backend
python test_supabase.py
```

## Step 7: Migrate Existing Data (Optional)

If you have existing data in SQLite that you want to move to Supabase:

1. Make sure your SQLite database has data
2. Run the migration script:
   ```bash
   cd backend
   python migrate_to_supabase.py
   ```

## Supabase Table Structure

### profiles (extends auth.users)
- `id` (uuid, primary key) - References auth.users
- `email` (text, unique) - User's email
- `name` (text) - User's full name
- `created_at` (timestamp) - Account creation date
- `last_seen` (timestamp) - Last activity timestamp
- `is_admin` (boolean) - Admin status (default: false)
- `linked_unregistered_names` (text) - JSON array of linked names (default: '[]')

### trips
- `id` (bigint, primary key) - Auto-generated ID
- `name` (varchar(100)) - Trip name
- `description` (text) - Trip description
- `start_date` (timestamp) - Trip start date
- `end_date` (timestamp) - Trip end date
- `created_at` (timestamp) - Creation timestamp
- `updated_at` (timestamp) - Last update timestamp
- `admin_id` (uuid) - References profile (user who created trip)
- `participants` (text) - JSON array of participant IDs
- `unregistered_participants` (text) - JSON array of unregistered participant names (default: '[]')
- `advances_json` (text) - JSON object of advance payments (default: '{}')
- `general_payments_json` (text) - JSON array of general payments (default: '[]')

### expenses
- `id` (bigint, primary key) - Auto-generated ID
- `description` (varchar(200)) - Expense description
- `amount` (double precision) - Expense amount
- `currency` (varchar(3)) - Currency code (default: INR)
- `date` (timestamp) - Expense date
- `created_at` (timestamp) - Creation timestamp
- `updated_at` (timestamp) - Last update timestamp
- `split_method` (varchar(20)) - How expense is split (default: 'equal')
- `payer_id` (text) - Can be UUID (registered user) or string (unregistered name)
- `trip_id` (bigint) - References trip
- `participants` (text) - JSON array of participants
- `shares` (text) - JSON object of how expense is shared
- `items` (text) - JSON array for itemized expenses
- `category` (text) - Expense category

### unregistered_participants
- `id` (bigint, primary key) - Auto-generated ID
- `name` (varchar(100)) - Participant name
- `trip_id` (bigint) - References trip
- `linked_user_id` (uuid) - References profile (linked user, if any)
- `created_at` (timestamp) - Creation timestamp

## Important Notes About Supabase Integration

1. **User Management**: Users are managed by Supabase Auth automatically
2. **UUID vs Integer IDs**: Supabase uses UUIDs for user IDs, while your SQLite uses integers
3. **Profile Data**: User profile information is stored in the `profiles` table
4. **Automatic Profile Creation**: New users automatically get a profile via triggers

## Security Features

1. **Row Level Security (RLS)**: Users can only access their own data
2. **Authentication**: Integrated with Supabase Auth
3. **Data Validation**: Database-level constraints
4. **Indexes**: Optimized for performance

## Troubleshooting

### Connection Issues
- Verify SUPABASE_URL and SUPABASE_KEY in `.env`
- Check internet connectivity
- Ensure Supabase project is not paused

### Migration Issues
- User IDs need to be mapped from integers to UUIDs
- Existing integer IDs will need mapping
- Foreign key relationships must be maintained

### Performance Issues
- Check that indexes are created
- Review RLS policies for complexity
- Consider pagination for large datasets

## Next Steps

1. Implement real-time features using Supabase Realtime
2. Add file storage for receipts using Supabase Storage
3. Set up custom functions for complex calculations
4. Configure email templates for notifications