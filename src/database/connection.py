from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.database import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db_session():
    return SessionLocal()

