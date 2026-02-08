"""
Generate skills master data and student-skill mappings
"""
from typing import List, Dict
import random
from datetime import datetime, timedelta

# Skill taxonomy (50 skills for MVP)
SKILLS_TAXONOMY = {
    'Technical': {
        'Programming': ['Python', 'JavaScript', 'Java', 'C++', 'SQL', 'R'],
        'Data': ['Pandas', 'NumPy', 'Excel', 'Tableau', 'Power BI', 'Statistics'],
        'Web': ['React', 'Node.js', 'HTML/CSS', 'Django', 'Flask'],
        'Database': ['PostgreSQL', 'MySQL', 'MongoDB'],
        'Cloud': ['AWS', 'Azure', 'Docker']
    },
    'Business': {
        'Analysis': ['Business Intelligence', 'Financial Modeling'],
        'Marketing': ['SEO', 'Google Ads', 'Social Media Marketing'],
        'Management': ['Project Management', 'Agile']
    },
    'Design': {
        'UI/UX': ['Figma', 'Wireframing', 'User Research'],
        'Graphics': ['Photoshop', 'Canva']
    },
    'Soft Skills': {
        'General': ['Communication', 'Teamwork', 'Leadership', 'Problem Solving']
    }
}

PROFICIENCY_LEVELS = ['Beginner', 'Intermediate', 'Advanced', 'Expert']
PROFICIENCY_SCORES = {
    'Beginner': 0.25,
    'Intermediate': 0.50,
    'Advanced': 0.75,
    'Expert': 1.00
}

SOURCES = ['Course', 'Certification', 'Project', 'Workshop']


def get_all_skills() -> List[Dict]:
    """
    Get all skills from taxonomy as a flat list.
    
    Returns:
        List of skill dictionaries with category and subcategory
    """
    skills = []
    skill_id = 1
    
    for category, subcategories in SKILLS_TAXONOMY.items():
        for subcategory, skill_names in subcategories.items():
            for skill_name in skill_names:
                skills.append({
                    'skill_id': skill_id,
                    'skill_name': skill_name,
                    'category': category,
                    'subcategory': subcategory
                })
                skill_id += 1
    
    return skills


def generate_student_skills(student_id: int, year_of_study: int, all_skills: List[Dict]) -> List[Dict]:
    """
    Generate skill assignments for a student based on their year of study.
    
    Args:
        student_id: Student ID
        year_of_study: Current year (1-4)
        all_skills: List of all available skills
    
    Returns:
        List of student-skill mappings
    """
    # Skill count ranges by year (from PRD)
    skill_ranges = {
        1: (3, 8),
        2: (8, 15),
        3: (15, 25),
        4: (20, 35)
    }
    
    min_skills, max_skills = skill_ranges.get(year_of_study, (5, 15))
    num_skills = random.randint(min_skills, max_skills)
    
    # Select random skills
    selected_skills = random.sample(all_skills, min(num_skills, len(all_skills)))
    
    student_skills = []
    base_date = datetime(2020, 1, 1)
    
    for skill in selected_skills:
        # Proficiency increases with year of study
        proficiency_weights = {
            1: [0.6, 0.3, 0.1, 0.0],  # Mostly Beginner
            2: [0.3, 0.5, 0.2, 0.0],  # Mostly Intermediate
            3: [0.1, 0.4, 0.4, 0.1],  # Mix of Intermediate/Advanced
            4: [0.0, 0.2, 0.5, 0.3]   # Mostly Advanced/Expert
        }
        
        weights = proficiency_weights.get(year_of_study, [0.25, 0.25, 0.25, 0.25])
        proficiency_level = random.choices(PROFICIENCY_LEVELS, weights=weights)[0]
        
        # Acquisition date: earlier for lower proficiency, later for higher
        months_ago = random.randint(1, (year_of_study * 12))
        acquisition_date = base_date + timedelta(days=30 * months_ago)
        
        student_skills.append({
            'student_id': student_id,
            'skill_id': skill['skill_id'],
            'proficiency_level': proficiency_level,
            'proficiency_score': PROFICIENCY_SCORES[proficiency_level],
            'acquisition_date': acquisition_date.date(),
            'source': random.choice(SOURCES)
        })
    
    return student_skills

