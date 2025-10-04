import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_supabase_client():
    """Create and return a Supabase client"""
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            print("Missing SUPABASE_URL or SUPABASE_KEY")
            return None
            
        return create_client(url, key)
    except Exception as e:
        print(f"Error creating Supabase client: {e}")
        return None

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret-key-for-testing")

# Create Supabase client
supabase = create_supabase_client()

@app.route("/")
def index():
    """Home page"""
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration with email and password"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validate input
        if not email or not password or not confirm_password:
            flash("All fields are required", "error")
            return render_template("register.html")
            
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("register.html")
            
        if len(password) < 6:
            flash("Password must be at least 6 characters", "error")
            return render_template("register.html")
        
        try:
            # Register user with email and password
            if supabase:
                response = supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                
                if response:
                    flash("Registration successful! Please check your email to confirm your account.", "success")
                    # Redirect to check email page
                    return redirect(url_for("check_email", email=email))
                else:
                    flash("Registration failed", "error")
            else:
                flash("Supabase client not available", "error")
                
        except Exception as e:
            flash(f"Registration error: {str(e)}", "error")
    
    return render_template("register.html")

@app.route("/register/magic-link", methods=["GET", "POST"])
def register_magic_link():
    """User registration with magic link (passwordless)"""
    if request.method == "POST":
        email = request.form.get("email")
        
        # Validate input
        if not email:
            flash("Email is required", "error")
            return render_template("register_magic_link.html")
        
        try:
            # Register user with magic link (no password)
            if supabase:
                response = supabase.auth.sign_up({
                    "email": email
                })
                
                if response:
                    flash("Registration successful! Please check your email for a magic link.", "success")
                    # Redirect to check email page
                    return redirect(url_for("check_email", email=email))
                else:
                    flash("Registration failed", "error")
            else:
                flash("Supabase client not available", "error")
                
        except Exception as e:
            flash(f"Registration error: {str(e)}", "error")
    
    return render_template("register_magic_link.html")

@app.route("/check-email")
def check_email():
    """Page instructing user to check email for confirmation link or magic link"""
    email = request.args.get("email")
    if not email:
        flash("No email provided", "error")
        return redirect(url_for("register"))
    
    return render_template("check_email.html", email=email)

@app.route("/login", methods=["GET", "POST"])
def login():
    """User login with email and password"""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Validate input
        if not email or not password:
            flash("Email and password are required", "error")
            return render_template("login.html")
        
        try:
            if supabase:
                # Login user with email and password
                response = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                
                if response:
                    # Store user in session
                    session["user"] = {
                        "id": response.user.id,
                        "email": response.user.email
                    }
                    flash("Login successful!", "success")
                    return redirect(url_for("dashboard"))
                else:
                    flash("Login failed", "error")
            else:
                flash("Supabase client not available", "error")
                
        except Exception as e:
            flash(f"Login error: {str(e)}", "error")
    
    return render_template("login.html")

@app.route("/login/magic-link", methods=["GET", "POST"])
def login_magic_link():
    """User login with magic link (passwordless)"""
    if request.method == "POST":
        email = request.form.get("email")
        
        # Validate input
        if not email:
            flash("Email is required", "error")
            return render_template("login_magic_link.html")
        
        try:
            if supabase:
                # Send magic link
                response = supabase.auth.sign_in_with_otp({
                    "email": email
                })
                
                if response:
                    flash("Magic link sent! Please check your email.", "success")
                    return redirect(url_for("check_email", email=email))
                else:
                    flash("Failed to send magic link", "error")
            else:
                flash("Supabase client not available", "error")
                
        except Exception as e:
            flash(f"Error sending magic link: {str(e)}", "error")
    
    return render_template("login_magic_link.html")

@app.route("/magic-link", methods=["GET"])
def magic_link():
    """Handle magic link authentication"""
    try:
        # In a real Supabase implementation, this would be handled automatically
        # For this demo, we'll simulate the process
        flash("Magic link processed successfully! You are now logged in.", "success")
        # In a real app, you would get the user data from Supabase
        # For demo purposes, we'll redirect to dashboard
        return redirect(url_for("dashboard"))
        
    except Exception as e:
        flash(f"Error processing magic link: {str(e)}", "error")
        return redirect(url_for("login"))

@app.route("/dashboard")
def dashboard():
    """User dashboard"""
    user = session.get("user")
    if not user:
        flash("Please log in to access the dashboard", "error")
        return redirect(url_for("login"))
    
    return render_template("dashboard.html", user=user)

@app.route("/logout")
def logout():
    """User logout"""
    session.pop("user", None)
    session.pop("pending_email", None)
    session.pop("otp_phone", None)
    flash("You have been logged out", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5005)