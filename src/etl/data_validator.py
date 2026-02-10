"""
Data validation utilities for ETL pipeline
"""
from typing import Dict, List, Tuple
import pandas as pd

# Valid program values
VALID_PROGRAMS = ['BBA', 'Btech', 'B.Com']

# Valid proficiency levels
VALID_PROFICIENCY_LEVELS = ['Beginner', 'Intermediate', 'Advanced', 'Expert']

# Valid skill sources
VALID_SOURCES = ['Course', 'Certification', 'Project', 'Workshop']

def validate_student_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate student data DataFrame.
    
    Args:
        df: DataFrame with student data
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    required_columns = ['name', 'email', 'program', 'year_of_study', 'enrollment_year', 'target_role']
    
    # Check required columns
    missing_cols = set(required_columns) - set(df.columns.str.lower())
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
    
    if errors:
        return False, errors
    
    # Validate data types and values
    if 'program' in df.columns:
        invalid_programs = df[~df['program'].isin(VALID_PROGRAMS)]
        if not invalid_programs.empty:
            errors.append(f"Invalid program values: {invalid_programs['program'].unique().tolist()}")
    
    if 'year_of_study' in df.columns:
        invalid_years = df[(df['year_of_study'] < 1) | (df['year_of_study'] > 4)]
        if not invalid_years.empty:
            errors.append(f"Invalid year_of_study values (must be 1-4): {invalid_years['year_of_study'].unique().tolist()}")
    
    if 'enrollment_year' in df.columns:
        invalid_enrollment = df[(df['enrollment_year'] < 2020) | (df['enrollment_year'] > 2030)]
        if not invalid_enrollment.empty:
            errors.append(f"Invalid enrollment_year values (must be 2020-2030): {invalid_enrollment['enrollment_year'].unique().tolist()}")
    
    # Check for null values in required fields
    for col in required_columns:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                errors.append(f"Column '{col}' has {null_count} null values")
    
    return len(errors) == 0, errors

def validate_skills_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate student skills data DataFrame.
    
    Args:
        df: DataFrame with student skills data
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    required_columns = ['student_id', 'skill_name', 'proficiency_level', 'acquisition_date', 'source']
    
    # Check required columns
    missing_cols = set(required_columns) - set(df.columns.str.lower())
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")
    
    if errors:
        return False, errors
    
    # Validate proficiency levels
    if 'proficiency_level' in df.columns:
        invalid_proficiency = df[~df['proficiency_level'].isin(VALID_PROFICIENCY_LEVELS)]
        if not invalid_proficiency.empty:
            errors.append(f"Invalid proficiency_level values: {invalid_proficiency['proficiency_level'].unique().tolist()}")
    
    # Validate sources
    if 'source' in df.columns:
        invalid_sources = df[~df['source'].isin(VALID_SOURCES)]
        if not invalid_sources.empty:
            errors.append(f"Invalid source values: {invalid_sources['source'].unique().tolist()}")
    
    # Check for null values
    for col in required_columns:
        if col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                errors.append(f"Column '{col}' has {null_count} null values")
    
    return len(errors) == 0, errors

def clean_student_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize student data.
    
    Args:
        df: Raw student DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    df_clean = df.copy()
    
    # Normalize column names to lowercase
    df_clean.columns = df_clean.columns.str.lower()
    
    # Strip whitespace from string columns
    string_cols = df_clean.select_dtypes(include=['object']).columns
    for col in string_cols:
        df_clean[col] = df_clean[col].astype(str).str.strip()
    
    # Ensure proper data types
    if 'year_of_study' in df_clean.columns:
        df_clean['year_of_study'] = pd.to_numeric(df_clean['year_of_study'], errors='coerce').astype('Int64')
    
    if 'enrollment_year' in df_clean.columns:
        df_clean['enrollment_year'] = pd.to_numeric(df_clean['enrollment_year'], errors='coerce').astype('Int64')
    
    return df_clean

def clean_skills_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and normalize skills data.
    
    Args:
        df: Raw skills DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    df_clean = df.copy()
    
    # Normalize column names to lowercase
    df_clean.columns = df_clean.columns.str.lower()
    
    # Strip whitespace from string columns
    string_cols = df_clean.select_dtypes(include=['object']).columns
    for col in string_cols:
        df_clean[col] = df_clean[col].astype(str).str.strip()
    
    # Ensure proper data types
    if 'student_id' in df_clean.columns:
        df_clean['student_id'] = pd.to_numeric(df_clean['student_id'], errors='coerce').astype('Int64')
    
    # Convert acquisition_date to datetime
    if 'acquisition_date' in df_clean.columns:
        df_clean['acquisition_date'] = pd.to_datetime(df_clean['acquisition_date'], errors='coerce')
    
    return df_clean

