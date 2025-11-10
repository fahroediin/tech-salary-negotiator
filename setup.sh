#!/bin/bash

# Tech Salary Negotiator Setup Script
echo "🚀 Setting up Tech Salary Negotiator..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 16+"
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is required but not installed. Please install PostgreSQL"
    exit 1
fi

echo "✅ All required tools are installed"

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Setup environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before running the application"
fi

# Setup database
echo "🗄️  Setting up database..."
read -p "Enter PostgreSQL database name (default: salary_negotiation): " db_name
db_name=${db_name:-salary_negotiation}

read -p "Enter PostgreSQL user (default: postgres): " db_user
db_user=${db_user:-postgres}

read -s -p "Enter PostgreSQL password: " db_pass
echo

# Create database
createdb $db_name 2>/dev/null || echo "Database already exists"

# Update DATABASE_URL in .env
sed -i "s|postgresql://user:password@localhost:5432/dbname|postgresql://$db_user:$db_pass@localhost:5432/$db_name|" .env

# Initialize database tables
echo "🏗️  Initializing database tables..."
python init_db.py

# Setup frontend
echo "🎨 Setting up frontend..."
cd frontend

# Install Node.js dependencies
npm install

echo "✅ Setup complete!"
echo ""
echo "🎉 Next steps:"
echo "1. Edit .env file with your Gemini API key"
echo "2. Start backend: cd .. && python main.py"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "📚 For more information, see README.md"