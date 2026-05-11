"""
Student Records Management System - ETL Pipeline

This script performs Extract, Transform, and Load operations:
1. EXTRACT: Read CSV files into pandas DataFrames
2. TRANSFORM: Validate data, ensure constraints, remove duplicates
3. LOAD: Insert data into PostgreSQL database in correct order

Designed for beginners - uses clear functions and simple logging.
"""

import pandas as pd
import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

# ============================================================================
# CONFIGURATION
# ============================================================================

# Path to CSV files (relative to this script's location)
DATA_DIR = "../data"

# Database tables in order of loading (respects foreign key dependencies)
LOAD_ORDER = ['students', 'courses', 'enrollments', 'grades', 'attendance']

# Expected columns for each table (for validation)
TABLE_COLUMNS = {
    'students': ['student_id', 'student_number', 'first_name', 'last_name', 
                 'date_of_birth', 'email', 'status'],
    'courses': ['course_id', 'course_code', 'course_name', 'credits', 'status'],
    'enrollments': ['enrollment_id', 'student_id', 'course_id', 'academic_year', 
                    'term', 'enrollment_date'],
    'grades': ['grades_id', 'enrollment_id', 'grade_type', 'grade_value', 'grade_date'],
    'attendance': ['attendance_id', 'enrollment_id', 'attendance_date', 'status']
}

# Valid values for CHECK constraints in the database
VALID_VALUES = {
    'student_status': ['active', 'inactive', 'graduated'],
    'course_status': ['active', 'inactive'],
    'grade_type': ['test', 'assignment', 'exam'],
    'grade_value_range': (0, 100),
    'enrollment_term': ['1', '2'],
    'attendance_status': ['present', 'absent', 'late']
}


# ============================================================================
# STEP 1: EXTRACT - Read CSV files
# ============================================================================

def extract_data(data_dir=DATA_DIR):
    """
    Read all CSV files into pandas DataFrames.
    
    Args:
        data_dir: Path to directory containing CSV files
        
    Returns:
        Dictionary with table names as keys and DataFrames as values
    """
    print("\n[EXTRACT] Reading CSV files...\n")
    
    datasets = {}
    
    for table_name in LOAD_ORDER:
        file_path = os.path.join(data_dir, f"{table_name}.csv")
        
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            datasets[table_name] = df
            print(f"  ✓ {table_name}.csv: {len(df)} rows, {len(df.columns)} columns")
        except FileNotFoundError:
            print(f"  ✗ ERROR: {file_path} not found")
            raise
        except Exception as e:
            print(f"  ✗ ERROR reading {file_path}: {str(e)}")
            raise
    
    return datasets


# ============================================================================
# STEP 2: TRANSFORM - Validate and clean data
# ============================================================================

def validate_columns(df, table_name, expected_columns):
    """
    Check that all expected columns exist in the DataFrame.
    
    Args:
        df: DataFrame to validate
        table_name: Name of the table (for error messages)
        expected_columns: List of expected column names
        
    Returns:
        True if valid, False otherwise
    """
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        print(f"  ✗ {table_name}: Missing columns: {missing_columns}")
        return False
    return True


def validate_no_nulls(df, table_name, required_columns):
    """
    Check that required columns have no NULL values.
    
    Args:
        df: DataFrame to validate
        table_name: Name of the table (for error messages)
        required_columns: List of columns that must not be NULL
        
    Returns:
        True if valid, False otherwise
    """
    null_cols = [col for col in required_columns if df[col].isnull().any()]
    if null_cols:
        print(f"  ✗ {table_name}: NULL values found in: {null_cols}")
        return False
    return True


def validate_student_status(df):
    """Validate that student status values are allowed."""
    invalid = df[~df['status'].isin(VALID_VALUES['student_status'])]
    if len(invalid) > 0:
        print(f"  ✗ students: Invalid status values: {invalid['status'].unique()}")
        return False
    return True


def validate_course_status(df):
    """Validate that course status values are allowed."""
    invalid = df[~df['status'].isin(VALID_VALUES['course_status'])]
    if len(invalid) > 0:
        print(f"  ✗ courses: Invalid status values: {invalid['status'].unique()}")
        return False
    return True


def validate_enrollment_term(df):
    """Validate that enrollment term values are allowed (1 or 2)."""
    invalid = df[~df['term'].astype(str).isin(VALID_VALUES['enrollment_term'])]
    if len(invalid) > 0:
        print(f"  ✗ enrollments: Invalid term values: {invalid['term'].unique()}")
        return False
    return True


def validate_grade_type(df):
    """Validate that grade type values are allowed."""
    invalid = df[~df['grade_type'].isin(VALID_VALUES['grade_type'])]
    if len(invalid) > 0:
        print(f"  ✗ grades: Invalid grade_type values: {invalid['grade_type'].unique()}")
        return False
    return True


def validate_grade_value(df):
    """Validate that grade values are between 0 and 100."""
    min_val, max_val = VALID_VALUES['grade_value_range']
    invalid = df[(df['grade_value'] < min_val) | (df['grade_value'] > max_val)]
    if len(invalid) > 0:
        print(f"  ✗ grades: Grade values outside 0-100 range: {len(invalid)} rows")
        return False
    return True


def validate_attendance_status(df):
    """Validate that attendance status values are allowed."""
    invalid = df[~df['status'].isin(VALID_VALUES['attendance_status'])]
    if len(invalid) > 0:
        print(f"  ✗ attendance: Invalid status values: {invalid['status'].unique()}")
        return False
    return True


def transform_data(datasets):
    """
    Validate and clean all datasets.
    
    Args:
        datasets: Dictionary of DataFrames
        
    Returns:
        Cleaned datasets dictionary, or raises exception if validation fails
    """
    print("\n[TRANSFORM] Validating and cleaning data...\n")
    
    # Validate students
    print("  Checking students...")
    df_students = datasets['students']
    assert validate_columns(df_students, 'students', TABLE_COLUMNS['students'])
    assert validate_no_nulls(df_students, 'students', 
                            ['student_id', 'student_number', 'first_name', 'last_name', 'status'])
    # Convert status to lowercase to ensure consistency
    df_students['status'] = df_students['status'].str.lower()
    assert validate_student_status(df_students)
    # Remove duplicates based on student_number (should be unique)
    df_students = df_students.drop_duplicates(subset=['student_number'], keep='first')
    datasets['students'] = df_students
    print(f"    ✓ Valid: {len(df_students)} students (after removing {len(datasets['students']) - len(df_students)} duplicates)")
    
    # Validate courses
    print("  Checking courses...")
    df_courses = datasets['courses']
    assert validate_columns(df_courses, 'courses', TABLE_COLUMNS['courses'])
    assert validate_no_nulls(df_courses, 'courses', 
                            ['course_id', 'course_code', 'course_name', 'status'])
    # Convert status to lowercase to ensure consistency
    df_courses['status'] = df_courses['status'].str.lower()
    assert validate_course_status(df_courses)
    # Remove duplicates based on course_code (should be unique)
    df_courses = df_courses.drop_duplicates(subset=['course_code'], keep='first')
    datasets['courses'] = df_courses
    print(f"    ✓ Valid: {len(df_courses)} courses (after removing {len(datasets['courses']) - len(df_courses)} duplicates)")
    
    # Validate enrollments
    print("  Checking enrollments...")
    df_enrollments = datasets['enrollments']
    assert validate_columns(df_enrollments, 'enrollments', TABLE_COLUMNS['enrollments'])
    assert validate_no_nulls(df_enrollments, 'enrollments', 
                            ['enrollment_id', 'student_id', 'course_id', 'term'])
    # Convert term to string and ensure it's valid
    df_enrollments['term'] = df_enrollments['term'].astype(str).str.strip()
    assert validate_enrollment_term(df_enrollments)
    # Fix academic_year format: if it's just a year, convert to YYYY-YYYY+1
    df_enrollments['academic_year'] = df_enrollments['academic_year'].apply(
        lambda x: f"{int(str(x).split('-')[0])}-{int(str(x).split('-')[0]) + 1}" 
        if '-' in str(x) and len(str(x).split('-')[0]) == 4 
        else f"{int(str(x))}-{int(str(x)) + 1}"
    )
    # Remove duplicate enrollments (same student + course + year + term)
    df_enrollments = df_enrollments.drop_duplicates(
        subset=['student_id', 'course_id', 'academic_year', 'term'], keep='first')
    datasets['enrollments'] = df_enrollments
    print(f"    ✓ Valid: {len(df_enrollments)} enrollments (after removing {len(datasets['enrollments']) - len(df_enrollments)} duplicates)")
    
    # Validate grades
    print("  Checking grades...")
    df_grades = datasets['grades']
    assert validate_columns(df_grades, 'grades', TABLE_COLUMNS['grades'])
    assert validate_no_nulls(df_grades, 'grades', 
                            ['grades_id', 'enrollment_id', 'grade_type', 'grade_value'])
    # Convert grade_type to lowercase to ensure consistency
    df_grades['grade_type'] = df_grades['grade_type'].str.lower()
    assert validate_grade_type(df_grades)
    # Ensure grade_value is integer and within 0-100
    df_grades['grade_value'] = df_grades['grade_value'].astype(int)
    df_grades['grade_value'] = df_grades['grade_value'].clip(lower=0, upper=100)
    assert validate_grade_value(df_grades)
    datasets['grades'] = df_grades
    print(f"    ✓ Valid: {len(df_grades)} grades")
    
    # Validate attendance
    print("  Checking attendance...")
    df_attendance = datasets['attendance']
    assert validate_columns(df_attendance, 'attendance', TABLE_COLUMNS['attendance'])
    assert validate_no_nulls(df_attendance, 'attendance', 
                            ['attendance_id', 'enrollment_id', 'status'])
    # Convert status to lowercase to ensure consistency
    df_attendance['status'] = df_attendance['status'].str.lower()
    assert validate_attendance_status(df_attendance)
    # Convert attendance_date to datetime (timestamp)
    df_attendance['attendance_date'] = pd.to_datetime(df_attendance['attendance_date'])
    datasets['attendance'] = df_attendance
    print(f"    ✓ Valid: {len(df_attendance)} attendance records")
    
    return datasets


def validate_foreign_keys(datasets):
    """
    Check referential integrity before loading.
    Ensure that foreign key values exist in parent tables.
    Remove any rows with invalid foreign keys to prevent database errors.
    
    Args:
        datasets: Dictionary of DataFrames
        
    Returns:
        True if all foreign keys are valid, False otherwise
    """
    print("\n[TRANSFORM] Validating foreign keys...\n")
    
    all_valid = True
    
    df_students = datasets['students']
    df_courses = datasets['courses']
    df_enrollments = datasets['enrollments']
    df_grades = datasets['grades']
    df_attendance = datasets['attendance']
    
    valid_student_ids = set(df_students['student_id'])
    valid_course_ids = set(df_courses['course_id'])
    valid_enrollment_ids = set(df_enrollments['enrollment_id'])
    
    # Check: All student_id in enrollments exist in students
    invalid_enrollments = df_enrollments[~df_enrollments['student_id'].isin(valid_student_ids)]
    if len(invalid_enrollments) > 0:
        print(f"  ⚠ enrollments: {len(invalid_enrollments)} rows have invalid student_id - removing them")
        # Remove invalid enrollments
        df_enrollments = df_enrollments[df_enrollments['student_id'].isin(valid_student_ids)]
        datasets['enrollments'] = df_enrollments
        all_valid = False
    else:
        print(f"  ✓ enrollments.student_id: All valid")
    
    # Check: All course_id in enrollments exist in courses
    invalid_enrollments = df_enrollments[~df_enrollments['course_id'].isin(valid_course_ids)]
    if len(invalid_enrollments) > 0:
        print(f"  ⚠ enrollments: {len(invalid_enrollments)} rows have invalid course_id - removing them")
        # Remove invalid enrollments
        df_enrollments = df_enrollments[df_enrollments['course_id'].isin(valid_course_ids)]
        datasets['enrollments'] = df_enrollments
        all_valid = False
    else:
        print(f"  ✓ enrollments.course_id: All valid")
    
    # Update valid_enrollment_ids after cleaning enrollments
    valid_enrollment_ids = set(df_enrollments['enrollment_id'])
    
    # Check: All enrollment_id in grades exist in enrollments
    invalid_grades = df_grades[~df_grades['enrollment_id'].isin(valid_enrollment_ids)]
    if len(invalid_grades) > 0:
        print(f"  ⚠ grades: {len(invalid_grades)} rows have invalid enrollment_id - removing them")
        # Remove invalid grades
        df_grades = df_grades[df_grades['enrollment_id'].isin(valid_enrollment_ids)]
        datasets['grades'] = df_grades
        all_valid = False
    else:
        print(f"  ✓ grades.enrollment_id: All valid")
    
    # Check: All enrollment_id in attendance exist in enrollments
    invalid_attendance = df_attendance[~df_attendance['enrollment_id'].isin(valid_enrollment_ids)]
    if len(invalid_attendance) > 0:
        print(f"  ⚠ attendance: {len(invalid_attendance)} rows have invalid enrollment_id - removing them")
        # Remove invalid attendance records
        df_attendance = df_attendance[df_attendance['enrollment_id'].isin(valid_enrollment_ids)]
        datasets['attendance'] = df_attendance
        all_valid = False
    else:
        print(f"  ✓ attendance.enrollment_id: All valid")
    
    return all_valid


# ============================================================================
# STEP 3: LOAD - Insert data into database
# ============================================================================

def create_database_connection(host, port, database, user, password):
    """
    Create a connection to the PostgreSQL database using SQLAlchemy.
    
    Args:
        host: Database host
        port: Database port
        database: Database name
        user: Database user
        password: Database password
        
    Returns:
        SQLAlchemy engine object
    """
    # Format connection string for PostgreSQL
    password_encoded = quote_plus(password)
    connection_string = f"postgresql+psycopg2://{user}:{password_encoded}@{host}:{port}/{database}"
    
    try:
        engine = create_engine(connection_string)
        # Test the connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print(f"  ✓ Connected to {database} at {host}:{port}")
        return engine
    except Exception as e:
        print(f"  ✗ ERROR: Could not connect to database: {str(e)}")
        raise


def load_data(datasets, engine):
    """
    Insert data into database tables in the correct order.
    Respects foreign key constraints by loading parent tables first.
    
    Args:
        datasets: Dictionary of DataFrames
        engine: SQLAlchemy engine object
        
    Returns:
        True if all inserts succeed, False otherwise
    """
    print("\n[LOAD] Inserting data into database...\n")
    
    all_success = True
    
    # First, drop all tables to clear existing data (using CASCADE to handle foreign keys)
    with engine.connect() as connection:
        try:
            connection.execute(text("DROP TABLE IF EXISTS attendance CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS grades CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS enrollments CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS courses CASCADE"))
            connection.execute(text("DROP TABLE IF EXISTS students CASCADE"))
            connection.commit()
            print("  ✓ Cleared existing tables")
        except Exception as e:
            print(f"  ✗ ERROR clearing tables: {str(e)}")
            all_success = False
    
    # Now insert data in correct order
    for table_name in LOAD_ORDER:
        df = datasets[table_name]
        
        try:
            # Convert DataFrame to SQL (append to empty tables)
            df.to_sql(table_name, con=engine, if_exists='append', index=False)
            print(f"  ✓ Loaded {table_name}: {len(df)} rows inserted")
        except Exception as e:
            print(f"  ✗ ERROR loading {table_name}: {str(e)}")
            all_success = False
    
    return all_success


# ============================================================================
# MAIN ETL FUNCTION
# ============================================================================

def run_etl(data_dir=DATA_DIR):
    """
    Execute the complete ETL pipeline:
    1. Extract data from CSV files
    2. Transform and validate data
    3. Load data into database
    
    Args:
        data_dir: Path to directory containing CSV files
    """
    print("\n" + "="*70)
    print("Student Records Management System - ETL Pipeline")
    print("="*70)
    
    try:
        # EXTRACT: Read CSV files
        datasets = extract_data(data_dir)
        
        # TRANSFORM: Validate and clean data
        datasets = transform_data(datasets)
        validate_foreign_keys(datasets)
        
        # LOAD: Connect to database and insert data
        print("\n[LOAD] Connecting to database...\n")
        engine = create_database_connection(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)
        
        load_data(datasets, engine)
        
        print("\n" + "="*70)
        print("✓ ETL Pipeline completed successfully!")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print("\n" + "="*70)
        print("✗ ETL Pipeline FAILED: Data validation error")
        print("="*70 + "\n")
        return False
    except Exception as e:
        print("\n" + "="*70)
        print(f"✗ ETL Pipeline FAILED: {str(e)}")
        print("="*70 + "\n")
        return False
    
    return True


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    success = run_etl()
    exit(0 if success else 1)
