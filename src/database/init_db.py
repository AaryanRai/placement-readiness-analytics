from src.database.connection import Base, engine
from src.database.models import *

def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    print("✓ Tables created successfully!")

if __name__ == "__main__":
    create_tables()

