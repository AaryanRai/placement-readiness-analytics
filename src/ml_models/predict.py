"""
ML Model Prediction Functions
Use trained models to predict readiness scores and levels
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import joblib
import pandas as pd
import numpy as np
from typing import Dict, Optional
from sqlalchemy.orm import Session

from src.ml_models.feature_extraction import extract_features_for_prediction

# Model paths
MODELS_DIR = project_root / 'models'
CLASSIFIER_PATH = MODELS_DIR / 'readiness_classifier.pkl'
GB_CLASSIFIER_PATH = MODELS_DIR / 'readiness_gradient_boosting.pkl'
REGRESSOR_PATH = MODELS_DIR / 'readiness_regressor.pkl'
LABEL_ENCODER_PATH = MODELS_DIR / 'readiness_classifier_label_encoder.pkl'
BASELINE_LOGREG_PATH = MODELS_DIR / "baseline_logistic_regression.pkl"
BASELINE_LOGREG_LABEL_ENCODER_PATH = MODELS_DIR / "baseline_logistic_regression_label_encoder.pkl"
BASELINE_RIDGE_PATH = MODELS_DIR / "baseline_ridge_regression.pkl"

# Feature columns (must match training)
# NOTE: Keep in sync with FEATURE_COLUMNS in train_models.py
FEATURE_COLUMNS = [
    'year_of_study', 'enrollment_year',
    'program_BBA', 'program_Btech', 'program_B.Com',
    'total_skills', 'avg_proficiency', 'max_proficiency', 'min_proficiency',
    'skills_Technical', 'skills_Business', 'skills_Design', 'skills_Soft Skills',
    'proficiency_Beginner', 'proficiency_Intermediate', 'proficiency_Advanced', 'proficiency_Expert',
    'source_Course', 'source_Certification', 'source_Project', 'source_Workshop',
    'required_skills_count', 'matched_skills_count', 'skill_gap_count',
    'role_Data Analyst', 'role_Full-Stack Developer', 'role_Digital Marketer',
    'role_Business Analyst', 'role_UX/UI Designer'
]

def load_models():
    """Load trained models and label encoder"""
    classifier = None
    gb_classifier = None
    regressor = None
    label_encoder = None
    baseline_logreg = None
    baseline_logreg_le = None
    baseline_ridge = None
    
    if CLASSIFIER_PATH.exists():
        classifier = joblib.load(CLASSIFIER_PATH)
        print(f"✓ Loaded Decision Tree classifier from {CLASSIFIER_PATH}")
    else:
        print(f"⚠ Decision Tree classifier not found at {CLASSIFIER_PATH}")
    
    if GB_CLASSIFIER_PATH.exists():
        gb_classifier = joblib.load(GB_CLASSIFIER_PATH)
        print(f"✓ Loaded Gradient Boosting classifier from {GB_CLASSIFIER_PATH}")
    else:
        print(f"⚠ Gradient Boosting classifier not found at {GB_CLASSIFIER_PATH}")
    
    if REGRESSOR_PATH.exists():
        regressor = joblib.load(REGRESSOR_PATH)
        print(f"✓ Loaded regressor from {REGRESSOR_PATH}")
    else:
        print(f"⚠ Regressor not found at {REGRESSOR_PATH}")
    
    if LABEL_ENCODER_PATH.exists():
        label_encoder = joblib.load(LABEL_ENCODER_PATH)
        print(f"✓ Loaded label encoder from {LABEL_ENCODER_PATH}")
    else:
        print(f"⚠ Label encoder not found at {LABEL_ENCODER_PATH}")

    if BASELINE_LOGREG_PATH.exists():
        baseline_logreg = joblib.load(BASELINE_LOGREG_PATH)
        print(f"✓ Loaded baseline Logistic Regression from {BASELINE_LOGREG_PATH}")
    else:
        print(f"⚠ Baseline Logistic Regression not found at {BASELINE_LOGREG_PATH}")

    if BASELINE_LOGREG_LABEL_ENCODER_PATH.exists():
        baseline_logreg_le = joblib.load(BASELINE_LOGREG_LABEL_ENCODER_PATH)
        print(f"✓ Loaded baseline label encoder from {BASELINE_LOGREG_LABEL_ENCODER_PATH}")
    else:
        print(f"⚠ Baseline label encoder not found at {BASELINE_LOGREG_LABEL_ENCODER_PATH}")

    if BASELINE_RIDGE_PATH.exists():
        baseline_ridge = joblib.load(BASELINE_RIDGE_PATH)
        print(f"✓ Loaded baseline Ridge Regression from {BASELINE_RIDGE_PATH}")
    else:
        print(f"⚠ Baseline Ridge Regression not found at {BASELINE_RIDGE_PATH}")
    
    return (
        classifier,
        gb_classifier,
        regressor,
        label_encoder,
        baseline_logreg,
        baseline_logreg_le,
        baseline_ridge,
    )

def predict_readiness_ml(student_id: int, role_id: int, session: Session) -> Dict:
    """
    Predict readiness using ML models (all 3 models).
    
    Args:
        student_id: Student ID
        role_id: Role ID
        session: Database session
    
    Returns:
        Dictionary with ML predictions from all models:
        {
            'readiness_score_ml': float (0-100),
            'readiness_level_ml': str,
            'readiness_score_ml_probabilities': dict,
            'model_used': str,
            'decision_tree': dict,
            'gradient_boosting': dict,
            'random_forest': dict
        }
    """
    # Load models
    (
        classifier,
        gb_classifier,
        regressor,
        label_encoder,
        baseline_logreg,
        baseline_logreg_le,
        baseline_ridge,
    ) = load_models()
    
    if classifier is None or regressor is None:
        return {
            'readiness_score_ml': None,
            'readiness_level_ml': None,
            'readiness_score_ml_probabilities': None,
            'model_used': None,
            'error': 'Models not trained. Please run train_models.py first.'
        }
    
    # Extract features
    try:
        features_df = extract_features_for_prediction(student_id, role_id, session)
    except Exception as e:
        return {
            'readiness_score_ml': None,
            'readiness_level_ml': None,
            'readiness_score_ml_probabilities': None,
            'model_used': None,
            'error': str(e)
        }
    
    # Ensure all feature columns are present
    for col in FEATURE_COLUMNS:
        if col not in features_df.columns:
            features_df[col] = 0
    
    X = features_df[FEATURE_COLUMNS]
    
    # Predict score using regressor
    score_prediction = regressor.predict(X)[0]
    score_prediction = max(0, min(100, score_prediction))  # Clamp to 0-100
    
    # Predict level using Decision Tree classifier (primary)
    level_encoded = classifier.predict(X)[0]
    level_prediction = label_encoder.inverse_transform([level_encoded])[0]
    
    # Get prediction probabilities from Decision Tree
    probabilities = classifier.predict_proba(X)[0]
    prob_dict = {
        label: float(prob) 
        for label, prob in zip(label_encoder.classes_, probabilities)
    }
    
    # Get predictions from all models
    result = {
        'readiness_score_ml': round(float(score_prediction), 2),
        'readiness_level_ml': level_prediction,
        'readiness_score_ml_probabilities': prob_dict,
        'model_used': 'ML (Random Forest + Decision Tree + Gradient Boosting)',
        'decision_tree': {
            'level': level_prediction,
            'probabilities': prob_dict
        },
        'random_forest': {
            'score': round(float(score_prediction), 2)
        }
    }
    
    # Add Gradient Boosting predictions if available
    if gb_classifier is not None:
        gb_level_encoded = gb_classifier.predict(X)[0]
        gb_level = label_encoder.inverse_transform([gb_level_encoded])[0]
        gb_probs = gb_classifier.predict_proba(X)[0]
        gb_prob_dict = {
            label: float(prob) 
            for label, prob in zip(label_encoder.classes_, gb_probs)
        }
        result['gradient_boosting'] = {
            'level': gb_level,
            'probabilities': gb_prob_dict
        }

    # Add baseline predictions if available (preprocessed pipelines stored in artifact dicts)
    if baseline_logreg is not None and baseline_logreg_le is not None:
        try:
            bl_model = baseline_logreg["model"]
            bl_pre = baseline_logreg["preprocessor"]
            X_bl = bl_pre.transform(X)
            bl_level_encoded = bl_model.predict(X_bl)[0]
            bl_level = baseline_logreg_le.inverse_transform([bl_level_encoded])[0]
            bl_probs = bl_model.predict_proba(X_bl)[0]
            bl_prob_dict = {
                label: float(prob)
                for label, prob in zip(baseline_logreg_le.classes_, bl_probs)
            }
            result["baseline_logistic_regression"] = {
                "level": bl_level,
                "probabilities": bl_prob_dict,
            }
        except Exception as e:
            result["baseline_logistic_regression"] = {"error": str(e)}

    if baseline_ridge is not None:
        try:
            bl_model = baseline_ridge["model"]
            bl_pre = baseline_ridge["preprocessor"]
            X_bl = bl_pre.transform(X)
            bl_score = float(bl_model.predict(X_bl)[0])
            bl_score = max(0.0, min(100.0, bl_score))
            result["baseline_ridge_regression"] = {"score": round(bl_score, 2)}
        except Exception as e:
            result["baseline_ridge_regression"] = {"error": str(e)}
    
    return result

def predict_batch_ml(session: Session, student_ids: Optional[list] = None, role_ids: Optional[list] = None) -> pd.DataFrame:
    """
    Predict readiness for multiple student-role combinations using ML.
    
    Args:
        session: Database session
        student_ids: List of student IDs (None = all students)
        role_ids: List of role IDs (None = all roles)
    
    Returns:
        DataFrame with predictions
    """
    from src.database.models import Student, JobRole, MarketReadinessScores
    
    # Load models
    (
        classifier,
        gb_classifier,
        regressor,
        label_encoder,
        baseline_logreg,
        baseline_logreg_le,
        baseline_ridge,
    ) = load_models()
    
    if classifier is None or regressor is None:
        print("ERROR: Models not trained. Please run train_models.py first.")
        return pd.DataFrame()
    
    # Get all student-role combinations
    query = session.query(
        MarketReadinessScores.student_id,
        MarketReadinessScores.role_id
    )
    
    if student_ids:
        query = query.filter(MarketReadinessScores.student_id.in_(student_ids))
    if role_ids:
        query = query.filter(MarketReadinessScores.role_id.in_(role_ids))
    
    combinations = query.distinct().all()
    
    predictions = []
    
    for student_id, role_id in combinations:
        try:
            # Extract features
            features_df = extract_features_for_prediction(student_id, role_id, session)
            
            # Ensure all feature columns are present
            for col in FEATURE_COLUMNS:
                if col not in features_df.columns:
                    features_df[col] = 0
            
            X = features_df[FEATURE_COLUMNS]
            
            # Predict
            score_pred = regressor.predict(X)[0]
            score_pred = max(0, min(100, score_pred))
            
            level_encoded = classifier.predict(X)[0]
            level_pred = label_encoder.inverse_transform([level_encoded])[0]
            
            predictions.append({
                'student_id': student_id,
                'role_id': role_id,
                'readiness_score_ml': round(float(score_pred), 2),
                'readiness_level_ml': level_pred
            })
        except Exception as e:
            print(f"Error predicting for student {student_id}, role {role_id}: {e}")
            continue
    
    return pd.DataFrame(predictions)

