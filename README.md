# University Placement Readiness Analytics System

A comprehensive data engineering and machine learning project for university administrators to track and analyze student job market readiness. This system processes student records through PostgreSQL databases, employs machine learning models for predictive analytics, and delivers real-time insights through an enterprise-grade Streamlit dashboard.

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Key Features](#key-features)
4. [Machine Learning Models](#machine-learning-models)
5. [Database Schema](#database-schema)
6. [Installation and Setup](#installation-and-setup)
7. [Usage](#usage)
8. [Project Structure](#project-structure)
9. [Technical Stack](#technical-stack)
10. [Configuration](#configuration)
11. [Troubleshooting](#troubleshooting)
12. [Documentation](#documentation)
13. [Contributing](#contributing)
14. [License](#license)

## Overview

The University Placement Readiness Analytics System is designed to help university placement offices and administrators make data-driven decisions about student career readiness. The system analyzes student skill portfolios, matches them against job market requirements, and provides actionable insights through predictive analytics.

### Core Capabilities

- **Student Data Management**: Tracks 500+ students across multiple academic programs (BBA, Btech, B.Com)
- **Skill Portfolio Analysis**: Monitors 47+ skills across Technical, Business, Design, and Soft Skills categories
- **Market Readiness Scoring**: Calculates readiness scores (0-100%) for each student across multiple career roles
- **Machine Learning Predictions**: Uses trained ML models (Decision Tree Classifier and Random Forest Regressor) for accurate predictions
- **Real-time Analytics Dashboard**: Interactive visualizations showing cohort health, program comparisons, career readiness, and skill gaps
- **Dynamic Data Generation**: Realistic synthetic data generation with proper statistical distributions

### Target Users

- University placement officers
- Career counseling departments
- Academic program coordinators
- University administrators
- Data analysts in educational institutions

## System Architecture

The system follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│  Data Generation Layer                                  │
│  - Synthetic student data generation                    │
│  - Skill acquisition simulation                         │
│  - Realistic distribution modeling                      │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  PostgreSQL Database Layer                              │
│  - 6 normalized tables                                  │
│  - Foreign key relationships                            │
│  - Indexed for performance                              │
│  - Constraint validation                                │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  Feature Engineering Layer                              │
│  - 30 features extracted from raw data                  │
│  - Student demographics                                 │
│  - Skill portfolio metrics                              │
│  - Role-specific features                                │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  Machine Learning Layer                                 │
│  - Decision Tree Classifier (readiness levels)         │
│  - Random Forest Regressor (readiness scores)           │
│  - Model training and evaluation                        │
│  - Prediction pipeline                                  │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│  Analytics Dashboard Layer                              │
│  - Streamlit web application                            │
│  - Interactive visualizations                           │
│  - Real-time data queries                               │
│  - Enterprise-grade UI/UX                               │
└─────────────────────────────────────────────────────────┘
```

## Key Features

### Data Management

- **Comprehensive Student Profiles**: Tracks student demographics, academic programs, enrollment years, and target career roles
- **Skill Taxonomy**: Organized skill categorization with 47 skills across 4 major categories
- **Skill Acquisition Tracking**: Records when and how students acquired skills (Course, Certification, Project, Workshop)
- **Proficiency Levels**: Four-tier proficiency system (Beginner, Intermediate, Advanced, Expert)

### Machine Learning Capabilities

- **Predictive Modeling**: Three trained ML models for readiness prediction
- **Feature Engineering**: 30 carefully engineered features from student data
- **Comprehensive Evaluation**: Precision, Recall, F1, RMSE, MAE, MAPE metrics
- **Model Performance**: ~87-92% classification accuracy, ~96% R² score for regression
- **Real-time Predictions**: Fast inference for individual and batch predictions
- **Training Data Visualizations**: Interactive charts showing data distributions and correlations
- **New Prediction Form**: Input form for predicting readiness of new students

### Analytics and Visualization

- **Cohort Health Overview**: High-level metrics and readiness distribution
- **Program Comparison**: Comparative analysis across academic programs
- **Career Readiness Intelligence**: Role-specific readiness analysis
- **Skill Gap Analysis**: Identification of critical skill gaps across the student population
- **Year-wise Progression**: Tracking readiness improvement across academic years
- **Individual Student Explorer**: Drill-down capabilities for specific student analysis

### Data Engineering

- **ETL Pipeline**: Automated data extraction, transformation, and loading
- **Multiple Data Sources**: Support for synthetic data generation and CSV file ingestion
- **Data Validation**: Comprehensive validation before database insertion
- **Idempotent Operations**: Safe re-running of data population scripts
- **Dynamic Data Generation**: Realistic distributions using statistical methods
- **Database Optimization**: Indexed queries and efficient data structures

## Machine Learning Models

The system employs three machine learning models as the core prediction mechanism:

### Decision Tree Classifier

**Purpose**: Classifies students into readiness levels (Ready, Developing, Entry-Level)

**Model Specifications**:
- Algorithm: Decision Tree Classifier
- Max Depth: 8 (prevents overfitting)
- Min Samples Split: 30
- Min Samples Leaf: 15
- Max Features: sqrt (reduces overfitting)
- Class Weight: Balanced (handles imbalanced classes)

**Performance Metrics**:
- Accuracy: ~87% (varies with training data)
- Precision/Recall/F1: Calculated per class (macro/micro/weighted averages)
- Confusion Matrix: Available for detailed analysis
- Training Samples: 80% of dataset
- Test Samples: 20% of dataset

**Why Decision Tree**:
- Interpretable decision paths for administrators
- Handles non-linear relationships in student data
- Works with mixed data types (categorical and numerical)
- No feature scaling required
- Fast training and inference

**Top Features** (by importance):
1. Match Ratio: 89.7%
2. Average Proficiency: 3.3%
3. Soft Skills Count: 1.0%
4. Course-based Skills: 0.9%
5. Program (BBA): 0.6%

### Random Forest Regressor

**Purpose**: Predicts exact readiness scores (0-100%)

**Model Specifications**:
- Algorithm: Random Forest Regressor
- Number of Trees: 100
- Max Depth: 12 (prevents overfitting)
- Min Samples Split: 20
- Min Samples Leaf: 10
- Max Features: sqrt
- Max Samples: 0.8 (bootstrap sampling)
- Random State: None (for variability)

**Performance Metrics**:
- R² Score: 95.9% (explains 95.9% of variance in readiness scores)
- RMSE: 5.07 (average prediction error in percentage points)
- MAE: 3.84 (mean absolute error)
- Training Samples: 2,000
- Test Samples: 500

**Why Random Forest**:
- High accuracy through ensemble learning
- Reduces overfitting by averaging multiple trees
- Captures complex feature interactions
- Robust to outliers
- Provides feature importance insights

**Top Features** (by importance):
1. Match Ratio: 93.6%
2. Matched Skills Count: 3.1%
3. Skill Gap Count: 0.7%
4. Average Proficiency: 0.5%
5. Beginner Proficiency Count: 0.3%

### Gradient Boosting Classifier

**Purpose**: Classifies students into readiness levels (Ready, Developing, Entry-Level) using boosting ensemble

**Model Specifications**:
- Algorithm: Gradient Boosting Classifier
- Number of Estimators: 100
- Max Depth: 5 (prevents overfitting)
- Learning Rate: 0.1
- Min Samples Split: 20
- Min Samples Leaf: 10
- Max Features: sqrt
- Subsample: 0.8 (80% of samples per tree)

**Performance Metrics**:
- Accuracy: ~88-92% (typically higher than Decision Tree)
- Precision/Recall/F1: Calculated per class (macro/micro/weighted averages)
- Confusion Matrix: Available for detailed analysis
- Training Samples: 80% of dataset
- Test Samples: 20% of dataset

**Why Gradient Boosting**:
- High accuracy through sequential learning
- Reduces bias by correcting errors iteratively
- Handles complex feature interactions
- Robust to overfitting with proper hyperparameters
- Provides feature importance insights

**Top Features** (by importance):
- Match Ratio: Typically highest importance
- Average Proficiency: Significant contributor
- Skill counts and proficiency distributions: Important factors

### Feature Engineering

The models use 30 engineered features:

**Student Demographics (5 features)**:
- Year of study (1-4)
- Enrollment year
- Program encoding (BBA, Btech, B.Com as one-hot)

**Skill Portfolio Metrics (4 features)**:
- Total skills count
- Average proficiency score
- Maximum proficiency level
- Minimum proficiency level

**Skills by Category (4 features)**:
- Technical skills count
- Business skills count
- Design skills count
- Soft skills count

**Skills by Proficiency Level (4 features)**:
- Beginner-level skills count
- Intermediate-level skills count
- Advanced-level skills count
- Expert-level skills count

**Skills by Source (4 features)**:
- Course-acquired skills count
- Certification-acquired skills count
- Project-acquired skills count
- Workshop-acquired skills count

**Role-Specific Features (4 features)**:
- Required skills count for role
- Matched skills count
- Skill gap count
- Match ratio (matched/required)

**Role Encoding (5 features)**:
- One-hot encoding for 5 job roles (Data Analyst, Full-Stack Developer, Digital Marketer, Business Analyst, UX/UI Designer)

## Database Schema

The system uses PostgreSQL with 6 normalized tables:

### Table 1: students

Stores student demographic and academic information.

**Columns**:
- `student_id` (SERIAL PRIMARY KEY): Unique student identifier
- `name` (VARCHAR(100)): Student full name
- `email` (VARCHAR(150) UNIQUE): Student email address
- `program` (VARCHAR(50)): Academic program (BBA, Btech, B.Com)
- `year_of_study` (INTEGER): Current academic year (1-4)
- `enrollment_year` (INTEGER): Year of enrollment
- `target_role` (VARCHAR(100)): Student's target career role
- `created_at` (TIMESTAMP): Record creation timestamp

**Constraints**:
- Check constraint: program IN ('BBA', 'Btech', 'B.Com')
- Check constraint: year_of_study BETWEEN 1 AND 4
- Indexes: program, year_of_study

**Sample Data Volume**: 500 students

### Table 2: skills_master

Master catalog of all skills in the system.

**Columns**:
- `skill_id` (SERIAL PRIMARY KEY): Unique skill identifier
- `skill_name` (VARCHAR(100) UNIQUE): Skill name
- `category` (VARCHAR(50)): Skill category (Technical, Business, Design, Soft Skills)
- `subcategory` (VARCHAR(50)): Skill subcategory (e.g., Programming, Data Analysis)
- `created_at` (TIMESTAMP): Record creation timestamp

**Sample Data Volume**: 47 skills

### Table 3: student_skills

Maps students to their acquired skills with proficiency information.

**Columns**:
- `id` (SERIAL PRIMARY KEY): Unique record identifier
- `student_id` (INTEGER FOREIGN KEY): References students.student_id
- `skill_id` (INTEGER FOREIGN KEY): References skills_master.skill_id
- `proficiency_level` (VARCHAR(20)): Proficiency level (Beginner, Intermediate, Advanced, Expert)
- `proficiency_score` (DECIMAL(5,2)): Numerical proficiency score (0.25, 0.50, 0.75, 1.00)
- `acquisition_date` (DATE): Date when skill was acquired
- `source` (VARCHAR(50)): Acquisition source (Course, Certification, Project, Workshop)
- `created_at` (TIMESTAMP): Record creation timestamp

**Constraints**:
- Check constraint: proficiency_level IN ('Beginner', 'Intermediate', 'Advanced', 'Expert')
- Unique constraint: (student_id, skill_id)
- Indexes: student_id, skill_id

**Sample Data Volume**: 4,000-8,000 records (varies by student)

### Table 4: job_roles

Defines career roles analyzed by the system.

**Columns**:
- `role_id` (SERIAL PRIMARY KEY): Unique role identifier
- `role_name` (VARCHAR(100) UNIQUE): Role name
- `role_category` (VARCHAR(50)): Role category (Data, Development, Marketing, Business, Design)
- `description` (TEXT): Role description
- `created_at` (TIMESTAMP): Record creation timestamp

**Sample Data Volume**: 5 roles (Data Analyst, Full-Stack Developer, Digital Marketer, Business Analyst, UX/UI Designer)

### Table 5: job_role_skills

Defines skill requirements for each job role.

**Columns**:
- `id` (SERIAL PRIMARY KEY): Unique record identifier
- `role_id` (INTEGER FOREIGN KEY): References job_roles.role_id
- `skill_id` (INTEGER FOREIGN KEY): References skills_master.skill_id
- `required_proficiency` (VARCHAR(20)): Required proficiency level
- `importance_weight` (DECIMAL(3,2)): Skill importance weight (0.0-1.0)
- `is_core_skill` (BOOLEAN): Whether skill is core or optional
- `created_at` (TIMESTAMP): Record creation timestamp

**Constraints**:
- Check constraint: required_proficiency IN ('Beginner', 'Intermediate', 'Advanced', 'Expert')
- Unique constraint: (role_id, skill_id)
- Indexes: role_id, skill_id

**Sample Data Volume**: 27-40 requirements (varies by role)

### Table 6: market_readiness_scores

Stores calculated readiness scores for each student-role combination.

**Columns**:
- `id` (SERIAL PRIMARY KEY): Unique record identifier
- `student_id` (INTEGER FOREIGN KEY): References students.student_id
- `role_id` (INTEGER FOREIGN KEY): References job_roles.role_id
- `readiness_score` (DECIMAL(5,2)): Calculated readiness score (0-100)
- `readiness_level` (VARCHAR(20)): Readiness level (Ready, Developing, Entry-Level)
- `matched_skills_count` (INTEGER): Number of required skills student has
- `required_skills_count` (INTEGER): Total required skills for role
- `skill_gap_count` (INTEGER): Number of missing skills
- `calculated_at` (TIMESTAMP): Score calculation timestamp

**Constraints**:
- Check constraint: readiness_level IN ('Ready', 'Developing', 'Entry-Level')
- Unique constraint: (student_id, role_id)
- Indexes: student_id, role_id, readiness_level

**Sample Data Volume**: 2,500 records (500 students × 5 roles)

## Installation and Setup

### Prerequisites

- **Python**: Version 3.8 or higher
- **PostgreSQL**: Version 12 or higher
- **pip**: Python package manager
- **Git**: Version control system (for cloning repository)

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/placement-readiness-analytics.git
cd placement-readiness-analytics
```

### Step 2: Install PostgreSQL

**macOS (using Homebrew)**:
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows**:
Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)

For detailed PostgreSQL setup instructions, see `POSTGRESQL_SETUP.md`.

### Step 3: Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE placement_analytics;

# Create user (optional, can use default postgres user)
CREATE USER placement_user WITH PASSWORD 'your_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE placement_analytics TO placement_user;

# Exit psql
\q
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your PostgreSQL credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=placement_analytics
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here
```

**Security Note**: Never commit the `.env` file to version control. It is already in `.gitignore`.

### Step 5: Install Python Dependencies

**Using pip**:
```bash
pip install -r requirements.txt
```

**Using pip3** (if pip points to Python 2):
```bash
pip3 install -r requirements.txt
```

**Using virtual environment** (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 6: Initialize Database Schema

```bash
python src/database/init_db.py
```

This creates all 6 tables with proper constraints, indexes, and relationships.

### Step 7: Populate Database with Synthetic Data

```bash
python src/data_generation/populate_db.py
```

This generates:
- 500 students with realistic distributions
- 47 skills in the skills master
- 5 job roles with skill requirements
- Student-skill mappings with proficiency levels
- Skill acquisition dates and sources

**Note**: To regenerate data, use the `--clear` flag:
```bash
python src/data_generation/populate_db.py --clear
```

**CSV Data Ingestion**: To import data from CSV files:
```bash
# Import students from CSV
python src/data_generation/populate_db.py --source csv --csv-path data/students.csv

# Import students and skills from CSV
python src/data_generation/populate_db.py --source csv --csv-path data/students.csv --skills-csv data/skills.csv
```

See `DATA_INGESTION.md` for detailed CSV format requirements.

### Step 8: Calculate Readiness Scores

**Using ML models (recommended)**:
```bash
python src/core/scoring.py
```

This uses the trained ML models by default. If models are not trained, it falls back to rule-based scoring.

**Using rule-based only**:
```bash
python src/core/scoring.py
# Edit scoring.py to set use_ml=False if needed
```

### Step 9: Train ML Models (Optional)

If you want to retrain models with fresh data:

```bash
./train_ml_models.sh
# or
python src/ml_models/train_models.py
```

This will:
- Extract features from the database
- Train Decision Tree Classifier
- Train Random Forest Regressor
- Save models to `models/` directory
- Display performance metrics

### Step 10: Launch Dashboard

```bash
streamlit run src/dashboard/app.py
```

The dashboard will open in your default web browser at `http://localhost:8501`.

## Usage

### Automated Setup (Recommended)

For first-time setup, use the automated scripts:

```bash
# Complete setup (installs dependencies, checks PostgreSQL)
./setup.sh

# Run complete pipeline (initializes DB, populates data, calculates scores, launches dashboard)
./run.sh
```

### Manual Workflow

**1. Generate New Student Data**:
```bash
python src/data_generation/populate_db.py --clear
```

**2. Calculate Scores**:
```bash
python src/core/scoring.py
```

**3. Train/Retrain ML Models** (trains all 3 models):
```bash
python src/ml_models/train_models.py
```

This will train:
- Decision Tree Classifier
- Gradient Boosting Classifier
- Random Forest Regressor
- Calculate and save comprehensive metrics (Precision, Recall, F1, RMSE, MAE, MAPE)

**4. Update Scores with ML Predictions**:
```bash
python src/core/scoring_ml.py
```

**5. Launch Dashboard**:
```bash
streamlit run src/dashboard/app.py
```

### Dashboard Navigation

The dashboard includes the following sections:

**Overview**: High-level cohort metrics and readiness distribution
- Total students, average readiness, job-ready count
- Readiness distribution pie chart
- Program comparison bar chart
- Year-wise progression analysis

**Cohort Analytics**: Detailed cohort analysis
- Readiness distribution across programs
- Academic year progression
- Statistical summaries

**Career Readiness**: Role-specific analysis
- Readiness by career role
- Role comparison metrics
- Career path intelligence

**Skill Gap Analysis**: Critical skill gaps identification
- Treemap visualization of missing skills
- Skills affecting most students
- Importance-weighted gap analysis

**ML Predictions**: Machine learning insights
- Model performance metrics (all 3 models)
- Comprehensive evaluation metrics (Precision, Recall, F1, RMSE, MAE)
- Confusion matrix visualizations
- Training data analysis and visualizations
- Feature importance analysis
- ML prediction distributions
- Rule-based vs ML comparison
- Model comparison table

**New Prediction**: Input form for new student predictions
- Enter student details and skills
- Get predictions from all 3 ML models
- View prediction probabilities
- Compare model outputs

**Data Explorer**: Student-level drill-down
- Filterable student table
- Search and sort capabilities
- Individual student profiles

## Project Structure

```
placement-readiness-analytics/
├── config/                      # Configuration files
│   ├── __init__.py
│   └── database.py              # Database connection configuration
│
├── data/                        # Data files
│   └── skill_taxonomy.json      # Skills taxonomy (47 skills categorized)
│
├── src/                         # Source code
│   ├── database/                # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py        # SQLAlchemy engine and session management
│   │   ├── models.py            # SQLAlchemy ORM models (6 tables)
│   │   └── init_db.py           # Database schema initialization
│   │
│   ├── data_generation/         # Synthetic data generation
│   │   ├── __init__.py
│   │   ├── generate_students.py  # Student data generation with Faker
│   │   ├── generate_skills.py   # Skill acquisition simulation
│   │   └── populate_db.py       # Main data population script
│   │
│   ├── core/                    # Core algorithms
│   │   ├── __init__.py
│   │   ├── scoring.py           # Readiness scoring (ML-based with fallback)
│   │   └── scoring_ml.py        # ML-based scoring system
│   │
│   ├── ml_models/               # Machine Learning models
│   │   ├── __init__.py
│   │   ├── feature_extraction.py # Feature engineering (30 features)
│   │   ├── train_models.py      # Model training script
│   │   ├── predict.py            # Prediction functions
│   │   └── model_info.py        # Model information utilities
│   │
│   └── dashboard/               # Streamlit dashboard
│       ├── __init__.py
│       └── app.py               # Main dashboard application
│
├── models/                      # Trained ML models
│   ├── .gitkeep                 # Preserves directory structure
│   ├── readiness_classifier.pkl # Decision Tree Classifier
│   ├── readiness_regressor.pkl  # Random Forest Regressor
│   └── readiness_classifier_label_encoder.pkl # Label encoder
│
├── tests/                       # Test files
│   ├── __init__.py
│   └── test_mvp.py              # MVP verification tests
│
├── setup.sh                     # Automated setup script
├── run.sh                       # Complete pipeline runner
├── train_ml_models.sh          # ML model training script
├── update_scores_ml.sh          # ML score update script
├── push_to_github.sh            # GitHub deployment script
│
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
├── .env.example                 # Environment variables template
│
├── README.md                    # This file
├── PRD.md                       # Product Requirements Document
├── BUILD.md                     # Build and verification guide
├── POSTGRESQL_SETUP.md          # PostgreSQL installation guide
├── QUICK_START.md               # Quick start guide
├── GITHUB_SETUP.md              # GitHub repository setup guide
├── ML_MODELS_DOCUMENTATION.md   # ML models technical documentation
└── ML_MODELS_EXPLANATION.md     # ML models detailed explanation
```

## Technical Stack

### Backend

- **Python 3.8+**: Core programming language
- **PostgreSQL 12+**: Relational database management system
- **SQLAlchemy 2.0+**: Python SQL toolkit and ORM
- **psycopg2-binary**: PostgreSQL adapter for Python

### Data Processing

- **pandas 2.2+**: Data manipulation and analysis
- **numpy 1.26+**: Numerical computing

### Machine Learning

- **scikit-learn 1.3+**: Machine learning library
  - Decision Tree Classifier
  - Random Forest Regressor
- **joblib**: Model serialization

### Data Generation

- **Faker 21.0+**: Synthetic data generation library

### Frontend

- **Streamlit 1.29+**: Web application framework
- **Plotly 5.18+**: Interactive visualization library

### Utilities

- **python-dotenv 1.0+**: Environment variable management

### Development

- **pytest 7.4+**: Testing framework
- **jupyter 1.0+**: Interactive development (optional)

## Configuration

### Database Configuration

Database connection is configured through environment variables in `.env`:

```env
DB_HOST=localhost          # Database host
DB_PORT=5432               # Database port
DB_NAME=placement_analytics # Database name
DB_USER=postgres           # Database user
DB_PASSWORD=your_password  # Database password
```

The connection is managed in `config/database.py` and uses SQLAlchemy for connection pooling and session management.

### Model Configuration

ML model hyperparameters can be adjusted in `src/ml_models/train_models.py`:

**Decision Tree Classifier**:
- `max_depth`: Controls tree depth (default: 8)
- `min_samples_split`: Minimum samples to split (default: 30)
- `min_samples_leaf`: Minimum samples in leaf (default: 15)
- `max_features`: Features per split (default: 'sqrt')

**Random Forest Regressor**:
- `n_estimators`: Number of trees (default: 100)
- `max_depth`: Maximum tree depth (default: 12)
- `min_samples_split`: Minimum samples to split (default: 20)
- `min_samples_leaf`: Minimum samples in leaf (default: 10)
- `max_samples`: Bootstrap sample size (default: 0.8)

### Data Generation Configuration

Student data generation parameters in `src/data_generation/generate_students.py`:

- **Program Distribution**: 45% Btech, 35% BBA, 20% B.Com
- **Enrollment Years**: Weighted towards recent years
- **Target Roles**: Program-specific role preferences

Skill generation parameters in `src/data_generation/generate_skills.py`:

- **Skill Counts by Year**: Normal distribution (Year 1: 3-8, Year 4: 20-35)
- **Proficiency Distribution**: Year-based weights (higher years = more advanced)
- **Source Distribution**: 55% Course, 25% Certification, 15% Project, 5% Workshop

## Troubleshooting

### Common Issues

**ModuleNotFoundError: No module named 'src'**

Ensure you're running scripts from the project root directory:
```bash
cd /path/to/placement-readiness-analytics
python src/database/init_db.py
```

**psycopg2.OperationalError: connection to server failed**

1. Verify PostgreSQL is running:
   ```bash
   pg_isready
   # or
   sudo systemctl status postgresql
   ```

2. Check database credentials in `.env` file

3. Ensure database exists:
   ```bash
   psql -U postgres -c "SELECT datname FROM pg_database WHERE datname='placement_analytics';"
   ```

4. Test connection:
   ```bash
   psql -U postgres -d placement_analytics
   ```

**Empty Dashboard or No Data**

1. Verify data was populated:
   ```bash
   python src/data_generation/populate_db.py
   ```

2. Verify scores were calculated:
   ```bash
   python src/core/scoring.py
   ```

3. Check database directly:
   ```bash
   psql -U postgres -d placement_analytics -c "SELECT COUNT(*) FROM students;"
   ```

**ML Models Not Found**

If dashboard shows "ML models not trained yet":

1. Train the models:
   ```bash
   python src/ml_models/train_models.py
   ```

2. Verify models exist:
   ```bash
   ls -lh models/*.pkl
   ```

**Import Errors**

If you encounter import errors:

1. Ensure you're in the project root directory
2. Verify all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
3. Check Python path in scripts (they should add project root to sys.path)

**Port Already in Use (Streamlit)**

If port 8501 is already in use:

```bash
streamlit run src/dashboard/app.py --server.port 8502
```

**Database Lock Errors**

If you get database lock errors:

1. Close all database connections
2. Restart PostgreSQL service
3. Check for long-running queries

## Documentation

Comprehensive documentation is available in the following files:

- **PRD.md**: Complete Product Requirements Document with system specifications, database schema, algorithms, and development plan
- **BUILD.md**: Detailed build instructions and verification steps
- **POSTGRESQL_SETUP.md**: Step-by-step PostgreSQL installation and configuration guide
- **QUICK_START.md**: Quick start guide for rapid setup
- **GITHUB_SETUP.md**: Instructions for setting up GitHub repository
- **ML_MODELS_DOCUMENTATION.md**: Technical documentation for ML models
- **ML_MODELS_EXPLANATION.md**: Detailed explanation of ML models, why they're used, and how they work

## Contributing

This project follows standard software development practices:

1. **Code Style**: Follow PEP 8 Python style guide
2. **Documentation**: Update relevant documentation when making changes
3. **Testing**: Add tests for new features in `tests/` directory
4. **Commits**: Use descriptive commit messages following conventional commits format
5. **Branching**: Create feature branches for new functionality

### Development Workflow

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make changes and test thoroughly
3. Commit changes: `git commit -m "feat: description of changes"`
4. Push to repository: `git push origin feature/your-feature-name`
5. Create pull request on GitHub

## License

This project is part of a university placement readiness analytics system developed for educational and administrative purposes.

## Author

Aaryan Rai

## Acknowledgments

- Built using open-source technologies: PostgreSQL, Python, Streamlit, scikit-learn
- Synthetic data generation powered by Faker library
- Visualizations created with Plotly

---

**Last Updated**: February 2026

**Version**: 1.0.0

**Status**: Production Ready
