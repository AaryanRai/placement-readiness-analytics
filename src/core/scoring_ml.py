"""
ML-based scoring system
Uses trained ML models to predict readiness scores and levels
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict
from sqlalchemy.orm import Session
from src.database.models import *
from src.ml_models.predict import predict_readiness_ml, predict_batch_ml

def calculate_readiness_score_ml(student_id: int, role_id: int, session: Session) -> Dict:
    """
    Calculate readiness score using ML models.
    
    Uses:
    - Random Forest Regressor for score prediction (0-100)
    - Decision Tree Classifier for level prediction
    
    Returns:
        {
            'readiness_score': float (0-100),
            'readiness_level': str,
            'matched_skills_count': int,
            'required_skills_count': int,
            'skill_gap_count': int,
            'model_used': 'ML'
        }
    """
    # Get ML prediction
    ml_result = predict_readiness_ml(student_id, role_id, session)
    
    if ml_result.get('error'):
        # Fallback to rule-based if ML fails
        from src.core.scoring import calculate_readiness_score
        rule_result = calculate_readiness_score(student_id, role_id, session)
        return {
            **rule_result,
            'model_used': 'Rule-based (ML unavailable)',
            'ml_error': ml_result.get('error')
        }
    
    # Get required skills count for metadata
    required_skills = session.query(JobRoleSkills).filter_by(role_id=role_id).all()
    required_count = len(required_skills)
    
    # Get student skills for metadata
    student_skills = session.query(StudentSkills).filter_by(student_id=student_id).all()
    student_skill_ids = {s.skill_id for s in student_skills}
    matched_count = sum(1 for req in required_skills if req.skill_id in student_skill_ids)
    
    return {
        'readiness_score': ml_result['readiness_score_ml'],
        'readiness_level': ml_result['readiness_level_ml'],
        'matched_skills_count': matched_count,
        'required_skills_count': required_count,
        'skill_gap_count': required_count - matched_count,
        'model_used': ml_result['model_used'],
        'ml_probabilities': ml_result.get('readiness_score_ml_probabilities')
    }

def calculate_all_scores_ml(session: Session, update_database: bool = True) -> None:
    """
    Calculate readiness scores for ALL student-role combinations using ML.
    
    Args:
        session: Database session
        update_database: If True, update market_readiness_scores table
    """
    from sqlalchemy import func
    
    students = session.query(Student).all()
    roles = session.query(JobRole).all()
    
    print(f"Calculating ML scores for {len(students)} students × {len(roles)} roles...")
    
    # Use batch prediction for efficiency
    predictions_df = predict_batch_ml(session)
    
    if predictions_df.empty:
        # If we cannot generate any predictions (e.g., models not trained yet),
        # raise an error so the caller can gracefully fall back to the
        # rule-based scoring pipeline.
        print("ERROR: No predictions generated. Check if models are trained.")
        raise RuntimeError("ML predictions unavailable (no predictions generated)")
    
    count = 0
    for _, row in predictions_df.iterrows():
        student_id = int(row['student_id'])
        role_id = int(row['role_id'])
        
        # Get metadata (matched skills, etc.)
        required_skills = session.query(JobRoleSkills).filter_by(role_id=role_id).all()
        required_count = len(required_skills)
        
        student_skills = session.query(StudentSkills).filter_by(student_id=student_id).all()
        student_skill_ids = {s.skill_id for s in student_skills}
        matched_count = sum(1 for req in required_skills if req.skill_id in student_skill_ids)
        
        if update_database:
            # Check if record exists (upsert logic)
            existing = session.query(MarketReadinessScores).filter_by(
                student_id=student_id,
                role_id=role_id
            ).first()
            
            if existing:
                # Update existing record with ML predictions
                existing.readiness_score = row['readiness_score_ml']
                existing.readiness_level = row['readiness_level_ml']
                existing.matched_skills_count = matched_count
                existing.required_skills_count = required_count
                existing.skill_gap_count = required_count - matched_count
            else:
                # Insert new record
                score_record = MarketReadinessScores(
                    student_id=student_id,
                    role_id=role_id,
                    readiness_score=row['readiness_score_ml'],
                    readiness_level=row['readiness_level_ml'],
                    matched_skills_count=matched_count,
                    required_skills_count=required_count,
                    skill_gap_count=required_count - matched_count
                )
                session.add(score_record)
        
        count += 1
        if count % 100 == 0:
            print(f"  Processed {count} scores...")
    
    if update_database:
        session.commit()
    
    print(f"✓ All {count} ML readiness scores calculated!")

if __name__ == "__main__":
    from src.database.connection import get_db_session
    session = get_db_session()
    try:
        calculate_all_scores_ml(session)
    finally:
        session.close()

