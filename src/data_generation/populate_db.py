import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import json
from sqlalchemy import func
from src.database.connection import get_db_session
from src.database.models import *
from src.data_generation.generate_students import generate_students
from src.data_generation.generate_skills import (
    load_skill_taxonomy, 
    generate_student_skills, 
    flatten_skills
)

def populate_skills_master(session, taxonomy):
    """Populate skills_master table (idempotent)."""
    print("Populating skills_master...")
    
    existing_count = session.query(SkillsMaster).count()
    if existing_count > 0:
        print(f"  Skills already exist ({existing_count} skills). Skipping...")
        return
    
    for category, subcats in taxonomy.items():
        if isinstance(subcats, dict):
            for subcat, skill_list in subcats.items():
                for skill_name in skill_list:
                    # Check if skill already exists
                    existing = session.query(SkillsMaster).filter_by(skill_name=skill_name).first()
                    if not existing:
                        skill = SkillsMaster(
                            skill_name=skill_name,
                            category=category,
                            subcategory=subcat
                        )
                        session.add(skill)
        else:  # Soft Skills
            for skill_name in subcats:
                # Check if skill already exists
                existing = session.query(SkillsMaster).filter_by(skill_name=skill_name).first()
                if not existing:
                    skill = SkillsMaster(
                        skill_name=skill_name,
                        category=category,
                        subcategory=None
                    )
                    session.add(skill)
    
    session.commit()
    print("✓ Skills master populated!")

def populate_job_roles(session):
    """Populate job_roles and job_role_skills tables (idempotent)."""
    print("Populating job roles...")
    
    existing_count = session.query(JobRole).count()
    if existing_count > 0:
        print(f"  Job roles already exist ({existing_count} roles). Skipping...")
        return
    
    # Define 5 job roles with their skill requirements
    roles_config = {
        'Data Analyst': {
            'category': 'Data',
            'skills': [
                ('Python', 'Intermediate', 1.0, True),
                ('SQL', 'Intermediate', 1.0, True),
                ('Excel', 'Advanced', 0.9, True),
                ('Tableau', 'Intermediate', 0.8, True),
                ('Statistics', 'Intermediate', 0.9, True),
                ('Pandas', 'Intermediate', 0.7, False),
                ('Power BI', 'Beginner', 0.5, False)
            ]
        },
        'Full-Stack Developer': {
            'category': 'Development',
            'skills': [
                ('JavaScript', 'Advanced', 1.0, True),
                ('React', 'Intermediate', 1.0, True),
                ('Node.js', 'Intermediate', 1.0, True),
                ('SQL', 'Intermediate', 0.8, True),
                ('HTML/CSS', 'Advanced', 0.9, True),
                ('PostgreSQL', 'Intermediate', 0.7, False)
            ]
        },
        'Digital Marketer': {
            'category': 'Marketing',
            'skills': [
                ('SEO', 'Intermediate', 1.0, True),
                ('Google Ads', 'Intermediate', 1.0, True),
                ('Social Media Marketing', 'Advanced', 1.0, True),
                ('Content Strategy', 'Intermediate', 0.9, True),
                ('Excel', 'Intermediate', 0.7, False)
            ]
        },
        'Business Analyst': {
            'category': 'Business',
            'skills': [
                ('Business Intelligence', 'Intermediate', 1.0, True),
                ('Excel', 'Advanced', 1.0, True),
                ('SQL', 'Intermediate', 0.9, True),
                ('Requirements Gathering', 'Intermediate', 0.8, True),
                ('Power BI', 'Intermediate', 0.7, False)
            ]
        },
        'UX/UI Designer': {
            'category': 'Design',
            'skills': [
                ('Figma', 'Advanced', 1.0, True),
                ('Wireframing', 'Advanced', 1.0, True),
                ('User Research', 'Intermediate', 0.9, True),
                ('Adobe XD', 'Intermediate', 0.7, False)
            ]
        }
    }
    
    for role_name, config in roles_config.items():
        # Create role
        role = JobRole(
            role_name=role_name,
            role_category=config['category']
        )
        session.add(role)
        session.flush()  # Get role_id
        
        # Add skill requirements
        for skill_name, req_prof, weight, is_core in config['skills']:
            skill = session.query(SkillsMaster).filter_by(skill_name=skill_name).first()
            if skill:
                req = JobRoleSkills(
                    role_id=role.role_id,
                    skill_id=skill.skill_id,
                    required_proficiency=req_prof,
                    importance_weight=weight,
                    is_core_skill=is_core
                )
                session.add(req)
    
    session.commit()
    print("✓ Job roles populated!")

def populate_students_and_skills(session, num_students=500, clear_existing=False):
    """Populate students and their skills (idempotent).
    
    Args:
        session: Database session
        num_students: Number of students to generate
        clear_existing: If True, clear existing students before generating new ones
    """
    if clear_existing:
        print("Clearing existing students and their data...")
        # Delete in correct order due to foreign keys
        session.query(StudentSkills).delete()
        session.query(MarketReadinessScores).delete()
        session.query(Student).delete()
        session.commit()
        print("  Existing data cleared.")
    
    existing_count = session.query(Student).count()
    if existing_count >= num_students and not clear_existing:
        print(f"  Students already exist ({existing_count} students). Skipping...")
        print("  Use clear_existing=True to regenerate data.")
        return
    
    print(f"Generating {num_students} students with realistic distributions...")
    
    taxonomy = load_skill_taxonomy()
    all_skills = flatten_skills(taxonomy)
    
    # Generate students with realistic program distribution
    students_data = generate_students(num_students)
    
    for student_data in students_data:
        # Create student
        student = Student(**student_data)
        session.add(student)
        session.flush()  # Get student_id
        
        # Generate skills for student
        skills_data = generate_student_skills(student_data, all_skills)
        
        for skill_data in skills_data:
            skill = session.query(SkillsMaster).filter_by(
                skill_name=skill_data['skill_name']
            ).first()
            
            if skill:
                student_skill = StudentSkills(
                    student_id=student.student_id,
                    skill_id=skill.skill_id,
                    proficiency_level=skill_data['proficiency_level'],
                    proficiency_score=skill_data['proficiency_score'],
                    acquisition_date=skill_data['acquisition_date'],
                    source=skill_data['source']
                )
                session.add(student_skill)
    
    session.commit()
    print(f"✓ {num_students} students and their skills populated!")
    # Show program distribution
    dist = session.query(Student.program, func.count(Student.student_id)).group_by(Student.program).all()
    print(f"  Program distribution: {dict(dist)}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Populate database with student data')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before populating')
    parser.add_argument('--source', choices=['synthetic', 'csv'], default='synthetic',
                        help='Data source: synthetic (default) or csv')
    parser.add_argument('--csv-path', type=str, help='Path to students CSV file (required if --source=csv)')
    parser.add_argument('--skills-csv', type=str, help='Path to skills CSV file (optional)')
    parser.add_argument('--num-students', type=int, default=500, help='Number of students for synthetic generation (default: 500)')
    
    args = parser.parse_args()
    
    session = get_db_session()
    
    try:
        taxonomy = load_skill_taxonomy()
        
        # Always populate skills master and job roles (idempotent)
        populate_skills_master(session, taxonomy)
        populate_job_roles(session)
        
        # Populate students based on source
        if args.source == 'csv':
            if not args.csv_path:
                print("ERROR: --csv-path is required when --source=csv")
                return
            
            print(f"\n[CSV Ingestion] Loading data from: {args.csv_path}")
            from src.etl.data_ingestion import ingest_from_csv
            
            result = ingest_from_csv(args.csv_path, args.skills_csv)
            
            if result['success']:
                print(f"✓ Successfully loaded {result['students_loaded']} students")
                if result['skills_loaded']:
                    print(f"✓ Successfully loaded {result['skills_loaded']} skill records")
            else:
                print("ERROR: CSV ingestion failed")
                for error in result['errors']:
                    print(f"  - {error}")
                return
        else:
            # Synthetic generation
            if args.clear:
                populate_students_and_skills(session, num_students=args.num_students, clear_existing=True)
            else:
                populate_students_and_skills(session, num_students=args.num_students, clear_existing=False)
        
        print("\n=== DATABASE POPULATED SUCCESSFULLY ===")
        print(f"Students: {session.query(Student).count()}")
        print(f"Skills: {session.query(SkillsMaster).count()}")
        print(f"Student Skills: {session.query(StudentSkills).count()}")
        print(f"Job Roles: {session.query(JobRole).count()}")
        
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
