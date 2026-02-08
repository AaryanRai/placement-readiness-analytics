"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config.database import DATABASE_URL

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


def get_db_session():
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


def close_db_session():
    """Close the current database session."""
    SessionLocal.remove()

