"""
Main script to populate database with synthetic data
"""
from src.database.connection import get_db_session
from src.database.models import (
    Student, SkillsMaster, StudentSkills, JobRole, JobRoleSkills, MarketReadinessScores
)
from src.data_generation.generate_students import generate_students_batch
from src.data_generation.generate_skills import (
    generate_skills_master, generate_job_roles, generate_student_skills
)
from datetime import datetime


def populate_database(total_students: int = 500):
    """
    Populate the database with synthetic data.
    
    Args:
        total_students: Number of students to generate (default: 500 for MVP)
    """
    session = get_db_session()
    
    try:
        print(f"Starting database population with {total_students} students...")
        
        # 1. Generate and insert skills_master
        print("\n1. Generating skills master...")
        skills = generate_skills_master()
        for skill_data in skills:
            skill = SkillsMaster(**skill_data)
            session.add(skill)
        session.commit()
        print(f"✓ Inserted {len(skills)} skills")
        
        # 2. Generate and insert job roles
        print("\n2. Generating job roles...")
        roles = generate_job_roles()
        for role_data in roles:
            role = JobRole(**role_data)
            session.add(role)
        session.commit()
        print(f"✓ Inserted {len(roles)} job roles")
        
        # 3. Generate and insert students
        print("\n3. Generating students...")
        students_data = generate_students_batch(total_students)
        skill_ids = [s.skill_id for s in session.query(SkillsMaster).all()]
        
        for student_data in students_data:
            student = Student(**student_data)
            session.add(student)
            session.flush()  # Get student_id
            
            # Generate student skills
            student_skills_data = generate_student_skills(
                student.student_id,
                student.year_of_study,
                skill_ids
            )
            
            for skill_data in student_skills_data:
                student_skill = StudentSkills(**skill_data)
                session.add(student_skill)
        
        session.commit()
        print(f"✓ Inserted {len(students_data)} students with their skills")
        
        # 4. Generate job role skills (placeholder - will be implemented in Phase 2)
        print("\n4. Job role skills will be populated in Phase 2...")
        
        print("\n✓ Database population completed successfully!")
        
    except Exception as e:
        session.rollback()
        print(f"\n✗ Error during population: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import sys
    
    total = 500  # MVP default
    if len(sys.argv) > 1:
        total = int(sys.argv[1])
    
    populate_database(total)

