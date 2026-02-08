#!/bin/bash

# Train ML Models Script
# Trains Decision Tree Classifier and Random Forest Regressor

set -e

echo "=========================================="
echo "Training ML Models"
echo "=========================================="
echo ""

echo "[1/2] Training ML models..."
python3 src/ml_models/train_models.py

echo ""
echo "[2/2] Verifying models..."
if [ -f "models/readiness_classifier.pkl" ] && [ -f "models/readiness_regressor.pkl" ]; then
    echo "✓ Models trained successfully!"
    echo "  - Classifier: models/readiness_classifier.pkl"
    echo "  - Regressor: models/readiness_regressor.pkl"
else
    echo "✗ Model training failed!"
    exit 1
fi

echo ""
echo "=========================================="
echo "ML Model Training Complete!"
echo "=========================================="

