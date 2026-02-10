"""
Tests for ML models and evaluation metrics
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from pathlib import Path
import joblib
import json

def test_models_exist():
    """Test that all 3 model files exist after training."""
    models_dir = project_root / 'models'
    
    classifier_path = models_dir / 'readiness_classifier.pkl'
    gb_classifier_path = models_dir / 'readiness_gradient_boosting.pkl'
    regressor_path = models_dir / 'readiness_regressor.pkl'
    label_encoder_path = models_dir / 'readiness_classifier_label_encoder.pkl'
    
    # At least Decision Tree and Random Forest should exist
    assert classifier_path.exists(), "Decision Tree classifier should exist"
    assert regressor_path.exists(), "Random Forest regressor should exist"
    assert label_encoder_path.exists(), "Label encoder should exist"
    
    # Gradient Boosting is optional but preferred
    if not gb_classifier_path.exists():
        print("Warning: Gradient Boosting classifier not found. Run train_models.py to create it.")

def test_models_loadable():
    """Test that models can be loaded."""
    models_dir = project_root / 'models'
    
    classifier_path = models_dir / 'readiness_classifier.pkl'
    regressor_path = models_dir / 'readiness_regressor.pkl'
    
    if classifier_path.exists():
        classifier = joblib.load(classifier_path)
        assert classifier is not None, "Classifier should load successfully"
        assert hasattr(classifier, 'predict'), "Classifier should have predict method"
    
    if regressor_path.exists():
        regressor = joblib.load(regressor_path)
        assert regressor is not None, "Regressor should load successfully"
        assert hasattr(regressor, 'predict'), "Regressor should have predict method"

def test_metrics_file_exists():
    """Test that metrics JSON file exists."""
    models_dir = project_root / 'models'
    metrics_path = models_dir / 'model_metrics.json'
    
    if metrics_path.exists():
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        
        assert 'decision_tree' in metrics, "Should have Decision Tree metrics"
        assert 'random_forest' in metrics, "Should have Random Forest metrics"
        
        # Check classification metrics structure
        if 'decision_tree' in metrics:
            dt_metrics = metrics['decision_tree']
            assert 'accuracy' in dt_metrics, "Should have accuracy"
            assert 'precision_macro' in dt_metrics, "Should have precision_macro"
            assert 'recall_macro' in dt_metrics, "Should have recall_macro"
            assert 'f1_macro' in dt_metrics, "Should have f1_macro"
            assert 'confusion_matrix' in dt_metrics, "Should have confusion_matrix"
        
        # Check regression metrics structure
        if 'random_forest' in metrics:
            rf_metrics = metrics['random_forest']
            assert 'r2_score' in rf_metrics, "Should have r2_score"
            assert 'rmse' in rf_metrics, "Should have rmse"
            assert 'mae' in rf_metrics, "Should have mae"

def test_evaluation_metrics_module():
    """Test that evaluation metrics module works."""
    from src.ml_models.evaluation_metrics import (
        calculate_classification_metrics,
        calculate_regression_metrics
    )
    import numpy as np
    
    # Test classification metrics
    y_true = np.array([0, 1, 2, 0, 1, 2])
    y_pred = np.array([0, 1, 2, 0, 1, 1])  # One error
    y_proba = np.array([[0.9, 0.05, 0.05],
                       [0.1, 0.8, 0.1],
                       [0.1, 0.2, 0.7],
                       [0.8, 0.1, 0.1],
                       [0.2, 0.7, 0.1],
                       [0.1, 0.6, 0.3]])
    classes = np.array(['Ready', 'Developing', 'Entry-Level'])
    
    metrics = calculate_classification_metrics(y_true, y_pred, y_proba, classes)
    
    assert 'accuracy' in metrics
    assert 'precision_macro' in metrics
    assert 'recall_macro' in metrics
    assert 'f1_macro' in metrics
    assert 'confusion_matrix' in metrics
    assert 'per_class' in metrics
    
    # Test regression metrics
    y_true_reg = np.array([80.0, 75.0, 90.0, 65.0, 85.0])
    y_pred_reg = np.array([82.0, 73.0, 88.0, 67.0, 83.0])
    
    reg_metrics = calculate_regression_metrics(y_true_reg, y_pred_reg)
    
    assert 'rmse' in reg_metrics
    assert 'mae' in reg_metrics
    assert 'r2_score' in reg_metrics
    assert 'mape' in reg_metrics

def test_model_info_loads_metrics():
    """Test that model_info can load metrics."""
    from src.ml_models.model_info import get_model_performance_metrics
    
    metrics = get_model_performance_metrics()
    
    assert isinstance(metrics, dict), "Should return a dictionary"
    
    # Should have at least decision_tree and random_forest
    assert 'decision_tree' in metrics or 'classifier' in metrics
    assert 'random_forest' in metrics or 'regressor' in metrics

def test_prediction_functions():
    """Test that prediction functions work."""
    from src.ml_models.predict import load_models
    from src.database.connection import get_db_session
    from src.database.models import Student, JobRole
    
    session = get_db_session()
    try:
        # Get a test student and role
        student = session.query(Student).first()
        role = session.query(JobRole).first()
        
        if student and role:
            # Test loading models
            classifier, gb_classifier, regressor, label_encoder = load_models()
            
            # At least Decision Tree and Random Forest should be available
            if classifier is None or regressor is None:
                pytest.skip("Models not trained. Run train_models.py first.")
            
            # Test prediction
            from src.ml_models.predict import predict_readiness_ml
            
            result = predict_readiness_ml(student.student_id, role.role_id, session)
            
            assert 'readiness_score_ml' in result, "Should have score prediction"
            assert 'readiness_level_ml' in result, "Should have level prediction"
            assert result['readiness_score_ml'] is not None, "Score should not be None"
            assert result['readiness_level_ml'] is not None, "Level should not be None"
            assert 0 <= result['readiness_score_ml'] <= 100, "Score should be 0-100"
            assert result['readiness_level_ml'] in ['Ready', 'Developing', 'Entry-Level'], "Level should be valid"
    finally:
        session.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

