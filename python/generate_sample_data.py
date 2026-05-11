"""
Student Records Management System - Sample Data Generator

This script uses the Faker library to generate realistic sample data
for the Student Records Management System.

Generates:
- students.csv
- courses.csv
- enrollments.csv
- grades.csv
- attendance.csv
"""

import os
import csv
from faker import Faker
from datetime import datetime, timedelta
import random

# Initialize Faker with both Zulu and English locales for mixed South African names
fake_zu = Faker('zu_ZA')  # Zulu (South Africa)
fake_en = Faker('en_US')  # English (fallback for mixed names)

# Configuration
OUTPUT_DIR = "../data"
NUM_STUDENTS = 100
NUM_COURSES = 15
NUM_ENROLLMENTS = 200
NUM_GRADES = 400
NUM_ATTENDANCE = 1000

# Course data (hardcoded for consistency)
COURSES_DATA = [
    ("CS101", "Introduction to Computer Science", 3),
    ("CS102", "Data Structures", 3),
    ("CS201", "Algorithms", 4),
    ("CS202", "Database Systems", 4),
    ("CS301", "Web Development", 3),
    ("CS302", "Machine Learning", 4),
    ("MATH101", "Calculus I", 4),
    ("MATH102", "Calculus II", 4),
    ("MATH201", "Linear Algebra", 3),
    ("PHYS101", "Physics I", 4),
    ("PHYS102", "Physics II", 4),
    ("ENG101", "English Composition", 3),
    ("ENG102", "Literature", 3),
    ("CHEM101", "Chemistry I", 4),
    ("CHEM102", "Chemistry II", 4),
]

GRADE_TYPES = ["test", "assignment", "exam"]
ATTENDANCE_STATUS = ["present", "absent", "late"]
STUDENT_STATUS = ["active", "inactive", "graduated"]
ENROLLMENT_TERMS = ["1", "2"]


def generate_students(num_students=NUM_STUDENTS):
    """Generate student data with randomly mixed Zulu and English names."""
    print(f"Generating {num_students} students...")
    
    students = []
    for i in range(1, num_students + 1):
        # Randomly select between Zulu and English locales for each student
        fake = random.choice([fake_zu, fake_en])
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=35)
        # Extract birth year (first 4 digits of student_number)
        birth_year = birth_date.year
        # Add 2 random digits for uniqueness (last 2 digits)
        random_suffix = random.randint(10, 99)
        student_number = int(f"{birth_year}{random_suffix}")
        
        student = {
            'student_id': i,
            'student_number': student_number,  # Pattern: YYYYRR (year + random digits)
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'date_of_birth': birth_date,
            'email': fake.email(),
            'status': random.choice(STUDENT_STATUS)
        }
        students.append(student)
    
    return students


def generate_courses(num_courses=len(COURSES_DATA)):
    """Generate course data."""
    print(f"Generating {num_courses} courses...")
    
    courses = []
    for i, (code, name, credits) in enumerate(COURSES_DATA, 1):
        course = {
            'course_id': i,
            'course_code': code,
            'course_name': name,
            'credits': credits,  # Keep as integer (SQL uses DECIMAL but accepts integers)
            'status': 'active'  # Match SQL: lowercase value
        }
        courses.append(course)
    
    return courses


def generate_enrollments(num_students, num_courses, num_enrollments=NUM_ENROLLMENTS):
    """Generate enrollment data.
    
    Args:
        num_students: Total number of students (ensures valid student_id references)
        num_courses: Total number of courses (ensures valid course_id references)
        num_enrollments: Number of enrollments to generate
    """
    print(f"Generating {num_enrollments} enrollments...")
    
    enrollments = []
    for i in range(1, num_enrollments + 1):
        # Use valid student and course IDs that were actually generated
        student_id = random.randint(1, num_students)
        course_id = random.randint(1, num_courses)
        academic_year = f"{random.randint(2020, 2024)}-{random.randint(2020, 2024)}"  # Format: YYYY-YYYY
        term = random.choice(ENROLLMENT_TERMS)  # Now uses '1' or '2'
        enrollment_date = fake_zu.date_between(start_date='-365d', end_date='today')
        
        enrollment = {
            'enrollment_id': i,
            'student_id': student_id,
            'course_id': course_id,
            'academic_year': academic_year,
            'term': term,
            'enrollment_date': enrollment_date
        }
        enrollments.append(enrollment)
    
    return enrollments


def generate_grades(enrollments, num_grades=NUM_GRADES):
    """Generate grade data based on existing enrollments.
    
    Args:
        enrollments: List of enrollment records (ensures enrollment_id validity)
        num_grades: Number of grades to generate
    """
    print(f"Generating {num_grades} grades...")
    
    # Get list of valid enrollment IDs that were actually generated
    valid_enrollment_ids = [e['enrollment_id'] for e in enrollments]
    
    grades = []
    for i in range(1, num_grades + 1):
        # Only use enrollment IDs that exist
        enrollment_id = random.choice(valid_enrollment_ids)
        grade_type = random.choice(GRADE_TYPES)  # Now uses lowercase values: 'test', 'assignment', 'exam'
        # Ensure grade_value is between 0 and 100 (matches SQL CHECK constraint)
        grade_value = random.randint(0, 100)
        grade_date = fake_zu.date_between(start_date='-365d', end_date='today')
        
        grade = {
            'grades_id': i,
            'enrollment_id': enrollment_id,
            'grade_type': grade_type,
            'grade_value': grade_value,
            'grade_date': grade_date
        }
        grades.append(grade)
    
    return grades


def generate_attendance(enrollments, num_attendance=NUM_ATTENDANCE):
    """Generate attendance data based on existing enrollments.
    
    Args:
        enrollments: List of enrollment records (ensures enrollment_id validity)
        num_attendance: Number of attendance records to generate
    """
    print(f"Generating {num_attendance} attendance records...")
    
    # Get list of valid enrollment IDs that were actually generated
    valid_enrollment_ids = [e['enrollment_id'] for e in enrollments]
    
    attendance = []
    for i in range(1, num_attendance + 1):
        # Only use enrollment IDs that exist
        enrollment_id = random.choice(valid_enrollment_ids)
        attendance_date = fake_zu.date_time_between(start_date='-365d')
        # SQL allows: 'present', 'absent', 'late' (lowercase only)
        status = random.choice(ATTENDANCE_STATUS)
        
        record = {
            'attendance_id': i,
            'enrollment_id': enrollment_id,
            'attendance_date': attendance_date,
            'status': status
        }
        attendance.append(record)
    
    return attendance


def write_csv(filename, fieldnames, data):
    """Write data to CSV file with comma delimiter.
    
    Args:
        filename: Name of the CSV file to create
        fieldnames: List of column names
        data: List of dictionaries containing the data
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Create directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
        # Remove old file if it exists (to avoid permission issues)
    if os.path.exists(filepath):
        os.remove(filepath)
        # Use comma delimiter for all files (consistent and standard)
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        writer.writerows(data)
    
    print(f"  Created {filepath}")


def main():
    """Main function to generate all sample data.
    
    Generation order matters for referential integrity:
    1. Students and courses (no dependencies)
    2. Enrollments (depends on students and courses)
    3. Grades and attendance (depend on enrollments)
    """
    print("\n" + "="*60)
    print("Student Records Management System - Sample Data Generator")
    print("="*60 + "\n")
    
    # Step 1: Generate independent data (no foreign key dependencies)
    students = generate_students()
    courses = generate_courses()
    
    # Step 2: Generate enrollments (depends on students and courses)
    enrollments = generate_enrollments(NUM_STUDENTS, len(COURSES_DATA))
    
    # Step 3: Generate dependent data (grades and attendance only reference existing enrollments)
    grades = generate_grades(enrollments)
    attendance = generate_attendance(enrollments)
    
    # Write all data to CSV files
    print(f"\nWriting CSV files to {OUTPUT_DIR}...\n")
    
    write_csv('students.csv', 
             ['student_id', 'student_number', 'first_name', 'last_name', 'date_of_birth', 'email', 'status'],
             students)
    
    write_csv('courses.csv',
             ['course_id', 'course_code', 'course_name', 'credits', 'status'],
             courses)
    
    write_csv('enrollments.csv',
             ['enrollment_id', 'student_id', 'course_id', 'academic_year', 'term', 'enrollment_date'],
             enrollments)
    
    write_csv('grades.csv',
             ['grades_id', 'enrollment_id', 'grade_type', 'grade_value', 'grade_date'],
             grades)
    
    write_csv('attendance.csv',
             ['attendance_id', 'enrollment_id', 'attendance_date', 'status'],
             attendance)
    
    print("\n" + "="*60)
    print("✓ Sample data generation complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
