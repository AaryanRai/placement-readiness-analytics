from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.database import DATABASE_URL

# Lazy initialization - only create engine when needed
_engine = None
_SessionLocal = None
Base = declarative_base()

def get_engine():
    """Get or create the database engine (lazy initialization)."""
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL)
    return _engine

def get_db_session():
    """Get a database session."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine())
    return _SessionLocal()

