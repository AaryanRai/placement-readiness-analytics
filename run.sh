#!/bin/bash

# University Placement Readiness Analytics System - Run Script
# Complete setup and run pipeline

set -e  # Exit on error

echo "=========================================="
echo "University Placement Readiness Analytics"
echo "Complete Setup & Run"
echo "=========================================="
echo ""

# Step 1: Initialize Database
echo "[1/4] Initializing database..."
python3 src/database/init_db.py
echo ""

# Step 2: Populate Data
echo "[2/4] Populating database with synthetic data..."
python3 src/data_generation/populate_db.py
echo ""

# Step 3: Calculate Scores
echo "[3/4] Calculating readiness scores..."
python3 src/core/scoring.py
echo ""

# Step 4: Train ML Models (baseline + advanced)
echo "[4/5] Training ML models (baseline + advanced)..."
python3 src/ml_models/train_models.py
echo ""

# Step 5: Start Dashboard
echo "[5/5] Starting Streamlit dashboard..."
echo ""
echo "✓ Dashboard will open in your browser"
echo "  Press Ctrl+C to stop the server"
echo ""
streamlit run src/dashboard/app.py

