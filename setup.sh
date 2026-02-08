#!/bin/bash

# University Placement Readiness Analytics System - Setup Script
# This script sets up the complete environment for the project

set -e  # Exit on error

echo "=========================================="
echo "University Placement Readiness Analytics"
echo "Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 is required but not installed. Aborting."; exit 1; }

# Install dependencies
echo ""
echo "Installing Python dependencies..."
# Try to install without version pin for psycopg2-binary to get latest compatible version
pip3 install psycopg2-binary SQLAlchemy==2.0.23 pandas==2.1.4 numpy==1.26.2 Faker==21.0.0 scikit-learn==1.3.2 joblib==1.3.2 streamlit==1.29.0 plotly==5.18.0 APScheduler==3.10.4 python-dotenv==1.0.0 pytest==7.4.3 jupyter==1.0.0 || {
    echo "⚠️  Some packages failed to install. Trying with requirements.txt..."
    pip3 install -r requirements.txt || echo "⚠️  Installation had issues. You may need to install packages manually."
}

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your PostgreSQL credentials!"
    echo ""
else
    echo ""
    echo "✓ .env file already exists"
fi

# Check if PostgreSQL is installed
echo ""
echo "Checking PostgreSQL installation..."
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL client (psql) found"
else
    echo "⚠️  PostgreSQL client not found. You may need to install PostgreSQL."
    echo "   macOS: brew install postgresql@14"
    echo "   Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    echo "   Or download from: https://www.postgresql.org/download/"
fi

# Check if PostgreSQL server is running
echo ""
echo "Checking if PostgreSQL server is running..."
if command -v pg_isready &> /dev/null; then
    if pg_isready -h localhost -p 5432 &> /dev/null; then
        echo "✓ PostgreSQL server is running"
        
        # Check PostgreSQL connection
        echo ""
        echo "Checking PostgreSQL connection..."
        python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from config.database import DATABASE_CONFIG
try:
    import psycopg2
    conn = psycopg2.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password'],
        database='postgres'  # Connect to default DB first
    )
    conn.close()
    print('✓ PostgreSQL connection successful!')
except ImportError:
    print('⚠️  psycopg2 not installed. Run: pip3 install psycopg2-binary')
except Exception as e:
    print(f'⚠️  PostgreSQL connection failed: {e}')
    print('   Please check your .env file credentials.')
" 2>/dev/null || echo "⚠️  Could not verify PostgreSQL connection"
    else
        echo "⚠️  PostgreSQL server is NOT running"
        echo ""
        echo "To start PostgreSQL:"
        echo "  macOS (Homebrew): brew services start postgresql@14"
        echo "  macOS (Postgres.app): Open Postgres.app"
        echo "  Linux: sudo systemctl start postgresql"
        echo "  Or: pg_ctl -D /usr/local/var/postgres start"
    fi
else
    echo "⚠️  pg_isready not found. Cannot check if PostgreSQL is running."
fi

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your PostgreSQL credentials"
echo "2. Create database: createdb placement_analytics"
echo "3. Initialize database: python src/database/init_db.py"
echo "4. Populate data: python src/data_generation/populate_db.py"
echo "5. Calculate scores: python src/core/scoring.py"
echo "6. Run dashboard: streamlit run src/dashboard/app.py"
echo ""

