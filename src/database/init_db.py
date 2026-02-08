"""
Database initialization script
Creates all tables in the PostgreSQL database
"""
from src.database.connection import engine
from src.database.models import Base


def init_database():
    """
    Create all database tables.
    This will create the tables if they don't exist.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")


def drop_database():
    """
    Drop all database tables.
    WARNING: This will delete all data!
    """
    print("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        confirm = input("Are you sure you want to drop all tables? (yes/no): ")
        if confirm.lower() == "yes":
            drop_database()
        else:
            print("Operation cancelled.")
    else:
        init_database()

