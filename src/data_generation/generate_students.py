"""
Generate synthetic student data using Faker
Dynamic and realistic data generation
"""
from faker import Faker
from typing import List, Dict
import random
import numpy as np
from datetime import datetime

# Use current time as seed component for variability
random.seed(None)  # Use system time
np.random.seed(None)

fake = Faker('en_IN')  # Indian names and data

PROGRAMS = ['BBA', 'Btech', 'B.Com']
# Realistic program distribution (Btech is most popular, then BBA, then B.Com)
PROGRAM_WEIGHTS = [0.45, 0.35, 0.20]  # Btech, BBA, B.Com

TARGET_ROLES_BY_PROGRAM = {
    'Btech': ['Data Analyst', 'Full-Stack Developer', 'Frontend Developer', 'Backend Developer'],
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
        # Generate students with realistic weighted program distribution
        for _ in range(count):
            program = np.random.choice(PROGRAMS, p=PROGRAM_WEIGHTS)
            students.append(_generate_single_student(program))
    
    # Shuffle to avoid ordering bias
    random.shuffle(students)
    return students


def _generate_single_student(program: str) -> Dict:
    """Generate a single student record with realistic distributions"""
    current_year = datetime.now().year
    
    # Realistic enrollment year distribution (more recent enrollments)
    # Weighted towards recent years
    enrollment_years = list(range(2020, current_year + 1))
    weights = [0.1, 0.15, 0.25, 0.35, 0.15]  # Older to newer
    weights = weights[:len(enrollment_years)]
    weights = [w / sum(weights) for w in weights]  # Normalize
    enrollment_year = int(np.random.choice(enrollment_years, p=weights))
    
    # Calculate year of study realistically
    year_of_study = min(current_year - enrollment_year + 1, 4)
    year_of_study = max(year_of_study, 1)  # Ensure at least year 1
    
    # Realistic target role selection (70% have target role, 30% don't)
    target_roles = TARGET_ROLES_BY_PROGRAM.get(program, [])
    if target_roles and random.random() < 0.70:
        # Weighted selection - first role is most popular
        role_weights = [0.4, 0.3, 0.2, 0.1][:len(target_roles)]
        role_weights = [w / sum(role_weights) for w in role_weights]
        target_role = np.random.choice(target_roles, p=role_weights)
    else:
        target_role = None
    
    return {
        'name': fake.name(),
        'email': fake.unique.email(),
        'program': program,
        'year_of_study': year_of_study,
        'enrollment_year': enrollment_year,
        'target_role': target_role
    }

