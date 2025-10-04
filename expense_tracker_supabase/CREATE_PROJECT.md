# Creating Your Supabase Project

This guide will help you create your Supabase project for the Expense Tracker application.

## Step 1: Create Supabase Account

1. Go to [https://supabase.com/](https://supabase.com/)
2. Click "Start your project" or "Sign up"
3. Sign up using your preferred method (GitHub, Google, or email)

## Step 2: Create New Project

1. Once logged in, click "New Project"
2. Fill in the project details:
   - **Project name**: `expense-tracker` (or any name you prefer)
   - **Database password**: Create a strong password and save it securely
   - **Region**: Select the region closest to you for better performance
3. Click "Create Project"

## Step 3: Wait for Project to Initialize

- Project creation may take 2-3 minutes
- You'll see a progress indicator
- Wait until the process is complete

## Step 4: Get Your API Credentials

1. Once your project is ready, go to "Project Settings" (gear icon)
2. Click on "API" in the left sidebar
3. Copy the following information:
   - **Project URL**: The URL at the top (starts with `https://`)
   - **anon key**: The long string under "Project API keys" (this is your SUPABASE_KEY)

## Step 5: Update Your Environment Variables

1. Open the `.env` file in the `backend` directory
2. Replace the placeholder values with your actual credentials:
   ```
   SUPABASE_URL=your_actual_project_url_here
   SUPABASE_KEY=your_actual_api_key_here
   ```

## Step 6: Test the Connection

1. Run the test script to verify the connection:
   ```bash
   cd backend
   python test_supabase.py
   ```

## Step 7: Create Database Tables

1. Go to the "SQL Editor" in your Supabase dashboard
2. Copy the contents of `supabase_schema.sql`
3. Paste it into the editor
4. Click "Run" to execute the schema

## Troubleshooting

### Common Issues

1. **Connection Failed**: 
   - Double-check your SUPABASE_URL and SUPABASE_KEY
   - Ensure there are no extra spaces or characters
   - Verify your internet connection

2. **Authentication Error**:
   - Make sure you're using the "anon" key, not the "service_role" key
   - Check that your project is not paused

3. **Schema Execution Error**:
   - Make sure you're copying the entire schema file
   - Check for any syntax errors in the SQL

### Need Help?

If you encounter any issues:
1. Check the Supabase documentation: [https://supabase.com/docs](https://supabase.com/docs)
2. Look at the error messages carefully
3. Verify all steps were completed correctly

Once you've completed these steps, update your PROGRESS_TRACKER.md file to mark the first task as complete!