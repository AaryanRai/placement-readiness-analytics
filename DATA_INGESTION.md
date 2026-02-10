# Data Ingestion Guide

This document describes how to ingest data into the University Placement Readiness Analytics System from various sources.

## Supported Data Sources

1. **Synthetic Data Generation** (Default) - Automatically generates realistic student data
2. **CSV Files** - Import student and skill data from CSV files
3. **API Integration** (Future) - Real-time data ingestion from external systems

## CSV Data Ingestion

### Prerequisites

- Database must be initialized (`python src/database/init_db.py`)
- Skills master and job roles must be populated (done automatically)

### CSV Format Requirements

#### Students CSV

**Required Columns:**
- `name` - Student full name (string)
- `email` - Student email address (string, must be unique)
- `program` - Academic program (string: "BBA", "Btech", or "B.Com")
- `year_of_study` - Current academic year (integer: 1-4)
- `enrollment_year` - Year of enrollment (integer: 2020-2030)
- `target_role` - Target career role (string: must match existing job roles)

**Example CSV:**
```csv
name,email,program,year_of_study,enrollment_year,target_role
John Doe,john.doe@example.com,Btech,3,2022,Full-Stack Developer
Jane Smith,jane.smith@example.com,BBA,2,2023,Digital Marketer
```

#### Skills CSV

**Required Columns:**
- `student_id` - Student ID (integer) OR `email` - Student email (string)
- `skill_name` - Name of the skill (string: must match skills_master)
- `proficiency_level` - Skill proficiency (string: "Beginner", "Intermediate", "Advanced", or "Expert")
- `acquisition_date` - Date skill was acquired (date: YYYY-MM-DD format)
- `source` - How skill was acquired (string: "Course", "Certification", "Project", or "Workshop")

**Example CSV:**
```csv
student_id,skill_name,proficiency_level,acquisition_date,source
1,Python,Advanced,2023-01-15,Course
1,SQL,Intermediate,2023-03-20,Certification
2,SEO,Advanced,2023-02-10,Project
```

### Usage

#### Basic CSV Ingestion

```bash
# Ingest students from CSV
python src/data_generation/populate_db.py --source csv --csv-path data/students.csv

# Ingest students and skills from CSV
python src/data_generation/populate_db.py --source csv --csv-path data/students.csv --skills-csv data/skills.csv
```

#### Synthetic Data Generation (Default)

```bash
# Generate 500 students (default)
python src/data_generation/populate_db.py

# Generate 1000 students
python src/data_generation/populate_db.py --num-students 1000

# Clear existing data and regenerate
python src/data_generation/populate_db.py --clear
```

### Data Validation

The ETL pipeline automatically validates all data before insertion:

- **Required Fields**: All required columns must be present
- **Data Types**: Values must match expected types
- **Value Ranges**: 
  - `year_of_study`: 1-4
  - `enrollment_year`: 2020-2030
  - `program`: Must be one of "BBA", "Btech", "B.Com"
  - `proficiency_level`: Must be one of "Beginner", "Intermediate", "Advanced", "Expert"
  - `source`: Must be one of "Course", "Certification", "Project", "Workshop"
- **Uniqueness**: Email addresses must be unique
- **Referential Integrity**: Skills must exist in skills_master, roles must exist in job_roles

### Error Handling

If validation fails, the ingestion process will:
1. Report all validation errors
2. Not insert any data (transaction rollback)
3. Provide detailed error messages for correction

**Example Error Output:**
```
ERROR: CSV ingestion failed
  - Validation errors:
    - Invalid program values: ['BCA']
    - Column 'year_of_study' has 5 null values
```

### Programmatic Usage

You can also use the ETL module programmatically:

```python
from src.etl.data_ingestion import ingest_from_csv

# Ingest from CSV
result = ingest_from_csv('data/students.csv', 'data/skills.csv')

if result['success']:
    print(f"Loaded {result['students_loaded']} students")
    print(f"Loaded {result['skills_loaded']} skill records")
else:
    print("Errors:")
    for error in result['errors']:
        print(f"  - {error}")
```

## Data Source Comparison

| Feature | Synthetic | CSV |
|---------|-----------|-----|
| Setup Time | Instant | Requires CSV preparation |
| Data Quality | High (realistic distributions) | Depends on source |
| Customization | Limited | Full control |
| Volume | Configurable (default: 500) | Unlimited |
| Use Case | Testing, demos | Production data |

## Best Practices

1. **Always validate CSV files** before ingestion using the validation functions
2. **Use unique email addresses** for each student
3. **Ensure skill names match** the skills_master table exactly
4. **Check date formats** - use YYYY-MM-DD for acquisition_date
5. **Backup database** before large data imports
6. **Test with small datasets** first before full import

## Troubleshooting

### "CSV file not found"
- Check file path is correct
- Use absolute paths if relative paths don't work

### "Invalid program values"
- Ensure program values are exactly: "BBA", "Btech", or "B.Com"
- Check for typos or extra spaces

### "Skill not found"
- Verify skill names match exactly with skills_master
- Check for case sensitivity issues
- Run `python src/data_generation/populate_db.py` first to populate skills_master

### "Duplicate email"
- Each student must have a unique email
- Remove duplicates from CSV or use --clear flag

## Future Enhancements

- **API Integration**: Real-time data ingestion from student information systems
- **Bulk Import**: Support for Excel files and other formats
- **Data Transformation**: Automatic data cleaning and normalization
- **Incremental Updates**: Update existing records instead of only inserting new ones

