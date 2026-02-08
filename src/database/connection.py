"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.database import DATABASE_URL

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Session:
    """
    Get a database session.
    Usage:
        session = get_db_session()
        try:
            # Use session
            pass
        finally:
            session.close()
    """
    return SessionLocal()


def create_tables():
    """Create all database tables"""
    from src.database.models import Base
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (use with caution!)"""
    from src.database.models import Base
    Base.metadata.drop_all(bind=engine)

