# University Placement Readiness Analytics System

A data-heavy, university-facing placement analytics dashboard that processes 2000+ student records through PostgreSQL and automated pipelines, delivering real-time insights on job market readiness.

## 🎯 Project Overview

This system helps university administrators track and analyze student job market readiness across multiple programs (BBA, BCA, B.Com) and job roles. It calculates Market Readiness Scores (0-100%) for each student-role combination using a weighted skill matching algorithm.

## 📋 MVP Status (Day 1)

**Current Phase:** Phase 1 - Project Setup & Database

**MVP Goals:**
- ✅ Project structure initialized
- ⏳ PostgreSQL database with 500 students
- ⏳ Core scoring algorithm
- ⏳ Streamlit dashboard with 3 visualizations

## 🏗️ Architecture

```
Synthetic Data Generator → PostgreSQL → ETL Pipeline → ML Models → Streamlit Dashboard
```

## 📁 Project Structure

```
placement-analytics/
├── config/          # Configuration files
├── data/            # Data files and taxonomies
├── src/
│   ├── database/    # Database models and connection
│   ├── data_generation/  # Synthetic data generation
│   ├── core/        # Core algorithms (scoring)
│   ├── etl/         # ETL pipeline
│   ├── ml_models/   # Machine learning models
│   └── dashboard/   # Streamlit dashboard
├── notebooks/       # Jupyter notebooks
├── models/          # Trained ML models
└── tests/           # Unit tests
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd placement-analytics
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Initialize database:
```bash
# (Coming in Phase 2)
```

## 📊 Database Schema

The system uses 6 main tables:
- `students` - Student information
- `skills_master` - Master skills catalog
- `student_skills` - Student-skill mappings with proficiency
- `job_roles` - Available job roles
- `job_role_skills` - Required skills per role
- `market_readiness_scores` - Calculated readiness scores

## 🔧 Development Phases

- **Phase 1:** Project Setup & Database ✅
- **Phase 2:** Synthetic Data Generation
- **Phase 3:** Scoring Algorithm
- **Phase 4:** Basic Dashboard
- **Phase 5:** Testing & Git

## 📝 License

This project is for educational purposes.

## 👤 Author

Aaryan Rai

---

For detailed specifications, see [PRD.md](PRD.md)

