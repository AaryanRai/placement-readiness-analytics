"""
Main script to populate database with synthetic data
"""
from src.database.connection import get_db_session
from src.database.models import (
    Student, SkillsMaster, StudentSkills, JobRole, JobRoleSkills, MarketReadinessScores
)
from src.data_generation.generate_students import generate_students
from src.data_generation.generate_skills import get_all_skills, generate_student_skills

# MVP Configuration (500 students)
STUDENT_CONFIG = {
    'total': 500,
    'programs': {
        'BBA': 200,   # 40%
        'BCA': 175,   # 35%
        'B.Com': 125  # 25%
    }
}

# Job roles for MVP (5 roles)
JOB_ROLES = [
    {'role_name': 'Data Analyst', 'role_category': 'Technical', 'description': 'Analyzes data to help businesses make decisions'},
    {'role_name': 'Full-Stack Developer', 'role_category': 'Technical', 'description': 'Develops both frontend and backend applications'},
    {'role_name': 'Digital Marketer', 'role_category': 'Business', 'description': 'Manages online marketing campaigns'},
    {'role_name': 'Business Analyst', 'role_category': 'Business', 'description': 'Analyzes business processes and requirements'},
    {'role_name': 'UX/UI Designer', 'role_category': 'Design', 'description': 'Designs user interfaces and experiences'}
]


def populate_database():
    """Populate database with synthetic data"""
    session = get_db_session()
    
    try:
        print("=" * 60)
        print("POPULATING DATABASE WITH SYNTHETIC DATA")
        print("=" * 60)
        
        # Step 1: Populate Skills Master
        print("\n[1/5] Populating skills_master...")
        all_skills = get_all_skills()
        for skill_data in all_skills:
            skill = SkillsMaster(**skill_data)
            session.add(skill)
        session.commit()
        print(f"✓ Added {len(all_skills)} skills to skills_master")
        
        # Step 2: Populate Job Roles
        print("\n[2/5] Populating job_roles...")
        role_map = {}  # Store role_id for later use
        for role_data in JOB_ROLES:
            role = JobRole(**role_data)
            session.add(role)
            session.flush()  # Get the role_id
            role_map[role_data['role_name']] = role.role_id
        session.commit()
        print(f"✓ Added {len(JOB_ROLES)} job roles")
        
        # Step 3: Populate Students
        print("\n[3/5] Populating students...")
        students_data = generate_students(
            count=STUDENT_CONFIG['total'],
            program_distribution=STUDENT_CONFIG['programs']
        )
        student_map = {}
        for student_data in students_data:
            student = Student(**student_data)
            session.add(student)
            session.flush()
            student_map[student.student_id] = student
        session.commit()
        print(f"✓ Added {len(students_data)} students")
        
        # Step 4: Populate Student Skills
        print("\n[4/5] Populating student_skills...")
        total_skill_records = 0
        for student_id, student in student_map.items():
            skills = generate_student_skills(student_id, student.year_of_study, all_skills)
            for skill_data in skills:
                student_skill = StudentSkills(**skill_data)
                session.add(student_skill)
                total_skill_records += 1
        session.commit()
        print(f"✓ Added {total_skill_records} student-skill mappings")
        
        # Step 5: Populate Job Role Skills (simplified for MVP)
        print("\n[5/5] Populating job_role_skills...")
        # This will be populated with role-specific requirements
        # For MVP, we'll add basic requirements (to be expanded)
        print("⚠ Job role skills will be populated in next phase")
        
        print("\n" + "=" * 60)
        print("✓ DATABASE POPULATION COMPLETE!")
        print("=" * 60)
        print(f"  Students: {len(students_data)}")
        print(f"  Skills: {len(all_skills)}")
        print(f"  Student-Skill Mappings: {total_skill_records}")
        print(f"  Job Roles: {len(JOB_ROLES)}")
        
    except Exception as e:
        session.rollback()
        print(f"\n✗ Error populating database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    populate_database()

