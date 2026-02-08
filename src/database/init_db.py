"""
Initialize database: Create all tables
"""
from src.database.connection import create_tables, engine
from src.database.models import Base

def main():
    """Create all database tables"""
    print("Creating database tables...")
    create_tables()
    print("✓ Database tables created successfully!")
    print(f"Database: {engine.url}")

if __name__ == "__main__":
    main()

