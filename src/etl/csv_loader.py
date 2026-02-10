"""
CSV data loader for ETL pipeline
"""
import sys
from pathlib import Path
import pandas as pd
from typing import Tuple, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.etl.data_validator import (
    validate_student_data, validate_skills_data,
    clean_student_data, clean_skills_data
)

def load_students_csv(csv_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load and validate student data from CSV file.
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        Tuple of (DataFrame, error_message)
        Returns (None, error_message) if loading fails
    """
    try:
        # Load CSV
        df = pd.read_csv(csv_path)
        
        # Clean data
        df_clean = clean_student_data(df)
        
        # Validate data
        is_valid, errors = validate_student_data(df_clean)
        
        if not is_valid:
            error_msg = "Validation errors:\n" + "\n".join(f"  - {e}" for e in errors)
            return None, error_msg
        
        return df_clean, None
    
    except FileNotFoundError:
        return None, f"CSV file not found: {csv_path}"
    except pd.errors.EmptyDataError:
        return None, "CSV file is empty"
    except Exception as e:
        return None, f"Error loading CSV: {str(e)}"

def load_skills_csv(csv_path: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Load and validate student skills data from CSV file.
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        Tuple of (DataFrame, error_message)
        Returns (None, error_message) if loading fails
    """
    try:
        # Load CSV
        df = pd.read_csv(csv_path)
        
        # Clean data
        df_clean = clean_skills_data(df)
        
        # Validate data
        is_valid, errors = validate_skills_data(df_clean)
        
        if not is_valid:
            error_msg = "Validation errors:\n" + "\n".join(f"  - {e}" for e in errors)
            return None, error_msg
        
        return df_clean, None
    
    except FileNotFoundError:
        return None, f"CSV file not found: {csv_path}"
    except pd.errors.EmptyDataError:
        return None, "CSV file is empty"
    except Exception as e:
        return None, f"Error loading CSV: {str(e)}"

def get_csv_format_requirements() -> dict:
    """
    Get CSV format requirements for documentation.
    
    Returns:
        Dictionary with format requirements
    """
    return {
        'students': {
            'required_columns': ['name', 'email', 'program', 'year_of_study', 'enrollment_year', 'target_role'],
            'program_values': ['BBA', 'Btech', 'B.Com'],
            'year_of_study_range': [1, 2, 3, 4],
            'enrollment_year_range': '2020-2030',
            'example': {
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'program': 'Btech',
                'year_of_study': 3,
                'enrollment_year': 2022,
                'target_role': 'Full-Stack Developer'
            }
        },
        'skills': {
            'required_columns': ['student_id', 'skill_name', 'proficiency_level', 'acquisition_date', 'source'],
            'proficiency_levels': ['Beginner', 'Intermediate', 'Advanced', 'Expert'],
            'sources': ['Course', 'Certification', 'Project', 'Workshop'],
            'acquisition_date_format': 'YYYY-MM-DD',
            'example': {
                'student_id': 1,
                'skill_name': 'Python',
                'proficiency_level': 'Advanced',
                'acquisition_date': '2023-01-15',
                'source': 'Course'
            }
        }
    }

