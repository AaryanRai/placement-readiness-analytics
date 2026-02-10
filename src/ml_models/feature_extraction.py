"""
Feature extraction for ML models
Extracts features from database for training and prediction
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.database.models import *
from src.database.connection import get_db_session

def extract_features_for_training(session: Session = None) -> pd.DataFrame:
    """
    Extract features from database for ML training.
    
    Features:
    - Student demographics: program, year_of_study, enrollment_year
    - Skill portfolio: total_skills, avg_proficiency, skill_counts_by_category
    - Role-specific: required_skills_count, matched_skills_count, skill_gap_count
    - Target variable: readiness_score, readiness_level
    
    Returns:
        DataFrame with features and target variables
    """
    if session is None:
        session = get_db_session()
        close_session = True
    else:
        close_session = False
    
    try:
        # Get all student-role score combinations
        scores = session.query(
            MarketReadinessScores.student_id,
            MarketReadinessScores.role_id,
            MarketReadinessScores.readiness_score,
            MarketReadinessScores.readiness_level,
            MarketReadinessScores.matched_skills_count,
            MarketReadinessScores.required_skills_count,
            MarketReadinessScores.skill_gap_count
        ).all()
        
        features_list = []
        
        for score in scores:
            student_id = score.student_id
            role_id = score.role_id
            
            # Get student info
            student = session.query(Student).filter_by(student_id=student_id).first()
            if not student:
                continue
            
            # Get role info
            role = session.query(JobRole).filter_by(role_id=role_id).first()
            if not role:
                continue
            
            # Get student skills
            student_skills = session.query(StudentSkills).filter_by(student_id=student_id).all()
            
            # Calculate skill portfolio features
            total_skills = len(student_skills)
            if total_skills > 0:
                avg_proficiency = float(sum(float(s.proficiency_score) for s in student_skills) / total_skills)
                max_proficiency = float(max(float(s.proficiency_score) for s in student_skills))
                min_proficiency = float(min(float(s.proficiency_score) for s in student_skills))
            else:
                avg_proficiency = 0.0
                max_proficiency = 0.0
                min_proficiency = 0.0
            
            # Count skills by category
            skill_categories = {}
            for skill_record in student_skills:
                skill = session.query(SkillsMaster).filter_by(skill_id=skill_record.skill_id).first()
                if skill:
                    category = skill.category
                    skill_categories[category] = skill_categories.get(category, 0) + 1
            
            # Count skills by proficiency level
            proficiency_counts = {'Beginner': 0, 'Intermediate': 0, 'Advanced': 0, 'Expert': 0}
            for skill_record in student_skills:
                proficiency_counts[skill_record.proficiency_level] = proficiency_counts.get(
                    skill_record.proficiency_level, 0
                ) + 1
            
            # Count skills by source
            source_counts = {'Course': 0, 'Certification': 0, 'Project': 0, 'Workshop': 0}
            for skill_record in student_skills:
                source_counts[skill_record.source] = source_counts.get(skill_record.source, 0) + 1
            
            # Program encoding
            program_encoded = {
                'program_BBA': 1 if student.program == 'BBA' else 0,
                'program_Btech': 1 if student.program == 'Btech' else 0,
                'program_B.Com': 1 if student.program == 'B.Com' else 0
            }
            
            # Role encoding
            role_encoded = {
                'role_Data Analyst': 1 if role.role_name == 'Data Analyst' else 0,
                'role_Full-Stack Developer': 1 if role.role_name == 'Full-Stack Developer' else 0,
                'role_Digital Marketer': 1 if role.role_name == 'Digital Marketer' else 0,
                'role_Business Analyst': 1 if role.role_name == 'Business Analyst' else 0,
                'role_UX/UI Designer': 1 if role.role_name == 'UX/UI Designer' else 0
            }
            
            # Build feature vector
            # NOTE: We intentionally exclude 'match_ratio' from ML features to avoid
            # an overly dominant shortcut feature. The models learn from underlying
            # portfolio and role features instead.
            features = {
                # Student demographics
                'year_of_study': student.year_of_study,
                'enrollment_year': student.enrollment_year,
                **program_encoded,
                
                # Skill portfolio
                'total_skills': total_skills,
                'avg_proficiency': avg_proficiency,
                'max_proficiency': max_proficiency,
                'min_proficiency': min_proficiency,
                
                # Skills by category
                'skills_Technical': skill_categories.get('Technical', 0),
                'skills_Business': skill_categories.get('Business', 0),
                'skills_Design': skill_categories.get('Design', 0),
                'skills_Soft Skills': skill_categories.get('Soft Skills', 0),
                
                # Skills by proficiency
                'proficiency_Beginner': proficiency_counts['Beginner'],
                'proficiency_Intermediate': proficiency_counts['Intermediate'],
                'proficiency_Advanced': proficiency_counts['Advanced'],
                'proficiency_Expert': proficiency_counts['Expert'],
                
                # Skills by source
                'source_Course': source_counts['Course'],
                'source_Certification': source_counts['Certification'],
                'source_Project': source_counts['Project'],
                'source_Workshop': source_counts['Workshop'],
                
                # Role-specific features (without direct match_ratio shortcut)
                'required_skills_count': score.required_skills_count,
                'matched_skills_count': score.matched_skills_count,
                'skill_gap_count': score.skill_gap_count,
                
                # Role encoding
                **role_encoded,
                
                # Target variables
                'readiness_score': float(score.readiness_score),
                'readiness_level': score.readiness_level
            }
            
            features_list.append(features)
        
        df = pd.DataFrame(features_list)
        return df
    
    finally:
        if close_session:
            session.close()

def extract_features_for_prediction(student_id: int, role_id: int, session: Session) -> pd.DataFrame:
    """
    Extract features for a single student-role pair for prediction.
    
    Returns:
        DataFrame with single row of features (without target variables)
    """
    # Get student info
    student = session.query(Student).filter_by(student_id=student_id).first()
    if not student:
        raise ValueError(f"Student {student_id} not found")
    
    # Get role info
    role = session.query(JobRole).filter_by(role_id=role_id).first()
    if not role:
        raise ValueError(f"Role {role_id} not found")
    
    # Get required skills for role
    required_skills = session.query(JobRoleSkills).filter_by(role_id=role_id).all()
    required_count = len(required_skills)
    
    # Get student skills
    student_skills = session.query(StudentSkills).filter_by(student_id=student_id).all()
    
    # Calculate skill portfolio features
    total_skills = len(student_skills)
    if total_skills > 0:
        avg_proficiency = float(sum(float(s.proficiency_score) for s in student_skills) / total_skills)
        max_proficiency = float(max(float(s.proficiency_score) for s in student_skills))
        min_proficiency = float(min(float(s.proficiency_score) for s in student_skills))
    else:
        avg_proficiency = 0.0
        max_proficiency = 0.0
        min_proficiency = 0.0
    
    # Count skills by category
    skill_categories = {}
    for skill_record in student_skills:
        skill = session.query(SkillsMaster).filter_by(skill_id=skill_record.skill_id).first()
        if skill:
            category = skill.category
            skill_categories[category] = skill_categories.get(category, 0) + 1
    
    # Count skills by proficiency level
    proficiency_counts = {'Beginner': 0, 'Intermediate': 0, 'Advanced': 0, 'Expert': 0}
    for skill_record in student_skills:
        proficiency_counts[skill_record.proficiency_level] = proficiency_counts.get(
            skill_record.proficiency_level, 0
        ) + 1
    
    # Count skills by source
    source_counts = {'Course': 0, 'Certification': 0, 'Project': 0, 'Workshop': 0}
    for skill_record in student_skills:
        source_counts[skill_record.source] = source_counts.get(skill_record.source, 0) + 1
    
    # Calculate matched skills
    student_skill_ids = {s.skill_id for s in student_skills}
    matched_count = sum(1 for req in required_skills if req.skill_id in student_skill_ids)
    skill_gap_count = required_count - matched_count
    
    # Program encoding
    program_encoded = {
        'program_BBA': 1 if student.program == 'BBA' else 0,
        'program_Btech': 1 if student.program == 'Btech' else 0,
        'program_B.Com': 1 if student.program == 'B.Com' else 0
    }
    
    # Role encoding
    role_encoded = {
        'role_Data Analyst': 1 if role.role_name == 'Data Analyst' else 0,
        'role_Full-Stack Developer': 1 if role.role_name == 'Full-Stack Developer' else 0,
        'role_Digital Marketer': 1 if role.role_name == 'Digital Marketer' else 0,
        'role_Business Analyst': 1 if role.role_name == 'Business Analyst' else 0,
        'role_UX/UI Designer': 1 if role.role_name == 'UX/UI Designer' else 0
    }
    
    # Build feature vector
    # NOTE: We intentionally exclude 'match_ratio' from ML features to avoid
    # an overly dominant shortcut feature. The models learn from underlying
    # portfolio and role features instead.
    features = {
        # Student demographics
        'year_of_study': student.year_of_study,
        'enrollment_year': student.enrollment_year,
        **program_encoded,
        
        # Skill portfolio
        'total_skills': total_skills,
        'avg_proficiency': avg_proficiency,
        'max_proficiency': max_proficiency,
        'min_proficiency': min_proficiency,
        
        # Skills by category
        'skills_Technical': skill_categories.get('Technical', 0),
        'skills_Business': skill_categories.get('Business', 0),
        'skills_Design': skill_categories.get('Design', 0),
        'skills_Soft Skills': skill_categories.get('Soft Skills', 0),
        
        # Skills by proficiency
        'proficiency_Beginner': proficiency_counts['Beginner'],
        'proficiency_Intermediate': proficiency_counts['Intermediate'],
        'proficiency_Advanced': proficiency_counts['Advanced'],
        'proficiency_Expert': proficiency_counts['Expert'],
        
        # Skills by source
        'source_Course': source_counts['Course'],
        'source_Certification': source_counts['Certification'],
        'source_Project': source_counts['Project'],
        'source_Workshop': source_counts['Workshop'],
        
        # Role-specific features (without direct match_ratio shortcut)
        'required_skills_count': required_count,
        'matched_skills_count': matched_count,
        'skill_gap_count': skill_gap_count,
        
        # Role encoding
        **role_encoded
    }
    
    return pd.DataFrame([features])

