# Supabase Authentication Test

This is a standalone test implementation for Supabase authentication to verify the flow works correctly before integrating with the main application.

## Authentication Methods

### 1. Traditional Authentication (Email/Password)
- Register with email and password
- Receive email confirmation link
- Login with email and password

### 2. Passwordless Authentication (Magic Links)
- Register with email only (no password)
- Receive magic link via email for confirmation
- Login by receiving magic link via email

## Setup

1. Create a Supabase project at https://supabase.com
2. Copy your project URL and anon key
3. Create a `.env` file with your credentials:

```
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
SECRET_KEY=your_flask_secret_key_here
```

## Running the Test

```bash
cd supabase_test
pip install -r requirements.txt
python app.py
```

Visit http://localhost:5005 in your browser to test the authentication flows.

## Authentication Flows

### Traditional Registration Flow
1. Visit `/register` 
2. Enter email, password, and confirm password
3. Click "Register"
4. Check email for confirmation link
5. Click confirmation link
6. Login with email and password

### Passwordless Registration Flow
1. Visit `/register/magic-link`
2. Enter email
3. Click "Send Magic Link"
4. Check email for magic link
5. Click magic link to confirm and log in

### Traditional Login Flow
1. Visit `/login`
2. Enter email and password
3. Click "Login"

### Passwordless Login Flow
1. Visit `/login/magic-link`
2. Enter email
3. Click "Send Magic Link"
4. Check email for magic link
5. Click magic link to log in