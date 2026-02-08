import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from decimal import Decimal
from typing import Dict
from sqlalchemy.orm import Session
from src.database.models import *

PROFICIENCY_MAP = {
    'Beginner': Decimal('0.25'),
    'Intermediate': Decimal('0.50'),
    'Advanced': Decimal('0.75'),
    'Expert': Decimal('1.00')
}

def calculate_readiness_score(student_id: int, role_id: int, session: Session, use_ml: bool = True) -> Dict:
    """
    Calculate market readiness score using ML models (default) or rule-based algorithm.
    
    By default, uses ML models for prediction. Falls back to rule-based if ML unavailable.
    
    ML Approach:
    - Uses trained Random Forest Regressor for score prediction
    - Uses trained Decision Tree Classifier for level prediction
    
    Rule-Based Algorithm (fallback):
    Score = (Σ matched_skill_proficiency × importance_weight) / Σ required_weights × 100
    
    Readiness Levels:
    - 80-100% = Ready
    - 50-79% = Developing
    - 0-49% = Entry-Level
    
    Args:
        student_id: Student ID
        role_id: Role ID
        session: Database session
        use_ml: If True, use ML models (default). If False, use rule-based.
    
    Returns:
        {
            'readiness_score': float (0-100),
            'readiness_level': str,
            'matched_skills_count': int,
            'required_skills_count': int,
            'skill_gap_count': int,
            'missing_skills': list,
            'model_used': str
        }
    """
    # Try ML first if requested
    if use_ml:
        try:
            from src.ml_models.predict import predict_readiness_ml
            ml_result = predict_readiness_ml(student_id, role_id, session)
            
            if not ml_result.get('error'):
                # Get metadata for ML result
                required_skills = session.query(JobRoleSkills).filter_by(role_id=role_id).all()
                required_count = len(required_skills)
                
                student_skills = session.query(StudentSkills).filter_by(student_id=student_id).all()
                student_skill_ids = {s.skill_id for s in student_skills}
                matched_count = sum(1 for req in required_skills if req.skill_id in student_skill_ids)
                
                return {
                    'readiness_score': ml_result['readiness_score_ml'],
                    'readiness_level': ml_result['readiness_level_ml'],
                    'matched_skills_count': matched_count,
                    'required_skills_count': required_count,
                    'skill_gap_count': required_count - matched_count,
                    'missing_skills': [],
                    'model_used': 'ML (Random Forest + Decision Tree)'
                }
        except Exception as e:
            # Fall through to rule-based if ML fails
            pass
    # Get required skills for role
    required_skills = session.query(JobRoleSkills).filter_by(role_id=role_id).all()
    
    if not required_skills:
        return {
            'readiness_score': 0,
            'readiness_level': 'Entry-Level',
            'matched_skills_count': 0,
            'required_skills_count': 0,
            'skill_gap_count': 0,
            'missing_skills': []
        }
    
    required_count = len(required_skills)
    total_weight = sum(Decimal(str(skill.importance_weight)) for skill in required_skills)
    
    # Get student's skills
    student_skills = session.query(StudentSkills).filter_by(student_id=student_id).all()
    student_skill_map = {
        skill.skill_id: Decimal(str(skill.proficiency_score)) 
        for skill in student_skills
    }
    
    # Calculate weighted score
    matched_score = Decimal('0')
    matched_count = 0
    missing_skills = []
    
    for req_skill in required_skills:
        skill_id = req_skill.skill_id
        required_prof = PROFICIENCY_MAP[req_skill.required_proficiency]
        importance = Decimal(str(req_skill.importance_weight))
        
        if skill_id in student_skill_map:
            # Student has this skill
            student_prof = student_skill_map[skill_id]
            
            # Partial credit if proficiency is lower than required
            proficiency_factor = min(student_prof / required_prof, Decimal('1.0'))
            matched_score += proficiency_factor * importance
            matched_count += 1
        else:
            # Student missing this skill
            skill = session.query(SkillsMaster).filter_by(skill_id=skill_id).first()
            missing_skills.append({
                'skill_id': skill_id,
                'skill_name': skill.skill_name if skill else f'Skill {skill_id}',
                'importance_weight': float(importance)
            })
    
    # Calculate final percentage
    if total_weight > 0:
        readiness_score = float((matched_score / total_weight) * 100)
    else:
        readiness_score = 0.0
    
    # Determine readiness level
    if readiness_score >= 80:
        readiness_level = 'Ready'
    elif readiness_score >= 50:
        readiness_level = 'Developing'
    else:
        readiness_level = 'Entry-Level'
    
    return {
        'readiness_score': round(readiness_score, 2),
        'readiness_level': readiness_level,
        'matched_skills_count': matched_count,
        'required_skills_count': required_count,
        'skill_gap_count': required_count - matched_count,
        'missing_skills': sorted(missing_skills, key=lambda x: x['importance_weight'], reverse=True),
        'model_used': 'Rule-based (weighted skill matching)'
    }

def calculate_all_scores(session: Session, use_ml: bool = True) -> None:
    """
    Calculate readiness scores for ALL student-role combinations using ML (default) or rule-based.
    Updates market_readiness_scores table.
    
    For 500 students × 5 roles = 2500 score records
    
    Args:
        session: Database session
        use_ml: If True (default), use ML models. If False, use rule-based algorithm.
    """
    from sqlalchemy import func
    
    # If ML requested, use ML batch prediction
    if use_ml:
        try:
            from src.core.scoring_ml import calculate_all_scores_ml
            calculate_all_scores_ml(session, update_database=True)
            return
        except Exception as e:
            print(f"ML scoring failed, falling back to rule-based: {e}")
            # Fall through to rule-based
    
    # Rule-based calculation
    students = session.query(Student).all()
    roles = session.query(JobRole).all()
    
    print(f"Calculating scores for {len(students)} students × {len(roles)} roles...")
    
    count = 0
    for student in students:
        for role in roles:
            result = calculate_readiness_score(student.student_id, role.role_id, session, use_ml=False)
            
            # Check if record exists (upsert logic)
            existing = session.query(MarketReadinessScores).filter_by(
                student_id=student.student_id,
                role_id=role.role_id
            ).first()
            
            if existing:
                # Update existing record
                existing.readiness_score = result['readiness_score']
                existing.readiness_level = result['readiness_level']
                existing.matched_skills_count = result['matched_skills_count']
                existing.required_skills_count = result['required_skills_count']
                existing.skill_gap_count = result['skill_gap_count']
            else:
                # Insert new record
                score_record = MarketReadinessScores(
                    student_id=student.student_id,
                    role_id=role.role_id,
                    readiness_score=result['readiness_score'],
                    readiness_level=result['readiness_level'],
                    matched_skills_count=result['matched_skills_count'],
                    required_skills_count=result['required_skills_count'],
                    skill_gap_count=result['skill_gap_count']
                )
                session.add(score_record)
            
            count += 1
            
            if count % 100 == 0:
                print(f"  Processed {count} scores...")
    
    session.commit()
    print(f"✓ All {count} readiness scores calculated!")

if __name__ == "__main__":
    import sys
    from pathlib import Path
    # Add project root to Python path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from src.database.connection import get_db_session
    session = get_db_session()
    calculate_all_scores(session)
    session.close()
