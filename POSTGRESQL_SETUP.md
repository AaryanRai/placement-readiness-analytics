# PostgreSQL Setup Guide

This guide will help you install and configure PostgreSQL for the Placement Readiness Analytics System.

## 🔍 Check Current Status

First, check if PostgreSQL is already installed and running:

```bash
# Check if PostgreSQL is installed
which psql

# Check if PostgreSQL server is running
pg_isready
```

## 📦 Installation

### macOS (using Homebrew - Recommended)

```bash
# Install PostgreSQL
brew install postgresql@14

# Start PostgreSQL service
brew services start postgresql@14

# Verify it's running
pg_isready
```

**Alternative for macOS:** Download [Postgres.app](https://postgresapp.com/) - a simple GUI app.

### Linux (Ubuntu/Debian)

```bash
# Install PostgreSQL
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql  # Start on boot

# Verify it's running
sudo systemctl status postgresql
```

### Linux (CentOS/RHEL)

```bash
# Install PostgreSQL
sudo yum install postgresql-server postgresql-contrib

# Initialize database
sudo postgresql-setup initdb

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify it's running
sudo systemctl status postgresql
```

### Windows

1. Download PostgreSQL from: https://www.postgresql.org/download/windows/
2. Run the installer
3. During installation, set a password for the `postgres` user
4. PostgreSQL service will start automatically

## 🔧 Configuration

### 1. Set PostgreSQL Password (if not set)

```bash
# Connect to PostgreSQL
psql postgres

# Set password for postgres user
ALTER USER postgres PASSWORD 'your_password_here';

# Exit
\q
```

### 2. Create Database

```bash
# Create the database
createdb placement_analytics

# Verify it was created
psql -l | grep placement_analytics
```

### 3. Configure .env File

Edit the `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=placement_analytics
DB_USER=postgres
DB_PASSWORD=your_password_here
```

Replace `your_password_here` with the password you set for the postgres user.

## ✅ Verification

Test your PostgreSQL connection:

```bash
# Test connection
psql -h localhost -U postgres -d placement_analytics

# If successful, you'll see:
# placement_analytics=#
# Type \q to exit
```

Or test from Python:

```bash
python3 -c "
from config.database import DATABASE_CONFIG
import psycopg2
conn = psycopg2.connect(
    host=DATABASE_CONFIG['host'],
    port=DATABASE_CONFIG['port'],
    user=DATABASE_CONFIG['user'],
    password=DATABASE_CONFIG['password'],
    database=DATABASE_CONFIG['database']
)
print('✓ Connection successful!')
conn.close()
"
```

## 🐛 Troubleshooting

### PostgreSQL Not Running

**macOS:**
```bash
# Check status
brew services list

# Start service
brew services start postgresql@14

# Or manually
pg_ctl -D /usr/local/var/postgresql@14 start
```

**Linux:**
```bash
# Check status
sudo systemctl status postgresql

# Start service
sudo systemctl start postgresql

# Check logs if issues
sudo journalctl -u postgresql
```

### Connection Refused

1. **Check if PostgreSQL is running:**
   ```bash
   pg_isready
   ```

2. **Check PostgreSQL port:**
   ```bash
   # Default is 5432
   lsof -i :5432
   ```

3. **Check PostgreSQL configuration:**
   ```bash
   # Find config file
   psql -U postgres -c "SHOW config_file;"
   
   # Edit to allow local connections (usually already enabled)
   # Look for: listen_addresses = 'localhost'
   ```

### Authentication Failed

1. **Check pg_hba.conf:**
   ```bash
   # Find location
   psql -U postgres -c "SHOW hba_file;"
   
   # Ensure local connections are allowed:
   # local   all   all   md5
   # host    all   all   127.0.0.1/32   md5
   ```

2. **Reset postgres password:**
   ```bash
   # Connect as postgres user
   sudo -u postgres psql
   
   # Change password
   ALTER USER postgres PASSWORD 'new_password';
   ```

### Database Already Exists

If you get "database already exists" error:

```bash
# Drop and recreate (WARNING: Deletes all data!)
dropdb placement_analytics
createdb placement_analytics
```

## 🚀 Next Steps

Once PostgreSQL is configured:

1. **Run setup:**
   ```bash
   ./setup.sh
   ```

2. **Initialize database:**
   ```bash
   python src/database/init_db.py
   ```

3. **Populate data:**
   ```bash
   python src/data_generation/populate_db.py
   ```

4. **Calculate scores:**
   ```bash
   python src/core/scoring.py
   ```

5. **Launch dashboard:**
   ```bash
   streamlit run src/dashboard/app.py
   ```

## 📚 Additional Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- psycopg2 Documentation: https://www.psycopg.org/docs/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/

