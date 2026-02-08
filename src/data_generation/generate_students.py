"""
Generate synthetic student data using Faker
"""
from faker import Faker
from datetime import datetime
import random
from typing import List, Dict

fake = Faker('en_IN')  # Indian names and data

PROGRAMS = ['BBA', 'BCA', 'B.Com']
TARGET_ROLES_BY_PROGRAM = {
    'BCA': ['Data Analyst', 'Full-Stack Developer', 'Frontend Developer', 'Backend Developer'],
    'BBA': ['Business Analyst', 'Product Manager', 'Digital Marketer', 'HR Analyst'],
    'B.Com': ['Financial Analyst', 'Business Analyst', 'Data Analyst']
}


def generate_student(student_id: int, program: str, year_of_study: int, enrollment_year: int) -> Dict:
    """
    Generate a single student record.
    
    Args:
        student_id: Unique student ID
        program: Program name (BBA, BCA, B.Com)
        year_of_study: Year of study (1-4)
        enrollment_year: Year of enrollment
        
    Returns:
        Dictionary with student data
    """
    # Select target role based on program
    possible_roles = TARGET_ROLES_BY_PROGRAM.get(program, ['Business Analyst'])
    target_role = random.choice(possible_roles)
    
    return {
        'student_id': student_id,
        'name': fake.name(),
        'email': fake.unique.email(),
        'program': program,
        'year_of_study': year_of_study,
        'enrollment_year': enrollment_year,
        'target_role': target_role
    }


def generate_students_batch(total: int = 500) -> List[Dict]:
    """
    Generate a batch of students with realistic distribution.
    
    Distribution:
    - Programs: BBA (40%), BCA (35%), B.Com (25%)
    - Years: Year 1 (30%), Year 2 (25%), Year 3 (25%), Year 4 (20%)
    
    Args:
        total: Total number of students to generate
        
    Returns:
        List of student dictionaries
    """
    students = []
    current_year = datetime.now().year
    
    # Program distribution
    program_dist = {
        'BBA': int(total * 0.40),
        'BCA': int(total * 0.35),
        'B.Com': total - int(total * 0.40) - int(total * 0.35)
    }
    
    # Year distribution
    year_dist = {
        1: int(total * 0.30),
        2: int(total * 0.25),
        3: int(total * 0.25),
        4: total - int(total * 0.30) - int(total * 0.25) - int(total * 0.25)
    }
    
    student_id = 1
    
    # Generate students by program
    for program, count in program_dist.items():
        for _ in range(count):
            year = random.choices(
                list(year_dist.keys()),
                weights=[year_dist[1], year_dist[2], year_dist[3], year_dist[4]]
            )[0]
            
            # Calculate enrollment year based on current year and year of study
            enrollment_year = current_year - (year - 1)
            
            student = generate_student(student_id, program, year, enrollment_year)
            students.append(student)
            student_id += 1
    
    return students

