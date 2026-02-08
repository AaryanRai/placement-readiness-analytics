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
pip3 install -r requirements.txt

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

# Check PostgreSQL connection
echo ""
echo "Checking PostgreSQL connection..."
python3 -c "
from config.database import DATABASE_CONFIG
import psycopg2
try:
    conn = psycopg2.connect(
        host=DATABASE_CONFIG['host'],
        port=DATABASE_CONFIG['port'],
        user=DATABASE_CONFIG['user'],
        password=DATABASE_CONFIG['password'],
        database='postgres'  # Connect to default DB first
    )
    conn.close()
    print('✓ PostgreSQL connection successful!')
except Exception as e:
    print(f'⚠️  PostgreSQL connection failed: {e}')
    print('Please ensure PostgreSQL is running and credentials in .env are correct.')
" || echo "⚠️  Could not verify PostgreSQL connection"

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

