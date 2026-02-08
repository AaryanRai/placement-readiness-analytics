# Quick Start Guide

## Prerequisites Checklist

Before running the application, ensure you have:

- [ ] Python 3.8+ installed
- [ ] PostgreSQL installed and running
- [ ] Database `placement_analytics` created
- [ ] `.env` file configured with PostgreSQL credentials

## Step-by-Step Setup

### 1. Install PostgreSQL

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

See `POSTGRESQL_SETUP.md` for detailed instructions.

### 2. Create Database

```bash
createdb placement_analytics
```

### 3. Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit .env with your PostgreSQL credentials
# Use your favorite editor:
nano .env
# or
vim .env
# or
code .env
```

Edit these values in `.env`:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=placement_analytics
DB_USER=postgres
DB_PASSWORD=your_actual_password_here
```

### 4. Install Python Dependencies

```bash
# Install all dependencies
pip3 install psycopg2-binary SQLAlchemy pandas numpy Faker scikit-learn joblib streamlit plotly APScheduler python-dotenv pytest jupyter

# Or use requirements.txt (may need to fix psycopg2 version)
pip3 install -r requirements.txt
```

### 5. Run Complete Pipeline

**Option A: Automated Script**
```bash
./run.sh
```

**Option B: Manual Steps**
```bash
# Step 1: Initialize database
python src/database/init_db.py

# Step 2: Populate data
python src/data_generation/populate_db.py

# Step 3: Calculate scores
python src/core/scoring.py

# Step 4: Launch dashboard
streamlit run src/dashboard/app.py
```

## Verification

After setup, verify everything works:

```bash
# Check PostgreSQL connection
pg_isready

# Check database exists
psql -l | grep placement_analytics

# Test Python connection
python3 -c "from src.database.connection import get_db_session; s = get_db_session(); print('✓ Connected!'); s.close()"
```

## Common Issues

### Issue: "Connection refused"
**Solution:** PostgreSQL is not running. Start it:
- macOS: `brew services start postgresql@14`
- Linux: `sudo systemctl start postgresql`

### Issue: "psycopg2 not found"
**Solution:** Install it:
```bash
pip3 install psycopg2-binary
```

### Issue: "Database does not exist"
**Solution:** Create it:
```bash
createdb placement_analytics
```

### Issue: "Authentication failed"
**Solution:** Check your `.env` file has correct password for postgres user.

## Next Steps

Once everything is running:

1. **Access Dashboard:** Open http://localhost:8501 in your browser
2. **View Data:** Check all 3 visualizations are displaying
3. **Explore:** Review student readiness scores and program comparisons

For detailed troubleshooting, see `POSTGRESQL_SETUP.md` and `README.md`.

