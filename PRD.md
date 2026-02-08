# PRODUCT REQUIREMENTS DOCUMENT (PRD)
# University Placement Readiness Analytics System
## MVP-First Approach for Day 1 Deployment

**Version:** 2.0 (MVP-Focused)  
**Date:** February 2026  
**Owner:** Aaryan Rai  
**Target:** Working MVP by End of Day 1, Full System by Day 7

---

## EXECUTIVE SUMMARY

### Vision
Build a data-heavy, university-facing placement analytics dashboard that processes 2000+ student records through PostgreSQL and automated pipelines, delivering real-time insights on job market readiness.

### MVP Strategy
**Day 1 Goal:** Functional system demonstrating core value proposition
- 500 students in PostgreSQL
- Basic ETL calculating readiness scores
- Dashboard with 3 key visualizations
- Prove the concept works end-to-end

**Day 2-7 Goal:** Scale to production
- 2000 students
- Full ETL automation
- 10 visualizations
- All 3 ML models
- Complete documentation

---

## SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────┐
│  SYNTHETIC DATA GENERATOR (Faker Library)           │
│  Day 1: 500 students → Day 7: 2000 students         │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  POSTGRESQL DATABASE (60,000+ records)              │
│  • students (2000)                                  │
│  • skills_master (200)                              │
│  • student_skills (25,000)                          │
│  • job_roles (12)                                   │
│  • job_role_skills (150)                            │
│  • market_readiness_scores (24,000)                 │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  ETL PIPELINE (Python + SQLAlchemy)                 │
│  Day 1: Manual run → Day 5: APScheduler automated  │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  ML MODELS (Scikit-learn)                           │
│  Day 3: Decision Tree → Day 5: All 3 models        │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  STREAMLIT DASHBOARD (Live PostgreSQL Queries)      │
│  Day 1: 3 charts → Day 7: 10 visualizations        │
└─────────────────────────────────────────────────────┘
```

---

## DAY 1 MVP SCOPE (MUST-HAVES)

### Database (PostgreSQL)
**Tables to Create:**
1. `students` - 500 records
2. `skills_master` - 50 skills (simplified)
3. `student_skills` - 4,000 records
4. `job_roles` - 5 roles (Data Analyst, Full-Stack Dev, Digital Marketer, Business Analyst, UX Designer)
5. `job_role_skills` - 40 records
6. `market_readiness_scores` - 2,500 records (500 × 5 roles)

### Core Algorithm (Python Function)
```python
def calculate_readiness_score(student_id, role_id):
    """
    Calculate market readiness score for a student-role pair.
    
    Formula:
    Score = (Σ matched_proficiency × importance_weight) / Σ required_weights × 100
    
    Returns:
    {
        'readiness_score': float (0-100),
        'readiness_level': str ('Ready', 'Developing', 'Entry-Level'),
        'matched_skills': int,
        'missing_skills': int
    }
    """
```

### Dashboard (Streamlit - 3 Core Charts)
1. **Pie Chart:** Cohort Readiness Distribution
   - Ready (80-100%): X students
   - Developing (50-79%): Y students
   - Entry-Level (0-49%): Z students

2. **Bar Chart:** Average Readiness by Program
   - BBA: 62%
   - Btech: 68%
   - B.Com: 59%

3. **Table:** Top 10 Students by Readiness
   - Columns: Name, Program, Year, Best Role, Score

### Success Criteria for Day 1
- [ ] PostgreSQL database running with 500 students
- [ ] Readiness scores calculated for all student-role pairs
- [ ] Dashboard loads in <3 seconds
- [ ] Can filter by program
- [ ] Git repository initialized with 5+ commits

---

## COMPLETE DATABASE SCHEMA

### Table 1: students
```sql
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    program VARCHAR(50) NOT NULL CHECK (program IN ('BBA', 'Btech', 'B.Com')),
    year_of_study INTEGER CHECK (year_of_study BETWEEN 1 AND 4),
    enrollment_year INTEGER NOT NULL,
    target_role VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_students_program ON students(program);
CREATE INDEX idx_students_year ON students(year_of_study);
```

**Sample Data:**
```
student_id | name         | program | year | target_role
-----------|--------------|---------|------|-------------
1          | Aarav Kumar  | Btech   | 3    | Data Analyst
2          | Priya Sharma | BBA     | 4    | Business Analyst
3          | Rahul Singh  | Btech   | 2    | Full-Stack Developer
```

### Table 2: skills_master
```sql
CREATE TABLE skills_master (
    skill_id SERIAL PRIMARY KEY,
    skill_name VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL CHECK (category IN ('Technical', 'Business', 'Design', 'Soft Skills')),
    subcategory VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_skills_category ON skills_master(category);
```

**Skills to Populate (50 for MVP, 200 for final):**
```
Technical:
  Programming: Python, JavaScript, Java, C++, SQL, R
  Data: Pandas, NumPy, Excel, Tableau, Power BI, Statistics
  Web: React, Node.js, HTML/CSS, Django, Flask
  Database: PostgreSQL, MySQL, MongoDB
  Cloud: AWS, Azure, Docker

Business:
  Analysis: Business Intelligence, Financial Modeling
  Marketing: SEO, Google Ads, Social Media Marketing
  Management: Project Management, Agile

Design:
  UI/UX: Figma, Wireframing, User Research
  Graphics: Photoshop, Canva

Soft Skills:
  Communication, Teamwork, Leadership, Problem Solving
```

### Table 3: student_skills
```sql
CREATE TABLE student_skills (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(student_id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills_master(skill_id) ON DELETE CASCADE,
    proficiency_level VARCHAR(20) CHECK (proficiency_level IN ('Beginner', 'Intermediate', 'Advanced', 'Expert')),
    proficiency_score DECIMAL(3,2) CHECK (proficiency_score BETWEEN 0 AND 1),
    acquisition_date DATE NOT NULL,
    source VARCHAR(50) CHECK (source IN ('Course', 'Certification', 'Project', 'Workshop')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, skill_id)
);

CREATE INDEX idx_student_skills_student ON student_skills(student_id);
CREATE INDEX idx_student_skills_skill ON student_skills(skill_id);
```

**Proficiency Mapping:**
- Beginner: 0.25
- Intermediate: 0.50
- Advanced: 0.75
- Expert: 1.00

### Table 4: job_roles
```sql
CREATE TABLE job_roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(100) UNIQUE NOT NULL,
    role_category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Job Roles (MVP: 5, Final: 12):**
```
1. Data Analyst
2. Full-Stack Developer
3. Digital Marketer
4. Business Analyst
5. UX/UI Designer
[Final adds: Frontend Dev, Backend Dev, Product Manager, Financial Analyst, HR Analyst, Cloud Engineer, DevOps Engineer]
```

### Table 5: job_role_skills
```sql
CREATE TABLE job_role_skills (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES job_roles(role_id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES skills_master(skill_id) ON DELETE CASCADE,
    required_proficiency VARCHAR(20) NOT NULL,
    importance_weight DECIMAL(3,2) DEFAULT 1.0 CHECK (importance_weight BETWEEN 0 AND 1),
    is_core_skill BOOLEAN DEFAULT FALSE,
    UNIQUE(role_id, skill_id)
);

CREATE INDEX idx_job_role_skills_role ON job_role_skills(role_id);
```

**Example: Data Analyst Requirements**
```
role_id | skill_name  | required_proficiency | importance_weight | is_core
--------|-------------|---------------------|-------------------|--------
1       | Python      | Intermediate        | 1.0               | TRUE
1       | SQL         | Intermediate        | 1.0               | TRUE
1       | Excel       | Advanced            | 0.9               | TRUE
1       | Tableau     | Intermediate        | 0.8               | TRUE
1       | Statistics  | Intermediate        | 0.9               | TRUE
1       | R           | Beginner            | 0.5               | FALSE
1       | Power BI    | Beginner            | 0.5               | FALSE
```

### Table 6: market_readiness_scores
```sql
CREATE TABLE market_readiness_scores (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(student_id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES job_roles(role_id) ON DELETE CASCADE,
    readiness_score DECIMAL(5,2) CHECK (readiness_score BETWEEN 0 AND 100),
    matched_skills_count INTEGER DEFAULT 0,
    required_skills_count INTEGER DEFAULT 0,
    skill_gap_count INTEGER DEFAULT 0,
    readiness_level VARCHAR(20) CHECK (readiness_level IN ('Ready', 'Developing', 'Entry-Level')),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, role_id)
);

CREATE INDEX idx_readiness_student ON market_readiness_scores(student_id);
CREATE INDEX idx_readiness_level ON market_readiness_scores(readiness_level);
CREATE INDEX idx_readiness_score ON market_readiness_scores(readiness_score DESC);
```

---

## SYNTHETIC DATA GENERATION SPECS

### Student Distribution (2000 total)
```python
STUDENT_CONFIG = {
    'total': 2000,
    'programs': {
        'BBA': 800,   # 40%
        'Btech': 700,   # 35%
        'B.Com': 500  # 25%
    },
    'years': {
        1: 600,  # 30%
        2: 500,  # 25%
        3: 500,  # 25%
        4: 400   # 20%
    }
}
```

### Skill Acquisition Patterns
```python
SKILLS_BY_YEAR = {
    1: (3, 8),    # Year 1: 3-8 skills
    2: (8, 15),   # Year 2: 8-15 skills
    3: (15, 25),  # Year 3: 15-25 skills
    4: (20, 35)   # Year 4: 20-35 skills
}

PROFICIENCY_BY_TIME = {
    'months_0_3': 'Beginner',
    'months_3_8': 'Intermediate',
    'months_8_18': 'Advanced',
    'months_18_plus': 'Expert'
}
```

### Program-to-Role Mapping
```python
TARGET_ROLES_BY_PROGRAM = {
    'Btech': ['Data Analyst', 'Full-Stack Developer', 'Frontend Developer', 'Backend Developer'],
    'BBA': ['Business Analyst', 'Product Manager', 'Digital Marketer', 'HR Analyst'],
    'B.Com': ['Financial Analyst', 'Business Analyst', 'Data Analyst']
}
```

---

## CORE ALGORITHM IMPLEMENTATION

### File: `src/core/scoring.py`
```python
"""
Market Readiness Score Calculation Engine
"""
from decimal import Decimal
from typing import Dict, List
from sqlalchemy.orm import Session
from src.database.models import Student, JobRole, JobRoleSkills, StudentSkills

PROFICIENCY_MAP = {
    'Beginner': Decimal('0.25'),
    'Intermediate': Decimal('0.50'),
    'Advanced': Decimal('0.75'),
    'Expert': Decimal('1.00')
}

def calculate_readiness_score(student_id: int, role_id: int, session: Session) -> Dict:
    """
    Calculate market readiness score using weighted skill matching.
    
    Algorithm:
    1. Get all required skills for the job role
    2. Get student's current skills
    3. For each required skill:
       - If student has it: calculate proficiency_factor = min(student_prof / required_prof, 1.0)
       - Add (proficiency_factor × importance_weight) to score
    4. Final score = (total_matched_score / sum_of_all_weights) × 100
    
    Returns:
        {
            'readiness_score': 0-100,
            'readiness_level': 'Ready' | 'Developing' | 'Entry-Level',
            'matched_skills_count': int,
            'required_skills_count': int,
            'skill_gap_count': int,
            'missing_skills': [{skill_name, importance_weight}]
        }
    """
    # Get required skills for role
    required_skills = session.query(JobRoleSkills).filter_by(role_id=role_id).all()
    
    if not required_skills:
        return {
            'readiness_score': 0,
            'readiness_level': 'Entry-Level',
            'matched_skills_count': 0,
            'required_skills_count': 0,
            'skill_gap_count': 0,
            'missing_skills': []
        }
    
    required_count = len(required_skills)
    total_weight = sum(Decimal(str(skill.importance_weight)) for skill in required_skills)
    
    # Get student's skills
    student_skills = session.query(StudentSkills).filter_by(student_id=student_id).all()
    student_skill_map = {
        skill.skill_id: Decimal(str(skill.proficiency_score)) 
        for skill in student_skills
    }
    
    # Calculate weighted score
    matched_score = Decimal('0')
    matched_count = 0
    missing_skills = []
    
    for req_skill in required_skills:
        skill_id = req_skill.skill_id
        required_prof = PROFICIENCY_MAP[req_skill.required_proficiency]
        importance = Decimal(str(req_skill.importance_weight))
        
        if skill_id in student_skill_map:
            # Student has this skill
            student_prof = student_skill_map[skill_id]
            
            # Partial credit if proficiency is lower than required
            proficiency_factor = min(student_prof / required_prof, Decimal('1.0'))
            matched_score += proficiency_factor * importance
            matched_count += 1
        else:
            # Student missing this skill
            missing_skills.append({
                'skill_id': skill_id,
                'skill_name': req_skill.skill.skill_name,
                'importance_weight': float(importance),
                'priority': 'High' if importance >= Decimal('0.8') else 
                           'Medium' if importance >= Decimal('0.5') else 'Low'
            })
    
    # Calculate final percentage
    if total_weight > 0:
        readiness_score = float((matched_score / total_weight) * 100)
    else:
        readiness_score = 0.0
    
    # Determine readiness level
    if readiness_score >= 80:
        readiness_level = 'Ready'
    elif readiness_score >= 50:
        readiness_level = 'Developing'
    else:
        readiness_level = 'Entry-Level'
    
    return {
        'readiness_score': round(readiness_score, 2),
        'readiness_level': readiness_level,
        'matched_skills_count': matched_count,
        'required_skills_count': required_count,
        'skill_gap_count': required_count - matched_count,
        'missing_skills': sorted(missing_skills, key=lambda x: x['importance_weight'], reverse=True)
    }


def calculate_all_scores(session: Session) -> None:
    """
    Calculate readiness scores for ALL student-role combinations.
    Updates market_readiness_scores table.
    """
    from src.database.models import MarketReadinessScores
    
    students = session.query(Student).all()
    roles = session.query(JobRole).all()
    
    print(f"Calculating scores for {len(students)} students × {len(roles)} roles...")
    
    for student in students:
        for role in roles:
            result = calculate_readiness_score(student.student_id, role.role_id, session)
            
            # Upsert score record
            score_record = session.query(MarketReadinessScores).filter_by(
                student_id=student.student_id,
                role_id=role.role_id
            ).first()
            
            if score_record:
                # Update existing
                score_record.readiness_score = result['readiness_score']
                score_record.readiness_level = result['readiness_level']
                score_record.matched_skills_count = result['matched_skills_count']
                score_record.required_skills_count = result['required_skills_count']
                score_record.skill_gap_count = result['skill_gap_count']
                score_record.calculated_at = func.now()
            else:
                # Insert new
                score_record = MarketReadinessScores(
                    student_id=student.student_id,
                    role_id=role.role_id,
                    **result
                )
                session.add(score_record)
    
    session.commit()
    print("✓ All readiness scores calculated!")
```

---

## STREAMLIT DASHBOARD SPECIFICATIONS

### File: `src/dashboard/app.py`
```python
"""
University Placement Analytics Dashboard
Administrator View
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import func
from src.database.connection import get_db_session
from src.database.models import *

st.set_page_config(
    page_title="Placement Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 1rem;
}
.metric-card {
    background: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

def main():
    session = get_db_session()
    
    st.markdown('<h1 class="main-header">University Placement Readiness Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # === SECTION 1: KEY METRICS ===
    st.subheader("📊 Cohort Overview")
    
    total_students = session.query(Student).count()
    avg_readiness = session.query(func.avg(MarketReadinessScores.readiness_score)).scalar()
    ready_count = session.query(MarketReadinessScores).filter(
        MarketReadinessScores.readiness_level == 'Ready'
    ).count()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Students", total_students)
    with col2:
        st.metric("Avg Readiness", f"{avg_readiness:.1f}%")
    with col3:
        st.metric("Job-Ready Students", ready_count)
    with col4:
        last_updated = "2 hours ago"  # From ETL
        st.metric("Last Updated", last_updated)
    
    st.divider()
    
    # === SECTION 2: READINESS DISTRIBUTION (PIE CHART) ===
    st.subheader("🎯 Cohort Readiness Distribution")
    
    readiness_counts = session.query(
        MarketReadinessScores.readiness_level,
        func.count(MarketReadinessScores.id)
    ).group_by(MarketReadinessScores.readiness_level).all()
    
    df_readiness = pd.DataFrame(readiness_counts, columns=['Level', 'Count'])
    
    fig_pie = px.pie(
        df_readiness,
        values='Count',
        names='Level',
        color='Level',
        color_discrete_map={
            'Ready': '#28a745',
            'Developing': '#ffc107',
            'Entry-Level': '#dc3545'
        },
        hole=0.3
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_pie, use_container_width=True)
    
    st.divider()
    
    # === SECTION 3: PROGRAM COMPARISON (BAR CHART) ===
    st.subheader("📚 Average Readiness by Program")
    
    program_stats = session.query(
        Student.program,
        func.avg(MarketReadinessScores.readiness_score).label('avg_score'),
        func.count(Student.student_id).label('student_count')
    ).join(MarketReadinessScores).group_by(Student.program).all()
    
    df_program = pd.DataFrame(program_stats, columns=['Program', 'Avg Readiness', 'Students'])
    
    fig_bar = px.bar(
        df_program,
        x='Program',
        y='Avg Readiness',
        text='Avg Readiness',
        color='Avg Readiness',
        color_continuous_scale='Blues'
    )
    fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.divider()
    
    # === SECTION 4: TOP STUDENTS TABLE ===
    st.subheader("🏆 Top 10 Students by Readiness")
    
    top_students = session.query(
        Student.name,
        Student.program,
        Student.year_of_study,
        JobRole.role_name,
        MarketReadinessScores.readiness_score
    ).join(
        MarketReadinessScores, Student.student_id == MarketReadinessScores.student_id
    ).join(
        JobRole, MarketReadinessScores.role_id == JobRole.role_id
    ).order_by(
        MarketReadinessScores.readiness_score.desc()
    ).limit(10).all()
    
    df_top = pd.DataFrame(top_students, columns=['Name', 'Program', 'Year', 'Best Role', 'Score'])
    df_top['Score'] = df_top['Score'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(df_top, use_container_width=True, hide_index=True)
    
    session.close()

if __name__ == "__main__":
    main()
```

---

## PROJECT DIRECTORY STRUCTURE

```
placement-analytics/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── config/
│   └── database.py          # DB connection settings
├── data/
│   └── skill_taxonomy.json  # 200 skills categorized
├── src/
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   ├── connection.py    # Session management
│   │   └── init_db.py       # Create tables
│   ├── data_generation/
│   │   ├── __init__.py
│   │   ├── generate_students.py
│   │   ├── generate_skills.py
│   │   └── populate_db.py   # Main script
│   ├── core/
│   │   ├── __init__.py
│   │   └── scoring.py       # Readiness calculation
│   ├── etl/
│   │   ├── __init__.py
│   │   ├── pipeline.py      # ETL orchestration
│   │   └── scheduler.py     # APScheduler setup
│   ├── ml_models/
│   │   ├── __init__.py
│   │   ├── train_models.py
│   │   └── predict.py
│   └── dashboard/
│       ├── __init__.py
│       └── app.py           # Streamlit dashboard
├── notebooks/
│   └── exploration.ipynb
├── models/
│   ├── decision_tree.pkl
│   ├── random_forest.pkl
│   └── kmeans.pkl
└── tests/
    ├── test_scoring.py
    └── test_data_generation.py
```

---

## REQUIREMENTS.TXT

```txt
# Database
psycopg2-binary==2.9.9
SQLAlchemy==2.0.23

# Data Processing
pandas==2.1.4
numpy==1.26.2

# Synthetic Data
Faker==21.0.0

# Machine Learning
scikit-learn==1.3.2
joblib==1.3.2

# Dashboard
streamlit==1.29.0
plotly==5.18.0

# Automation
APScheduler==3.10.4

# Utilities
python-dotenv==1.0.0

# Development
pytest==7.4.3
jupyter==1.0.0
```

---

## GIT WORKFLOW

### Initial Commit Structure
```bash
# Commit 1
git add README.md requirements.txt .gitignore
git commit -m "feat: Initialize project structure"

# Commit 2
git add config/ src/database/
git commit -m "feat: Setup database schema and ORM models"

# Commit 3
git add src/data_generation/
git commit -m "feat: Implement synthetic data generation (500 students)"

# Commit 4
git add src/core/scoring.py
git commit -m "feat: Implement market readiness scoring algorithm"

# Commit 5
git add src/dashboard/app.py
git commit -m "feat: Build initial dashboard with 3 core visualizations"

# Tag MVP
git tag -a v1.0-mvp -m "MVP: 500 students, basic dashboard"
```

---

## SUCCESS METRICS

### MVP (End of Day 1)
- [ ] PostgreSQL with 500 students, 4000 skills
- [ ] 2500 readiness scores calculated
- [ ] Dashboard shows 3 charts correctly
- [ ] Average query time < 500ms
- [ ] 5+ Git commits

### Production (Day 7)
- [ ] PostgreSQL with 2000 students, 25,000 skills
- [ ] 24,000 readiness scores
- [ ] Dashboard with 10 visualizations
- [ ] ETL pipeline automated
- [ ] All 3 ML models trained
- [ ] 40+ Git commits
- [ ] Complete documentation

---

**END OF PRD**
