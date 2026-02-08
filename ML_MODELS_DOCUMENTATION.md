# ML Models Documentation

## Overview

The system has transitioned from rule-based scoring to ML-based prediction using two trained models:

1. **Decision Tree Classifier** - Predicts readiness level (Ready/Developing/Entry-Level)
2. **Random Forest Regressor** - Predicts exact readiness score (0-100%)

## Model Performance

### Decision Tree Classifier
- **Accuracy:** 87.0%
- **Purpose:** Classify students into readiness levels
- **Classes:** Ready, Developing, Entry-Level
- **Training Samples:** 2,000
- **Test Samples:** 500
- **Key Features:** match_ratio (89.7% importance), avg_proficiency, skills_Soft Skills

### Random Forest Regressor
- **R² Score:** 95.9%
- **RMSE:** 5.07
- **MAE:** 3.84
- **Purpose:** Predict exact readiness score percentage
- **Training Samples:** 2,000
- **Test Samples:** 500
- **Key Features:** match_ratio (93.6% importance), matched_skills_count, skill_gap_count

## Feature Engineering

### 28 Features Extracted

#### Student Demographics (3 features)
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

#### Role-Specific Features (4 features)
- `required_skills_count`: Number of skills required for role
- `matched_skills_count`: Number of required skills student has
- `skill_gap_count`: Number of missing skills
- `match_ratio`: matched_skills / required_skills

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
- Trains Random Forest Regressor
- Evaluates model performance
- Saves models to `models/` directory

### Model Files
- `models/readiness_classifier.pkl` - Decision Tree Classifier
- `models/readiness_regressor.pkl` - Random Forest Regressor
- `models/readiness_classifier_label_encoder.pkl` - Label encoder for classes

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

The dashboard now includes an "ML Predictions" section showing:
- Model performance metrics
- Rule-based vs ML comparison table
- Feature importance visualizations
- ML prediction distributions
- Statistical summaries

## Key Advantages of ML Models

1. **Pattern Learning:** Models learn complex patterns in skill portfolios
2. **Non-linear Relationships:** Captures interactions between features
3. **Generalization:** Better performance on unseen data
4. **Feature Importance:** Identifies most predictive features
5. **Scalability:** Fast predictions once trained

## Model Interpretability

### Most Important Features
1. **match_ratio** (89.7% - Classifier, 93.6% - Regressor)
   - Ratio of matched skills to required skills
   - Most predictive feature

2. **avg_proficiency** (3.3% - Classifier, 0.5% - Regressor)
   - Average skill proficiency level
   - Indicates overall skill quality

3. **matched_skills_count** (3.1% - Regressor)
   - Absolute number of matched skills
   - Important for score prediction

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

