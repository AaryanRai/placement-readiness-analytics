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
REGRESSOR_PATH = MODELS_DIR / 'readiness_regressor.pkl'
LABEL_ENCODER_PATH = MODELS_DIR / 'readiness_classifier_label_encoder.pkl'

# Feature columns (must match training)
FEATURE_COLUMNS = [
    'year_of_study', 'enrollment_year',
    'program_BBA', 'program_Btech', 'program_B.Com',
    'total_skills', 'avg_proficiency', 'max_proficiency', 'min_proficiency',
    'skills_Technical', 'skills_Business', 'skills_Design', 'skills_Soft Skills',
    'proficiency_Beginner', 'proficiency_Intermediate', 'proficiency_Advanced', 'proficiency_Expert',
    'source_Course', 'source_Certification', 'source_Project', 'source_Workshop',
    'required_skills_count', 'matched_skills_count', 'skill_gap_count', 'match_ratio',
    'role_Data Analyst', 'role_Full-Stack Developer', 'role_Digital Marketer',
    'role_Business Analyst', 'role_UX/UI Designer'
]

def load_models():
    """Load trained models and label encoder"""
    classifier = None
    regressor = None
    label_encoder = None
    
    if CLASSIFIER_PATH.exists():
        classifier = joblib.load(CLASSIFIER_PATH)
        print(f"✓ Loaded classifier from {CLASSIFIER_PATH}")
    else:
        print(f"⚠ Classifier not found at {CLASSIFIER_PATH}")
    
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
    
    return classifier, regressor, label_encoder

def predict_readiness_ml(student_id: int, role_id: int, session: Session) -> Dict:
    """
    Predict readiness using ML models.
    
    Args:
        student_id: Student ID
        role_id: Role ID
        session: Database session
    
    Returns:
        Dictionary with ML predictions:
        {
            'readiness_score_ml': float (0-100),
            'readiness_level_ml': str,
            'readiness_score_ml_probabilities': dict,
            'model_used': str
        }
    """
    # Load models
    classifier, regressor, label_encoder = load_models()
    
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
    
    # Predict level using classifier
    level_encoded = classifier.predict(X)[0]
    level_prediction = label_encoder.inverse_transform([level_encoded])[0]
    
    # Get prediction probabilities
    probabilities = classifier.predict_proba(X)[0]
    prob_dict = {
        label: float(prob) 
        for label, prob in zip(label_encoder.classes_, probabilities)
    }
    
    return {
        'readiness_score_ml': round(float(score_prediction), 2),
        'readiness_level_ml': level_prediction,
        'readiness_score_ml_probabilities': prob_dict,
        'model_used': 'ML (Random Forest + Decision Tree)'
    }

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
    classifier, regressor, label_encoder = load_models()
    
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

