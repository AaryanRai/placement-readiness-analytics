"""
Utility script to align the students.program CHECK constraint with the
application model (BBA, Btech, B.Com).

This is mainly needed for existing databases that were created before
the program list was updated from BCA to Btech.
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from src.database.connection import get_engine


def fix_program_check_constraint() -> None:
    engine = get_engine()
    ddl_drop = "ALTER TABLE students DROP CONSTRAINT IF EXISTS check_program"
    ddl_add = (
        "ALTER TABLE students "
        "ADD CONSTRAINT check_program "
        "CHECK (program IN ('BBA','Btech','B.Com'))"
    )

    with engine.begin() as conn:
        conn.execute(text(ddl_drop))
        conn.execute(text(ddl_add))

    print("✓ Updated students.program CHECK constraint to allow BBA, Btech, B.Com")


if __name__ == "__main__":
    fix_program_check_constraint()


