# University Placement Readiness Analytics System

A data-heavy, university-facing placement analytics dashboard that processes student records through PostgreSQL and automated pipelines, delivering real-time insights on job market readiness.

## MVP Status

**Current Version:** MVP (Day 1)  
**Target:** 500 students, core scoring algorithm, 3-chart dashboard

## Project Structure

```
placement-analytics/
├── config/          # Configuration files
├── data/            # Data files and taxonomies
├── src/             # Source code
│   ├── database/    # Database models and connection
│   ├── data_generation/  # Synthetic data generation
│   ├── core/        # Core algorithms (scoring)
│   └── dashboard/   # Streamlit dashboard
├── models/          # ML models (future)
└── tests/           # Test files
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database:
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

3. Initialize database:
```bash
python src/database/init_db.py
```

4. Generate data:
```bash
python src/data_generation/populate_db.py
```

5. Run dashboard:
```bash
streamlit run src/dashboard/app.py
```

## Development Status

- [x] Project structure
- [ ] Database schema
- [ ] Data generation
- [ ] Scoring algorithm
- [ ] Dashboard

