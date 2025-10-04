# Trip Schema for Expense Tracker

This document provides instructions for applying the trip schema to your Supabase database.

## Files

- [trip_schema.sql](trip_schema.sql) - Contains the SQL schema for the trips table with RLS policies
- [test_trip_schema.py](test_trip_schema.py) - Python script to test the schema (optional)

## Applying the Schema

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Copy and paste the contents of [trip_schema.sql](trip_schema.sql)
4. Run the SQL commands

## Schema Details

The schema creates:

1. A `trips` table with the following columns:
   - `id` (UUID, primary key)
   - `name` (VARCHAR(100), not null)
   - `description` (TEXT)
   - `start_date` (TIMESTAMP WITH TIME ZONE, not null)
   - `end_date` (TIMESTAMP WITH TIME ZONE, not null)
   - `created_at` (TIMESTAMP WITH TIME ZONE, default now)
   - `updated_at` (TIMESTAMP WITH TIME ZONE, default now)
   - `admin_id` (UUID, foreign key to auth.users)
   - `participants` (JSONB, default empty array)

2. Row Level Security (RLS) policies:
   - Users can view trips they are part of (admin or participant)
   - Users can create trips (must be the admin)
   - Trip admins can update their trips
   - Trip admins can delete their trips

## Testing

After applying the schema, you can test it by:

1. Creating a trip through your application
2. Verifying that RLS policies work correctly
3. Checking that authenticated users can create trips when they are the admin

## Troubleshooting

If you encounter RLS errors:
1. Ensure you are properly authenticated with Supabase
2. Verify that the `admin_id` matches the authenticated user's ID
3. Check that the user exists in the `auth.users` table