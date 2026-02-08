import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.database.connection import Base, get_engine
from src.database.models import *

def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("✓ Tables created successfully!")

if __name__ == "__main__":
    create_tables()

