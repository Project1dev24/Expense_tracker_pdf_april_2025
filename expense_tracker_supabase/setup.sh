#!/bin/bash

# Setup script for Expense Tracker with Supabase

echo "🚀 Setting up Expense Tracker with Supabase..."

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 is not installed. Please install Python3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null
then
    echo "❌ pip3 is not installed. Please install pip3 and try again."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
cd backend
pip3 install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file template..."
    cat > .env << EOF
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_service_role_key_here

# Flask Configuration
SECRET_KEY=your_random_secret_key_here

# Application Configuration
FLASK_APP=app.py
FLASK_DEBUG=True
EOF
    echo "✅ Created .env template. Please update it with your Supabase credentials."
else
    echo "✅ .env file already exists."
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your Supabase credentials"
echo "2. Apply database schema:"
echo "   cd ../supabase"
echo "   supabase link --project-ref YOUR_PROJECT_ID"
echo "   supabase db push"
echo "3. Run the application:"
echo "   cd ../backend"
echo "   python3 app.py"