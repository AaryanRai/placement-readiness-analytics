import json
import random
from datetime import datetime, timedelta

PROFICIENCY_MAP = {
    'Beginner': 0.25,
    'Intermediate': 0.50,
    'Advanced': 0.75,
    'Expert': 1.00
}

def load_skill_taxonomy():
    """Load skills from JSON."""
    with open('data/skill_taxonomy.json', 'r') as f:
        return json.load(f)

def generate_student_skills(student, all_skills_flat):
    """
    Generate skill acquisition records for a student.
    
    Skills by year:
    - Year 1: 3-8 skills
    - Year 2: 8-15 skills
    - Year 3: 15-25 skills
    - Year 4: 20-35 skills
    
    Returns list of dicts with:
    skill_name, proficiency_level, proficiency_score, acquisition_date, source
    """
    year = student['year_of_study']
    skill_ranges = {1: (3, 8), 2: (8, 15), 3: (15, 25), 4: (20, 35)}
    
    num_skills = random.randint(*skill_ranges[year])
    
    # Select random skills (weighted towards target role)
    selected_skills = random.sample(all_skills_flat, min(num_skills, len(all_skills_flat)))
    
    student_skills = []
    enrollment_date = datetime(student['enrollment_year'], 8, 1)
    
    for skill_name in selected_skills:
        # Random acquisition date within enrollment period
        days_enrolled = (datetime.now() - enrollment_date).days
        acquisition_days = random.randint(0, max(days_enrolled, 1))
        acquisition_date = enrollment_date + timedelta(days=acquisition_days)
        
        # Determine proficiency based on time since acquisition
        months_since = (datetime.now() - acquisition_date).days / 30
        if months_since < 3:
            proficiency = 'Beginner'
        elif months_since < 8:
            proficiency = 'Intermediate'
        elif months_since < 18:
            proficiency = 'Advanced'
        else:
            proficiency = 'Expert'
        
        source = random.choices(
            ['Course', 'Certification', 'Project', 'Workshop'],
            weights=[0.60, 0.25, 0.10, 0.05]
        )[0]
        
        student_skills.append({
            'skill_name': skill_name,
            'proficiency_level': proficiency,
            'proficiency_score': PROFICIENCY_MAP[proficiency],
            'acquisition_date': acquisition_date.date(),
            'source': source
        })
    
    return student_skills

def flatten_skills(taxonomy):
    """Flatten nested skill dict to list."""
    skills = []
    for category, subcats in taxonomy.items():
        if isinstance(subcats, dict):
            for subcat, skill_list in subcats.items():
                skills.extend(skill_list)
        else:  # Soft Skills is just a list
            skills.extend(subcats)
    return skills
