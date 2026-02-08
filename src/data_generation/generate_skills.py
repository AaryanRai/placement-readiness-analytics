"""
Generate skills data and job role requirements
"""
import json
import os
from typing import List, Dict
from datetime import datetime, timedelta
import random

# Load skill taxonomy
SKILL_TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), '../../data/skill_taxonomy.json')


def load_skill_taxonomy() -> Dict:
    """Load skills from taxonomy JSON file."""
    with open(SKILL_TAXONOMY_PATH, 'r') as f:
        return json.load(f)


def generate_skills_master() -> List[Dict]:
    """
    Generate skills_master records from taxonomy.
    
    Returns:
        List of skill dictionaries
    """
    taxonomy = load_skill_taxonomy()
    skills = []
    skill_id = 1
    
    for category, subcategories in taxonomy.items():
        if isinstance(subcategories, dict):
            # Has subcategories (Technical, Business, Design)
            for subcategory, skill_list in subcategories.items():
                for skill_name in skill_list:
                    skills.append({
                        'skill_id': skill_id,
                        'skill_name': skill_name,
                        'category': category,
                        'subcategory': subcategory
                    })
                    skill_id += 1
        else:
            # No subcategories (Soft Skills)
            for skill_name in subcategories:
                skills.append({
                    'skill_id': skill_id,
                    'skill_name': skill_name,
                    'category': category,
                    'subcategory': None
                })
                skill_id += 1
    
    return skills


def generate_job_roles() -> List[Dict]:
    """
    Generate job roles for MVP (5 roles).
    
    Returns:
        List of job role dictionaries
    """
    roles = [
        {
            'role_id': 1,
            'role_name': 'Data Analyst',
            'role_category': 'Technical',
            'description': 'Analyze data to help organizations make informed decisions'
        },
        {
            'role_id': 2,
            'role_name': 'Full-Stack Developer',
            'role_category': 'Technical',
            'description': 'Develop both frontend and backend applications'
        },
        {
            'role_id': 3,
            'role_name': 'Digital Marketer',
            'role_category': 'Business',
            'description': 'Promote brands through digital channels'
        },
        {
            'role_id': 4,
            'role_name': 'Business Analyst',
            'role_category': 'Business',
            'description': 'Bridge gap between business needs and technical solutions'
        },
        {
            'role_id': 5,
            'role_name': 'UX/UI Designer',
            'role_category': 'Design',
            'description': 'Design user interfaces and experiences'
        }
    ]
    return roles


def generate_job_role_skills() -> List[Dict]:
    """
    Generate job role skill requirements.
    This is a simplified version - will be expanded in Phase 2.
    
    Returns:
        List of job role skill requirement dictionaries
    """
    # This will be populated with actual requirements in Phase 2
    # For now, return empty list as placeholder
    return []


def generate_student_skills(student_id: int, year_of_study: int, skill_pool: List[int]) -> List[Dict]:
    """
    Generate student skills based on year of study.
    
    Skill acquisition patterns:
    - Year 1: 3-8 skills
    - Year 2: 8-15 skills
    - Year 3: 15-25 skills
    - Year 4: 20-35 skills
    
    Args:
        student_id: Student ID
        year_of_study: Year of study (1-4)
        skill_pool: List of available skill IDs
        
    Returns:
        List of student skill dictionaries
    """
    skills = []
    proficiency_levels = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
    proficiency_scores = {
        'Beginner': 0.25,
        'Intermediate': 0.50,
        'Advanced': 0.75,
        'Expert': 1.00
    }
    sources = ['Course', 'Certification', 'Project', 'Workshop']
    
    # Determine number of skills based on year
    skill_ranges = {
        1: (3, 8),
        2: (8, 15),
        3: (15, 25),
        4: (20, 35)
    }
    min_skills, max_skills = skill_ranges[year_of_study]
    num_skills = random.randint(min_skills, max_skills)
    
    # Select random skills
    selected_skills = random.sample(skill_pool, min(num_skills, len(skill_pool)))
    
    # Generate acquisition dates (spread over enrollment period)
    current_date = datetime.now()
    enrollment_date = datetime(current_date.year - (year_of_study - 1), 1, 1)
    
    for skill_id in selected_skills:
        # Proficiency increases with time
        proficiency = random.choices(
            proficiency_levels,
            weights=[0.4, 0.3, 0.2, 0.1] if year_of_study <= 2 else [0.2, 0.3, 0.3, 0.2]
        )[0]
        
        # Random acquisition date between enrollment and now
        days_since_enrollment = (current_date - enrollment_date).days
        acquisition_days = random.randint(0, days_since_enrollment)
        acquisition_date = enrollment_date + timedelta(days=acquisition_days)
        
        skills.append({
            'student_id': student_id,
            'skill_id': skill_id,
            'proficiency_level': proficiency,
            'proficiency_score': proficiency_scores[proficiency],
            'acquisition_date': acquisition_date.date(),
            'source': random.choice(sources)
        })
    
    return skills

