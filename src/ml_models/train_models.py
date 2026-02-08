"""
Train ML models for readiness prediction
- Decision Tree Classifier: Predicts readiness level (Ready/Developing/Entry-Level)
- Random Forest Regressor: Predicts readiness score (0-100)
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
import joblib
import os

from src.ml_models.feature_extraction import extract_features_for_training
from src.database.connection import get_db_session

# Feature columns (excluding target variables)
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

def train_classifier(df: pd.DataFrame, save_path: str = None) -> DecisionTreeClassifier:
    """
    Train Decision Tree Classifier for readiness level prediction.
    
    Args:
        df: DataFrame with features and 'readiness_level' target
        save_path: Path to save the trained model
    
    Returns:
        Trained DecisionTreeClassifier
    """
    print("\n" + "="*60)
    print("Training Decision Tree Classifier")
    print("="*60)
    
    # Prepare features and target
    X = df[FEATURE_COLUMNS].copy()
    y = df['readiness_level'].copy()
    
    # Encode target labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    # Train model with anti-overfitting parameters
    model = DecisionTreeClassifier(
        max_depth=8,  # Reduced to prevent overfitting
        min_samples_split=30,  # Increased to require more samples for splits
        min_samples_leaf=15,  # Increased to prevent leaf nodes with few samples
        max_features='sqrt',  # Use sqrt of features to reduce overfitting
        random_state=None,  # Use system time for variability
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\nModel Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': FEATURE_COLUMNS,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    print(feature_importance.head(10).to_string(index=False))
    
    # Save model and label encoder
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        joblib.dump(model, save_path)
        joblib.dump(le, save_path.replace('.pkl', '_label_encoder.pkl'))
        print(f"\n✓ Model saved to: {save_path}")
        print(f"✓ Label encoder saved to: {save_path.replace('.pkl', '_label_encoder.pkl')}")
    
    return model, le

def train_regressor(df: pd.DataFrame, save_path: str = None) -> RandomForestRegressor:
    """
    Train Random Forest Regressor for readiness score prediction.
    
    Args:
        df: DataFrame with features and 'readiness_score' target
        save_path: Path to save the trained model
    
    Returns:
        Trained RandomForestRegressor
    """
    print("\n" + "="*60)
    print("Training Random Forest Regressor")
    print("="*60)
    
    # Prepare features and target
    X = df[FEATURE_COLUMNS].copy()
    y = df['readiness_score'].copy()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    # Train model with anti-overfitting parameters
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,  # Reduced to prevent overfitting
        min_samples_split=20,  # Increased to require more samples
        min_samples_leaf=10,  # Increased to prevent overfitting
        max_features='sqrt',  # Use sqrt of features (default is 'auto' which is sqrt)
        max_samples=0.8,  # Use 80% of samples per tree (bootstrap)
        random_state=None,  # Use system time for variability
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\nModel Performance:")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  R² Score: {r2:.4f} ({r2*100:.2f}%)")
    print(f"  Mean Absolute Error: {np.mean(np.abs(y_test - y_pred)):.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': FEATURE_COLUMNS,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nTop 10 Most Important Features:")
    print(feature_importance.head(10).to_string(index=False))
    
    # Save model
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        joblib.dump(model, save_path)
        print(f"\n✓ Model saved to: {save_path}")
    
    return model

def main():
    """Main training function"""
    print("="*60)
    print("ML Model Training Pipeline")
    print("="*60)
    
    # Extract features
    print("\n[1/3] Extracting features from database...")
    session = get_db_session()
    try:
        df = extract_features_for_training(session)
        print(f"✓ Extracted {len(df)} samples with {len(df.columns)} features")
    finally:
        session.close()
    
    if len(df) == 0:
        print("ERROR: No data found. Please populate the database first.")
        return
    
    # Check for required columns
    missing_cols = set(FEATURE_COLUMNS) - set(df.columns)
    if missing_cols:
        print(f"WARNING: Missing feature columns: {missing_cols}")
    
    # Train models
    print("\n[2/3] Training models...")
    
    # Create models directory
    models_dir = project_root / 'models'
    models_dir.mkdir(exist_ok=True)
    
    # Train classifier
    classifier_path = models_dir / 'readiness_classifier.pkl'
    classifier, label_encoder = train_classifier(df, str(classifier_path))
    
    # Train regressor
    regressor_path = models_dir / 'readiness_regressor.pkl'
    regressor = train_regressor(df, str(regressor_path))
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f"\nModels saved in: {models_dir}")
    print(f"  - Classifier: {classifier_path.name}")
    print(f"  - Regressor: {regressor_path.name}")
    print(f"  - Label Encoder: {classifier_path.name.replace('.pkl', '_label_encoder.pkl')}")

if __name__ == "__main__":
    main()

