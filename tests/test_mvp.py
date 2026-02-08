import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from src.database.connection import get_db_session
from src.database.models import *
from src.core.scoring import calculate_readiness_score

def test_database_populated():
    """Verify database has data."""
    session = get_db_session()
    
    assert session.query(Student).count() == 500, "Should have 500 students"
    assert session.query(JobRole).count() == 5, "Should have 5 job roles"
    assert session.query(MarketReadinessScores).count() == 2500, "Should have 2500 scores"
    
    session.close()

def test_scoring_algorithm():
    """Test scoring calculation."""
    session = get_db_session()
    
    # Get a student and role
    student = session.query(Student).first()
    role = session.query(JobRole).first()
    
    result = calculate_readiness_score(student.student_id, role.role_id, session)
    
    assert 0 <= result['readiness_score'] <= 100, "Score must be 0-100"
    assert result['readiness_level'] in ['Ready', 'Developing', 'Entry-Level']
    assert result['matched_skills_count'] >= 0
    
    session.close()

def test_dashboard_data():
    """Verify dashboard queries work."""
    session = get_db_session()
    
    # Test readiness distribution query
    from sqlalchemy import func
    counts = session.query(
        MarketReadinessScores.readiness_level,
        func.count(MarketReadinessScores.id)
    ).group_by(MarketReadinessScores.readiness_level).all()
    
    assert len(counts) > 0, "Should have readiness data"
    
    session.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

