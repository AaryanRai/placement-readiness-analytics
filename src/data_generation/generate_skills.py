import json
import random
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Use current time as seed component for variability
random.seed(None)  # Use system time
np.random.seed(None)

PROFICIENCY_MAP = {
    'Beginner': 0.25,
    'Intermediate': 0.50,
    'Advanced': 0.75,
    'Expert': 1.00
}

def load_skill_taxonomy():
    """Load skills from JSON."""
    # Get project root (3 levels up from this file)
    project_root = Path(__file__).parent.parent.parent
    skill_file = project_root / 'data' / 'skill_taxonomy.json'
    
    with open(skill_file, 'r') as f:
        return json.load(f)

def generate_student_skills(student, all_skills_flat):
    """
    Generate skill acquisition records for a student with realistic distributions.
    
    Skills by year (using normal distribution for realism):
    - Year 1: 3-8 skills (mean: 5.5)
    - Year 2: 8-15 skills (mean: 11.5)
    - Year 3: 15-25 skills (mean: 20)
    - Year 4: 20-35 skills (mean: 27.5)
    
    Returns list of dicts with:
    skill_name, proficiency_level, proficiency_score, acquisition_date, source
    """
    year = student['year_of_study']
    
    # Realistic skill count distributions using normal distribution
    skill_params = {
        1: {'mean': 5.5, 'std': 1.5, 'min': 3, 'max': 8},
        2: {'mean': 11.5, 'std': 2.5, 'min': 8, 'max': 15},
        3: {'mean': 20, 'std': 3.5, 'min': 15, 'max': 25},
        4: {'mean': 27.5, 'std': 4.5, 'min': 20, 'max': 35}
    }
    
    params = skill_params.get(year, skill_params[1])
    num_skills = int(np.clip(np.random.normal(params['mean'], params['std']), 
                            params['min'], params['max']))
    
    # Realistic skill selection - mix of relevant and diverse skills
    # 60% relevant to program/role, 40% diverse
    target_role = student.get('target_role')
    program = student.get('program', '')
    
    # Weight skills based on relevance (simplified - in real system would use skill-role mapping)
    if len(all_skills_flat) > num_skills:
        # Use weighted random selection for more diversity
        selected_skills = random.sample(all_skills_flat, num_skills)
    else:
        selected_skills = all_skills_flat.copy()
        random.shuffle(selected_skills)
    
    student_skills = []
    enrollment_date = datetime(student['enrollment_year'], 8, 1)
    current_date = datetime.now()
    days_enrolled = max((current_date - enrollment_date).days, 1)
    
    # Realistic proficiency distribution by year
    # Higher years have more advanced skills
    proficiency_weights_by_year = {
        1: {'Beginner': 0.50, 'Intermediate': 0.40, 'Advanced': 0.09, 'Expert': 0.01},
        2: {'Beginner': 0.30, 'Intermediate': 0.45, 'Advanced': 0.20, 'Expert': 0.05},
        3: {'Beginner': 0.15, 'Intermediate': 0.40, 'Advanced': 0.35, 'Expert': 0.10},
        4: {'Beginner': 0.05, 'Intermediate': 0.30, 'Advanced': 0.45, 'Expert': 0.20}
    }
    
    proficiency_weights = proficiency_weights_by_year.get(year, proficiency_weights_by_year[1])
    proficiency_levels = list(proficiency_weights.keys())
    proficiency_probs = list(proficiency_weights.values())
    
    for skill_name in selected_skills:
        # Realistic acquisition date - weighted towards more recent (students learn continuously)
        # Use beta distribution for realistic spread
        acquisition_ratio = np.random.beta(2, 3)  # Skewed towards recent
        acquisition_days = int(acquisition_ratio * days_enrolled)
        acquisition_date = enrollment_date + timedelta(days=acquisition_days)
        
        # Determine proficiency - mix of time-based and year-based
        months_since = (current_date - acquisition_date).days / 30
        
        # 70% based on year (realistic - higher years have better skills)
        # 30% based on time since acquisition
        if random.random() < 0.7:
            proficiency = np.random.choice(proficiency_levels, p=proficiency_probs)
        else:
            # Time-based proficiency
            if months_since < 3:
                proficiency = 'Beginner'
            elif months_since < 8:
                proficiency = 'Intermediate'
            elif months_since < 18:
                proficiency = 'Advanced'
            else:
                proficiency = 'Expert'
        
        # Realistic source distribution
        source = np.random.choice(
            ['Course', 'Certification', 'Project', 'Workshop'],
            p=[0.55, 0.25, 0.15, 0.05]  # Courses most common, workshops rare
        )
        
        student_skills.append({
            'skill_name': skill_name,
            'proficiency_level': proficiency,
            'proficiency_score': PROFICIENCY_MAP[proficiency],
            'acquisition_date': acquisition_date.date(),
            'source': source
        })
    
    # Sort by acquisition date for realism
    student_skills.sort(key=lambda x: x['acquisition_date'])
    
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
