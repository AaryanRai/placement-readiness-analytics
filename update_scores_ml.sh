#!/bin/bash

# Update Scores with ML Predictions Script

set -e

echo "=========================================="
echo "Updating Scores with ML Predictions"
echo "=========================================="
echo ""

# Check if models exist
if [ ! -f "models/readiness_classifier.pkl" ] || [ ! -f "models/readiness_regressor.pkl" ]; then
    echo "ERROR: ML models not found!"
    echo "Please run: ./train_ml_models.sh first"
    exit 1
fi

echo "[1/1] Calculating ML-based readiness scores..."
python3 src/core/scoring_ml.py

echo ""
echo "=========================================="
echo "ML Scores Updated Successfully!"
echo "=========================================="

