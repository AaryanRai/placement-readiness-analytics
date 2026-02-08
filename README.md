# University Placement Readiness Analytics System

A data-heavy, university-facing placement analytics dashboard that processes student records through PostgreSQL and automated pipelines, delivering real-time insights on job market readiness.

## 🎯 MVP Status

**Current Version:** MVP (Day 1)  
**Status:** ✅ Complete and Ready for Deployment

**Features:**
- ✅ PostgreSQL database with 6 tables
- ✅ 500 synthetic students with skill profiles
- ✅ Market readiness scoring algorithm
- ✅ Streamlit dashboard with 3 core visualizations
- ✅ Complete data pipeline

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Run setup script
./setup.sh

# Then run complete pipeline
./run.sh
```

### Option 2: Manual Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Database**
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL credentials
   ```

3. **Create PostgreSQL Database**
   ```bash
   createdb placement_analytics
   ```

4. **Initialize Database Schema**
   ```bash
   python src/database/init_db.py
   ```

5. **Populate with Synthetic Data**
   ```bash
   python src/data_generation/populate_db.py
   ```

6. **Calculate Readiness Scores**
   ```bash
   python src/core/scoring.py
   ```

7. **Launch Dashboard**
   ```bash
   streamlit run src/dashboard/app.py
   ```

## 📁 Project Structure

```
placement-analytics/
├── config/              # Configuration files
│   ├── __init__.py
│   └── database.py      # Database connection settings
├── data/                # Data files
│   └── skill_taxonomy.json  # 47 skills categorized
├── src/                 # Source code
│   ├── database/        # Database layer
│   │   ├── models.py    # SQLAlchemy ORM models
│   │   ├── connection.py # Database connection
│   │   └── init_db.py   # Database initialization
│   ├── data_generation/ # Synthetic data generation
│   │   ├── generate_students.py
│   │   ├── generate_skills.py
│   │   └── populate_db.py
│   ├── core/            # Core algorithms
│   │   └── scoring.py   # Readiness scoring algorithm
│   └── dashboard/       # Streamlit dashboard
│       └── app.py       # Main dashboard application
├── models/              # ML models (future)
├── tests/               # Test files
├── setup.sh             # Automated setup script
├── run.sh               # Complete pipeline runner
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## 🗄️ Database Schema

The system uses 6 PostgreSQL tables:

1. **students** - Student records (500 records)
2. **skills_master** - Skills taxonomy (47 skills)
3. **student_skills** - Student-skill mappings (~4,000-8,000 records)
4. **job_roles** - Job role definitions (5 roles)
5. **job_role_skills** - Role skill requirements (27 requirements)
6. **market_readiness_scores** - Calculated scores (2,500 records)

## 📊 Dashboard Features

The Streamlit dashboard includes:

1. **Cohort Overview Metrics**
   - Total students
   - Average readiness score
   - Job-ready students count

2. **Readiness Distribution (Pie Chart)**
   - Ready (80-100%)
   - Developing (50-79%)
   - Entry-Level (0-49%)

3. **Program Comparison (Bar Chart)**
   - Average readiness by program (BBA, Btech, B.Com)
   - Student counts per program

4. **Top 10 Students Table**
   - Ranked by readiness score
   - Shows program, year, and target role

## 🔧 Configuration

Edit `.env` file with your PostgreSQL credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=placement_analytics
DB_USER=postgres
DB_PASSWORD=your_password_here
```

## 🐛 Troubleshooting

### ModuleNotFoundError
If you get import errors, ensure you're running scripts from the project root:
```bash
cd /path/to/Career\ Readiness\ Prediction
```

### Database Connection Errors
1. Verify PostgreSQL is running: `pg_isready`
2. Check credentials in `.env` file
3. Ensure database exists: `createdb placement_analytics`

### Empty Dashboard
If dashboard shows no data:
1. Verify data was populated: `python src/data_generation/populate_db.py`
2. Verify scores were calculated: `python src/core/scoring.py`

## 📈 Next Steps (Future Enhancements)

- [ ] Scale to 2000 students
- [ ] Add ML models (Decision Tree, Random Forest, K-Means)
- [ ] Implement ETL automation with APScheduler
- [ ] Add 10+ visualizations
- [ ] Export functionality (CSV, PDF reports)
- [ ] User authentication
- [ ] Student-facing portal

## 📝 Development Status

- [x] Project structure
- [x] Database schema
- [x] Data generation
- [x] Scoring algorithm
- [x] Dashboard
- [x] Error handling
- [x] Documentation

## 📄 License

This project is part of a university placement readiness analytics system.

## 👤 Author

Aaryan Rai

---

**Last Updated:** February 2026
