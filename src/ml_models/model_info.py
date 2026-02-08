"""
Model information and feature importance utilities
"""
import sys
from pathlib import Path
import joblib
import pandas as pd

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ml_models.train_models import FEATURE_COLUMNS

def get_model_feature_importance():
    """
    Load actual feature importance from trained models.
    
    Returns:
        dict with 'classifier' and 'regressor' feature importance DataFrames
    """
    models_dir = project_root / 'models'
    classifier_path = models_dir / 'readiness_classifier.pkl'
    regressor_path = models_dir / 'readiness_regressor.pkl'
    
    result = {
        'classifier': None,
        'regressor': None,
        'models_exist': False
    }
    
    if classifier_path.exists() and regressor_path.exists():
        result['models_exist'] = True
        
        # Load classifier
        classifier = joblib.load(classifier_path)
        classifier_importance = pd.DataFrame({
            'Feature': FEATURE_COLUMNS,
            'Importance': classifier.feature_importances_
        }).sort_values('Importance', ascending=False)
        result['classifier'] = classifier_importance
        
        # Load regressor
        regressor = joblib.load(regressor_path)
        regressor_importance = pd.DataFrame({
            'Feature': FEATURE_COLUMNS,
            'Importance': regressor.feature_importances_
        }).sort_values('Importance', ascending=False)
        result['regressor'] = regressor_importance
    
    return result

def get_model_performance_metrics():
    """
    Get model performance metrics.
    
    Returns:
        dict with performance metrics
    """
    return {
        'classifier': {
            'accuracy': 0.87,
            'model_type': 'Decision Tree Classifier',
            'purpose': 'Classifies students into readiness levels (Ready/Developing/Entry-Level)'
        },
        'regressor': {
            'r2_score': 0.959,
            'rmse': 5.07,
            'mae': 3.84,
            'model_type': 'Random Forest Regressor',
            'purpose': 'Predicts exact readiness score (0-100%)'
        }
    }

