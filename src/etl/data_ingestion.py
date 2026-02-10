"""
Main data ingestion orchestrator
Supports multiple data sources: synthetic, CSV, and future API integration
"""
import sys
from pathlib import Path
from typing import Optional, Dict
import pandas as pd

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.etl.csv_loader import load_students_csv, load_skills_csv
from src.database.connection import get_db_session
from src.database.models import Student, StudentSkills, SkillsMaster, JobRole

def ingest_from_csv(students_csv_path: str, skills_csv_path: Optional[str] = None) -> Dict:
    """
    Ingest data from CSV files.
    
    Args:
        students_csv_path: Path to students CSV file
        skills_csv_path: Optional path to skills CSV file
    
    Returns:
        Dictionary with ingestion results and statistics
    """
    results = {
        'success': False,
        'students_loaded': 0,
        'skills_loaded': 0,
        'errors': []
    }
    
    # Load students
    students_df, error = load_students_csv(students_csv_path)
    if error:
        results['errors'].append(f"Students CSV: {error}")
        return results
    
    if students_df is None or students_df.empty:
        results['errors'].append("Students CSV is empty or invalid")
        return results
    
    # Load skills if provided
    skills_df = None
    if skills_csv_path:
        skills_df, error = load_skills_csv(skills_csv_path)
        if error:
            results['errors'].append(f"Skills CSV: {error}")
            # Continue with students only
    
    # Insert into database
    session = get_db_session()
    try:
        # Insert students
        students_inserted = 0
        for _, row in students_df.iterrows():
            # Check if student already exists (by email)
            existing = session.query(Student).filter_by(email=row['email']).first()
            if existing:
                continue  # Skip duplicates
            
            student = Student(
                name=row['name'],
                email=row['email'],
                program=row['program'],
                year_of_study=int(row['year_of_study']),
                enrollment_year=int(row['enrollment_year']),
                target_role=row['target_role']
            )
            session.add(student)
            students_inserted += 1
        
        session.flush()
        results['students_loaded'] = students_inserted
        
        # Insert skills if provided
        if skills_df is not None and not skills_df.empty:
            skills_inserted = 0
            student_id_map = {s.email: s.student_id for s in session.query(Student).all()}
            
            for _, row in skills_df.iterrows():
                # Get student_id from email or direct ID
                student_id = None
                if 'student_id' in row and pd.notna(row['student_id']):
                    student_id = int(row['student_id'])
                elif 'email' in row:
                    student_id = student_id_map.get(row['email'])
                
                if not student_id:
                    continue  # Skip if student not found
                
                # Get skill from master
                skill = session.query(SkillsMaster).filter_by(skill_name=row['skill_name']).first()
                if not skill:
                    continue  # Skip if skill not in master
                
                # Check if student-skill combination already exists
                existing = session.query(StudentSkills).filter_by(
                    student_id=student_id,
                    skill_id=skill.skill_id
                ).first()
                if existing:
                    continue  # Skip duplicates
                
                # Calculate proficiency score
                proficiency_scores = {
                    'Beginner': 0.25,
                    'Intermediate': 0.50,
                    'Advanced': 0.75,
                    'Expert': 1.00
                }
                
                student_skill = StudentSkills(
                    student_id=student_id,
                    skill_id=skill.skill_id,
                    proficiency_level=row['proficiency_level'],
                    proficiency_score=proficiency_scores.get(row['proficiency_level'], 0.50),
                    acquisition_date=pd.to_datetime(row['acquisition_date']).date(),
                    source=row['source']
                )
                session.add(student_skill)
                skills_inserted += 1
            
            results['skills_loaded'] = skills_inserted
        
        session.commit()
        results['success'] = True
        
    except Exception as e:
        session.rollback()
        results['errors'].append(f"Database error: {str(e)}")
    finally:
        session.close()
    
    return results

def ingest_from_synthetic(num_students: int = 500) -> Dict:
    """
    Ingest data from synthetic generation (existing functionality).
    
    Args:
        num_students: Number of students to generate
    
    Returns:
        Dictionary with ingestion results
    """
    from src.data_generation.populate_db import populate_students_and_skills
    
    session = get_db_session()
    try:
        populate_students_and_skills(session, num_students=num_students, clear_existing=False)
        session.commit()
        
        return {
            'success': True,
            'students_loaded': num_students,
            'skills_loaded': 'variable',
            'errors': []
        }
    except Exception as e:
        session.rollback()
        return {
            'success': False,
            'students_loaded': 0,
            'skills_loaded': 0,
            'errors': [str(e)]
        }
    finally:
        session.close()

