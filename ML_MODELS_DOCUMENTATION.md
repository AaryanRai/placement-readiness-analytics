# ML Models Documentation

## Overview

The system transitions from rule-based scoring to ML-based prediction using trained models:

1. **Decision Tree Classifier** - Predicts readiness level (Ready/Developing/Entry-Level)
2. **Gradient Boosting Classifier** - Predicts readiness level (Ready/Developing/Entry-Level)
3. **Random Forest Regressor** - Predicts exact readiness score (0-100%)

Additionally, baseline models (**Logistic Regression** for readiness level and **Ridge Regression** for readiness score) are trained and saved to support technical validation/defense. The dashboard reads aggregated performance metrics from `models/model_metrics.json` and displays model artifacts (feature importance, confusion matrix, score distributions) from the trained model files.

## Model Performance

### Decision Tree Classifier
- **Metrics:** loaded from `models/model_metrics.json` and displayed on the ML dashboard
- **Purpose:** Classify students into readiness levels
- **Classes:** Ready, Developing, Entry-Level
- **Key Features:** The exact top features are computed from the trained model and displayed dynamically in the dashboard (feature importance).

### Random Forest Regressor
- **Metrics:** loaded from `models/model_metrics.json` and displayed on the ML dashboard
- **Purpose:** Predict exact readiness score percentage
- **Key Features:** The exact top features are computed from the trained model and displayed dynamically in the dashboard (feature importance).

### Gradient Boosting Classifier
- **Purpose:** Classify students into readiness levels (Ready/Developing/Entry-Level)
- **Key Features:** The exact top features are computed from the trained model and displayed dynamically in the dashboard (feature importance).

## Feature Engineering

### 29 Features Extracted

#### Student Demographics & Program Encoding (5 features)
- `year_of_study`: Academic year (1-4)
- `enrollment_year`: Year of enrollment
- `program_BBA`, `program_Btech`, `program_B.Com`: One-hot encoded program

#### Skill Portfolio (4 features)
- `total_skills`: Total number of skills acquired
- `avg_proficiency`: Average proficiency score across all skills
- `max_proficiency`: Highest proficiency score
- `min_proficiency`: Lowest proficiency score

#### Skills by Category (4 features)
- `skills_Technical`: Count of technical skills
- `skills_Business`: Count of business skills
- `skills_Design`: Count of design skills
- `skills_Soft Skills`: Count of soft skills

#### Skills by Proficiency Level (4 features)
- `proficiency_Beginner`: Count of beginner-level skills
- `proficiency_Intermediate`: Count of intermediate-level skills
- `proficiency_Advanced`: Count of advanced-level skills
- `proficiency_Expert`: Count of expert-level skills

#### Skills by Source (4 features)
- `source_Course`: Skills from courses
- `source_Certification`: Skills from certifications
- `source_Project`: Skills from projects
- `source_Workshop`: Skills from workshops

#### Role-Specific Features (3 features)
- `required_skills_count`: Number of skills required for role
- `matched_skills_count`: Number of required skills student has
- `skill_gap_count`: Number of missing skills

#### Role Encoding (5 features)
- `role_Data Analyst`: One-hot encoded
- `role_Full-Stack Developer`: One-hot encoded
- `role_Digital Marketer`: One-hot encoded
- `role_Business Analyst`: One-hot encoded
- `role_UX/UI Designer`: One-hot encoded

## Training Process

### Data Preparation
1. Extract features from 2,500 student-role combinations
2. Split into train (80%) and test (20%) sets
3. Stratified split for classifier to maintain class distribution

### Model Training
```bash
python src/ml_models/train_models.py
```

This script:
- Extracts features from database
- Trains Decision Tree Classifier
- Trains Gradient Boosting Classifier
- Trains Random Forest Regressor
- Trains baseline Logistic Regression + Ridge Regression for comparison
- Evaluates model performance
- Saves models to `models/` directory

### Model Files
- `models/readiness_classifier.pkl` - Decision Tree Classifier
- `models/readiness_gradient_boosting.pkl` - Gradient Boosting Classifier
- `models/readiness_regressor.pkl` - Random Forest Regressor
- `models/readiness_classifier_label_encoder.pkl` - Label encoder for readiness classes
- `models/baseline_logistic_regression.pkl` - Baseline Logistic Regression (readiness level)
- `models/baseline_logistic_regression_label_encoder.pkl` - Label encoder for baseline logistic regression
- `models/baseline_ridge_regression.pkl` - Baseline Ridge Regression (readiness score)
- `models/model_metrics.json` - Aggregated evaluation metrics for dashboard display

## Usage

### Training Models
```bash
./train_ml_models.sh
# or
python src/ml_models/train_models.py
```

### Making Predictions

#### Single Prediction
```python
from src.ml_models.predict import predict_readiness_ml
from src.database.connection import get_db_session

session = get_db_session()
result = predict_readiness_ml(student_id=1, role_id=1, session=session)
print(result['readiness_score_ml'])  # ML predicted score
print(result['readiness_level_ml'])   # ML predicted level
session.close()
```

#### Batch Prediction
```python
from src.ml_models.predict import predict_batch_ml
from src.database.connection import get_db_session

session = get_db_session()
df = predict_batch_ml(session)  # Predicts for all student-role pairs
session.close()
```

### Updating Database with ML Scores
```bash
./update_scores_ml.sh
# or
python src/core/scoring_ml.py
```

## Integration with Dashboard

The dashboard now includes an ML section showing:
- Model performance metrics
- Data drift monitoring (PSI-based)
- Feature importance visualizations
- Confusion matrix for the classification model (Decision Tree artifact)
- Correlation scatter (Rule-based vs ML signal)
- ML predicted score distribution histogram

## Key Advantages of ML Models

1. **Pattern Learning:** Models learn complex patterns in skill portfolios
2. **Non-linear Relationships:** Captures interactions between features
3. **Generalization:** Better performance on unseen data
4. **Feature Importance:** Identifies most predictive features
5. **Scalability:** Fast predictions once trained

## Model Interpretability

### Most Important Features
- Feature importance is computed from the trained sklearn model artifacts and displayed in the dashboard’s ML page.
- The feature space is defined in `src/ml_models/train_models.py` as `FEATURE_COLUMNS`.

## Comparison: Rule-Based vs ML

### Rule-Based Approach
- **Pros:** Interpretable, explainable, no training needed
- **Cons:** Limited to linear relationships, manual weight tuning

### ML Approach
- **Pros:** Learns complex patterns, better accuracy, automatic feature weighting
- **Cons:** Requires training data, less interpretable, model maintenance

### Hybrid Approach
The system supports both:
- Use rule-based for transparency and explanation
- Use ML for accuracy and pattern discovery
- Compare both in dashboard for validation

## Future Enhancements

1. **Model Retraining:** Periodic retraining as data grows
2. **Hyperparameter Tuning:** Grid search for optimal parameters
3. **Ensemble Methods:** Combine multiple models
4. **Feature Engineering:** Add temporal features, skill interactions
5. **Model Monitoring:** Track prediction drift over time
6. **K-Means Clustering:** Student segmentation (next phase)

