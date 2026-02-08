"""
Generate synthetic student data using Faker
"""
from faker import Faker
from typing import List, Dict
import random

fake = Faker('en_IN')  # Indian names and data

PROGRAMS = ['BBA', 'BCA', 'B.Com']
TARGET_ROLES_BY_PROGRAM = {
    'BCA': ['Data Analyst', 'Full-Stack Developer', 'Frontend Developer', 'Backend Developer'],
    'BBA': ['Business Analyst', 'Product Manager', 'Digital Marketer', 'HR Analyst'],
    'B.Com': ['Financial Analyst', 'Business Analyst', 'Data Analyst']
}

def generate_students(count: int, program_distribution: Dict[str, int] = None) -> List[Dict]:
    """
    Generate synthetic student records.
    
    Args:
        count: Total number of students to generate
        program_distribution: Dict with program names as keys and counts as values
    
    Returns:
        List of student dictionaries
    """
    students = []
    
    if program_distribution:
        # Generate students according to distribution
        for program, program_count in program_distribution.items():
            for _ in range(program_count):
                students.append(_generate_single_student(program))
    else:
        # Generate students with random program distribution
        for _ in range(count):
            program = random.choice(PROGRAMS)
            students.append(_generate_single_student(program))
    
    return students


def _generate_single_student(program: str) -> Dict:
    """Generate a single student record"""
    enrollment_year = random.randint(2020, 2023)
    current_year = 2024
    year_of_study = min(current_year - enrollment_year + 1, 4)
    year_of_study = max(year_of_study, 1)  # Ensure at least year 1
    
    target_roles = TARGET_ROLES_BY_PROGRAM.get(program, [])
    target_role = random.choice(target_roles) if target_roles else None
    
    return {
        'name': fake.name(),
        'email': fake.unique.email(),
        'program': program,
        'year_of_study': year_of_study,
        'enrollment_year': enrollment_year,
        'target_role': target_role
    }

