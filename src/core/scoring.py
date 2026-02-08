"""
Market Readiness Score Calculation Engine
"""
from decimal import Decimal
from typing import Dict
from sqlalchemy.orm import Session
from src.database.models import Student, JobRole, JobRoleSkills, StudentSkills, MarketReadinessScores
from sqlalchemy import func

PROFICIENCY_MAP = {
    'Beginner': Decimal('0.25'),
    'Intermediate': Decimal('0.50'),
    'Advanced': Decimal('0.75'),
    'Expert': Decimal('1.00')
}


def calculate_readiness_score(student_id: int, role_id: int, session: Session) -> Dict:
    """
    Calculate market readiness score using weighted skill matching.
    
    Algorithm:
    1. Get all required skills for the job role
    2. Get student's current skills
    3. For each required skill:
       - If student has it: calculate proficiency_factor = min(student_prof / required_prof, 1.0)
       - Add (proficiency_factor × importance_weight) to score
    4. Final score = (total_matched_score / sum_of_all_weights) × 100
    
    Returns:
        {
            'readiness_score': 0-100,
            'readiness_level': 'Ready' | 'Developing' | 'Entry-Level',
            'matched_skills_count': int,
            'required_skills_count': int,
            'skill_gap_count': int,
            'missing_skills': [{skill_name, importance_weight}]
        }
    """
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
            missing_skills.append({
                'skill_id': skill_id,
                'skill_name': req_skill.skill.skill_name,
                'importance_weight': float(importance),
                'priority': 'High' if importance >= Decimal('0.8') else 
                           'Medium' if importance >= Decimal('0.5') else 'Low'
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
        'missing_skills': sorted(missing_skills, key=lambda x: x['importance_weight'], reverse=True)
    }


def calculate_all_scores(session: Session) -> None:
    """
    Calculate readiness scores for ALL student-role combinations.
    Updates market_readiness_scores table.
    """
    students = session.query(Student).all()
    roles = session.query(JobRole).all()
    
    print(f"Calculating scores for {len(students)} students × {len(roles)} roles...")
    
    for student in students:
        for role in roles:
            result = calculate_readiness_score(student.student_id, role.role_id, session)
            
            # Upsert score record
            score_record = session.query(MarketReadinessScores).filter_by(
                student_id=student.student_id,
                role_id=role.role_id
            ).first()
            
            if score_record:
                # Update existing
                score_record.readiness_score = result['readiness_score']
                score_record.readiness_level = result['readiness_level']
                score_record.matched_skills_count = result['matched_skills_count']
                score_record.required_skills_count = result['required_skills_count']
                score_record.skill_gap_count = result['skill_gap_count']
                score_record.calculated_at = func.now()
            else:
                # Insert new
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
    
    session.commit()
    print("✓ All readiness scores calculated!")

