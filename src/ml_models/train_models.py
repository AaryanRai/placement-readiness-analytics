"""
Train ML models for readiness prediction
- Decision Tree Classifier: Predicts readiness level (Ready/Developing/Entry-Level)
- Gradient Boosting Classifier: Predicts readiness level (Ready/Developing/Entry-Level)
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
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score, classification_report, mean_squared_error, r2_score,
    precision_score, recall_score, f1_score, confusion_matrix
)
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import json
from datetime import datetime

from src.ml_models.feature_extraction import extract_features_for_training
from src.database.connection import get_db_session
from src.preprocessing.preprocessor import (
    PreprocessSpec,
    build_preprocessor,
    group_train_test_split,
    validate_training_frame,
)
from src.preprocessing.data_quality import generate_quality_report
from src.ml_models.drift import build_drift_baseline_from_training_frame, save_drift_baseline

# Feature columns (excluding target variables)
# NOTE: We intentionally exclude 'match_ratio' to prevent it from becoming an
# overly dominant shortcut feature. Models instead learn from underlying
# portfolio and role features (required/matched/skill_gap).
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


def train_baseline_logistic_regression(
    df: pd.DataFrame,
    spec: PreprocessSpec,
    save_path: str | None = None,
):
    """Baseline classifier: Logistic Regression on preprocessed features."""
    print("\n" + "=" * 60)
    print("Training Baseline Logistic Regression (Readiness Level)")
    print("=" * 60)

    X_all = df[spec.feature_columns].copy()
    y_all = df["readiness_level"].copy()

    le = LabelEncoder()
    y_encoded = le.fit_transform(y_all)

    # Leakage-safe split by student
    train_df, test_df = group_train_test_split(df, group_col="student_id", test_size=0.2, random_state=42)
    X_train_raw = train_df[spec.feature_columns].copy()
    y_train = le.transform(train_df["readiness_level"].copy())
    X_test_raw = test_df[spec.feature_columns].copy()
    y_test = le.transform(test_df["readiness_level"].copy())

    pre = build_preprocessor(spec.feature_columns)
    X_train = pre.fit_transform(X_train_raw)
    X_test = pre.transform(X_test_raw)

    model = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        n_jobs=-1,
        solver="lbfgs",
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)
    acc = accuracy_score(y_test, y_pred)

    print(f"\nBaseline Accuracy: {acc:.4f} ({acc*100:.2f}%)")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        joblib.dump({"model": model, "preprocessor": pre}, save_path)
        joblib.dump(le, save_path.replace(".pkl", "_label_encoder.pkl"))
        print(f"\n✓ Baseline model saved to: {save_path}")

    return model, pre, le, y_test, y_pred, y_proba, le.classes_


def train_baseline_ridge_regression(
    df: pd.DataFrame,
    spec: PreprocessSpec,
    save_path: str | None = None,
):
    """Baseline regressor: Ridge Regression on preprocessed features."""
    print("\n" + "=" * 60)
    print("Training Baseline Ridge Regression (Readiness Score)")
    print("=" * 60)

    train_df, test_df = group_train_test_split(df, group_col="student_id", test_size=0.2, random_state=42)
    X_train_raw = train_df[spec.feature_columns].copy()
    y_train = train_df["readiness_score"].astype(float).copy()
    X_test_raw = test_df[spec.feature_columns].copy()
    y_test = test_df["readiness_score"].astype(float).copy()

    pre = build_preprocessor(spec.feature_columns)
    X_train = pre.fit_transform(X_train_raw)
    X_test = pre.transform(X_test_raw)

    model = Ridge(alpha=1.0, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    rmse = float(np.sqrt(mse))
    r2 = r2_score(y_test, y_pred)
    mae = float(np.mean(np.abs(y_test - y_pred)))

    print("\nBaseline Performance:")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  R² Score: {r2:.4f} ({r2*100:.2f}%)")
    print(f"  Mean Absolute Error: {mae:.4f}")

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        joblib.dump({"model": model, "preprocessor": pre}, save_path)
        print(f"\n✓ Baseline model saved to: {save_path}")

    return model, pre, y_test, y_pred

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
    
    return model, le, X_test, y_test, le.classes_

def train_gradient_boosting_classifier(df: pd.DataFrame, save_path: str = None, label_encoder: LabelEncoder = None):
    """
    Train Gradient Boosting Classifier for readiness level prediction.
    
    Args:
        df: DataFrame with features and 'readiness_level' target
        save_path: Path to save the trained model
        label_encoder: Pre-fitted label encoder (from Decision Tree training)
    
    Returns:
        Trained GradientBoostingClassifier, label encoder, test data, test labels, class names
    """
    print("\n" + "="*60)
    print("Training Gradient Boosting Classifier")
    print("="*60)
    
    # Prepare features and target
    X = df[FEATURE_COLUMNS].copy()
    y = df['readiness_level'].copy()
    
    # Use existing label encoder or create new one
    if label_encoder is None:
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
    else:
        le = label_encoder
        y_encoded = le.transform(y)
    
    # Split data (use same random_state for consistency)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")
    
    # Train model with anti-overfitting parameters
    model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,  # Shallow trees to prevent overfitting
        learning_rate=0.1,  # Moderate learning rate
        min_samples_split=20,  # Require more samples for splits
        min_samples_leaf=10,  # Prevent leaf nodes with few samples
        max_features='sqrt',  # Use sqrt of features
        random_state=None,  # Use system time for variability
        subsample=0.8  # Use 80% of samples per tree
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
    
    # Save model
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        joblib.dump(model, save_path)
        print(f"\n✓ Model saved to: {save_path}")
    
    return model, le, X_test, y_test, le.classes_

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
    
    return model, X_test, y_test

def calculate_comprehensive_metrics(y_true, y_pred, y_test_proba, classes, model_type='classification'):
    """
    Calculate comprehensive evaluation metrics.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_test_proba: Prediction probabilities (for classification)
        classes: Class names
        model_type: 'classification' or 'regression'
    
    Returns:
        Dictionary with all metrics
    """
    from src.ml_models.evaluation_metrics import calculate_classification_metrics, calculate_regression_metrics
    
    if model_type == 'classification':
        return calculate_classification_metrics(y_true, y_pred, y_test_proba, classes)
    else:
        return calculate_regression_metrics(y_true, y_pred)

def main():
    """Main training function"""
    print("="*60)
    print("ML Model Training Pipeline")
    print("="*60)
    
    # Extract features
    print("\n[1/4] Extracting features from database...")
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

    # Validate schema (includes student_id/role_id/targets)
    spec = PreprocessSpec(feature_columns=list(FEATURE_COLUMNS))
    validate_training_frame(df, spec)

    # Save a data quality report for the training frame
    quality = generate_quality_report(df, target_class_col="readiness_level")
    
    # Train models
    print("\n[2/4] Training models...")
    
    # Create models directory
    models_dir = project_root / 'models'
    models_dir.mkdir(exist_ok=True)

    # Save quality report
    quality_path = models_dir / "data_quality_report.json"
    with open(quality_path, "w") as f:
        json.dump(quality.to_dict(), f, indent=2)
    print(f"✓ Data quality report saved to: {quality_path}")

    # Baseline models (requested as remarks)
    baseline_clf_path = models_dir / "baseline_logistic_regression.pkl"
    baseline_reg_path = models_dir / "baseline_ridge_regression.pkl"

    bl_clf, bl_clf_pre, bl_le, bl_y_test, bl_y_pred, bl_y_proba, bl_classes = train_baseline_logistic_regression(
        df, spec, str(baseline_clf_path)
    )
    bl_reg, bl_reg_pre, bl_reg_y_test, bl_reg_y_pred = train_baseline_ridge_regression(
        df, spec, str(baseline_reg_path)
    )
    
    # Train Decision Tree Classifier
    classifier_path = models_dir / 'readiness_classifier.pkl'
    classifier, label_encoder, dt_X_test, dt_y_test, class_names = train_classifier(df, str(classifier_path))
    
    # Train Gradient Boosting Classifier
    gb_classifier_path = models_dir / 'readiness_gradient_boosting.pkl'
    gb_classifier, _, gb_X_test, gb_y_test, _ = train_gradient_boosting_classifier(
        df, str(gb_classifier_path), label_encoder
    )
    
    # Train Random Forest Regressor
    regressor_path = models_dir / 'readiness_regressor.pkl'
    regressor, rf_X_test, rf_y_test = train_regressor(df, str(regressor_path))
    
    # Calculate comprehensive metrics
    print("\n[3/4] Calculating comprehensive evaluation metrics...")
    metrics = {}

    # Baseline metrics
    metrics["baseline_logistic_regression"] = calculate_comprehensive_metrics(
        bl_y_test, bl_y_pred, bl_y_proba, bl_classes, "classification"
    )
    metrics["baseline_ridge_regression"] = calculate_comprehensive_metrics(
        bl_reg_y_test, bl_reg_y_pred, None, None, "regression"
    )
    
    # Decision Tree metrics
    dt_y_pred = classifier.predict(dt_X_test)
    dt_y_proba = classifier.predict_proba(dt_X_test)
    metrics['decision_tree'] = calculate_comprehensive_metrics(
        dt_y_test, dt_y_pred, dt_y_proba, class_names, 'classification'
    )
    
    # Gradient Boosting metrics
    gb_y_pred = gb_classifier.predict(gb_X_test)
    gb_y_proba = gb_classifier.predict_proba(gb_X_test)
    metrics['gradient_boosting'] = calculate_comprehensive_metrics(
        gb_y_test, gb_y_pred, gb_y_proba, class_names, 'classification'
    )
    
    # Random Forest metrics
    rf_y_pred = regressor.predict(rf_X_test)
    metrics['random_forest'] = calculate_comprehensive_metrics(
        rf_y_test, rf_y_pred, None, None, 'regression'
    )
    
    # Add metadata
    metrics['metadata'] = {
        'training_date': datetime.now().isoformat(),
        'total_samples': len(df),
        'training_samples': len(df) * 0.8,
        'test_samples': len(df) * 0.2,
        'feature_count': len(FEATURE_COLUMNS),
        'split_strategy': 'grouped_by_student_id',
        'artifacts': {
            'data_quality_report': str(quality_path),
            'baseline_logistic_regression': str(baseline_clf_path),
            'baseline_ridge_regression': str(baseline_reg_path),
        },
    }
    
    # Save metrics to JSON
    metrics_path = models_dir / 'model_metrics.json'
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"✓ Metrics saved to: {metrics_path}")

    # Save a baseline distribution snapshot for later data drift monitoring.
    # This supports a lightweight "is the model still behaving similarly?" check.
    try:
        baseline = build_drift_baseline_from_training_frame(df)
        baseline_path = save_drift_baseline(models_dir=models_dir, baseline=baseline)
        print(f"✓ Drift baseline saved to: {baseline_path}")
    except Exception as e:
        print(f"⚠ Could not build drift baseline: {e}")
    
    print("\n[4/4] Summary:")
    print(f"  Baseline Logistic Accuracy: {metrics['baseline_logistic_regression']['accuracy']:.4f}")
    print(f"  Baseline Ridge R²: {metrics['baseline_ridge_regression']['r2_score']:.4f}")
    print(f"  Decision Tree Accuracy: {metrics['decision_tree']['accuracy']:.4f}")
    print(f"  Gradient Boosting Accuracy: {metrics['gradient_boosting']['accuracy']:.4f}")
    print(f"  Random Forest R²: {metrics['random_forest']['r2_score']:.4f}")
    
    print("\n" + "="*60)
    print("Training Complete!")
    print("="*60)
    print(f"\nModels saved in: {models_dir}")
    print(f"  - Baseline Logistic Regression: {baseline_clf_path.name}")
    print(f"  - Baseline Ridge Regression: {baseline_reg_path.name}")
    print(f"  - Decision Tree Classifier: {classifier_path.name}")
    print(f"  - Gradient Boosting Classifier: {gb_classifier_path.name}")
    print(f"  - Random Forest Regressor: {regressor_path.name}")
    print(f"  - Label Encoder: {classifier_path.name.replace('.pkl', '_label_encoder.pkl')}")
    print(f"  - Metrics: {metrics_path.name}")

if __name__ == "__main__":
    main()

