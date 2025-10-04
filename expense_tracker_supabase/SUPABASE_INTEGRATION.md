# Supabase Integration for Expense Tracker

This document explains how to set up and use Supabase authentication in the Expense Tracker application.

## Setup Instructions

### 1. Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com) and create an account
2. Create a new project
3. Note down your project URL and anon key from the project settings

### 2. Configure Environment Variables

Update the `.env` file in the backend directory with your Supabase credentials:

```env
# Supabase Configuration
SUPABASE_URL=your_actual_supabase_project_url_here
SUPABASE_KEY=your_actual_supabase_anon_key_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
```

### 3. Enable Authentication Methods

In your Supabase project dashboard:

1. Go to Authentication > Settings
2. Enable Email signup
3. Enable Phone signup (for OTP functionality)

### 4. Database Schema

The Supabase integration uses Supabase's built-in auth system, so no additional database setup is required for user management.

## Available Authentication Routes

The following routes are available for authentication:

- `GET /auth/supabase/register` - Registration page
- `POST /auth/supabase/register` - Handle registration
- `GET /auth/supabase/registration-otp` - Combined OTP page for registration
- `POST /auth/supabase/registration-otp` - Handle OTP actions for registration
- `GET /auth/supabase/post-registration-options` - Post-registration options
- `GET /auth/supabase/register/verify-email` - Email verification instructions
- `GET /auth/supabase/register/use-otp` - Use OTP for new registration
- `POST /auth/supabase/register/use-otp` - Handle sending OTP for new registration
- `GET /auth/supabase/login` - Login page
- `POST /auth/supabase/login` - Handle login
- `GET /auth/supabase/logout` - Logout
- `GET /auth/supabase/send-otp` - Send OTP page
- `POST /auth/supabase/send-otp` - Handle sending OTP
- `GET /auth/supabase/verify-otp` - Verify OTP page
- `POST /auth/supabase/verify-otp` - Handle OTP verification
- `GET /auth/supabase/profile` - User profile page

## Features

### Email/Password Authentication
- User registration with email verification
- Secure password storage
- Login/logout functionality

### Phone OTP Authentication
- Send OTP to phone number
- Verify OTP for authentication
- Phone number storage
- Combined send/verify page for streamlined registration

## Authentication Flow

### Registration Flow
1. User registers with email/password
2. User is automatically redirected to the OTP verification page
3. User enters phone number and clicks "Send Verification Code"
4. User receives SMS with OTP code
5. User enters code and clicks "Verify Code"
6. User is logged in and redirected to dashboard

### Login Flow
1. User enters email/password
2. System authenticates credentials
3. User is logged in and redirected to dashboard

### OTP Flow (for existing users)
1. User navigates to OTP login
2. User enters phone number
3. User receives SMS with OTP code
4. User enters code to log in

## API Endpoints

### Current User
- `GET /api/current-user` - Returns current user information

## Implementation Details

The integration uses:
- Supabase Auth for user management
- Session storage for maintaining login state
- Bootstrap 5 for UI components
- Flask for routing and templating

## Security Considerations

1. Always use HTTPS in production
2. Store sensitive credentials in environment variables
3. Supabase handles password hashing automatically
4. Email verification is enabled by default

## Troubleshooting

### Common Issues

1. **Invalid URL error**: Check that your SUPABASE_URL is correctly formatted
2. **Authentication failed**: Verify your credentials in the .env file
3. **OTP not sending**: Ensure phone signup is enabled in Supabase settings

### Testing

Run the test script to verify integration:
```bash
cd expense_tracker/backend
python3 test_supabase.py
```

## Future Enhancements

Possible improvements:
- Social login (Google, Facebook, etc.)
- Password reset functionality
- Email verification enforcement
- Role-based access control
- Multi-factor authentication