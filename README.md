🎓 Student Records Management System
Project Overview
This project implements a complete Student Records Management System using PostgreSQL and Python. The system manages students, courses, enrollments, grades, and attendance while supporting deep analytics for academic performance and engagement.

Developed as part of the IBM Data Engineering Professional Certificate, this repository demonstrates core competencies in:

Relational Database Design (Normalization, Constraints, ERDs).

ETL Pipeline Development (Python, Faker, Batch Loading).

SQL Analytics (Complex Queries, Views, and Stored Procedures).

🏗️ Database Design
The database follows a normalized relational schema centered around the enrollments table to ensure data integrity and minimize redundancy.

Key Principles:

Normalized Schema: Grades and attendance reference enrollments rather than students directly to maintain a clean relationship history.

Integrity Constraints: Strict enforcement of NOT NULL for critical fields (like course_code and graded_at), UNIQUE identifiers, and CHECK constraints for valid grade ranges.

Relational Mapping: Referential integrity is enforced using foreign keys across all five core tables.

⚙️ ETL Pipeline (Python)
Data Generation & Transformation
Faker Integration: Programmatically generates 300+ students and 25 courses.

Validation Logic:

Validates email formats and date ranges.

Ensures grades are clamped within the 0–100 range.

Generates unique, high-fidelity Course Codes (e.g., CS-101) to satisfy schema constraints.

Consistency Fixes: Attendance records are transformed from raw statuses into boolean logic for optimized analytics.

Load Process
Data is loaded into PostgreSQL via Psycopg2 using batch inserts. The pipeline is designed to be idempotent:

Transactions: Uses conn.rollback() and conn.commit() to ensure atomic operations (no partial data loads).

Port Specificity: Specifically configured to connect via Port 5433 to accommodate custom Windows/PostgreSQL environments.

To run the ETL pipeline:

Bash
python etl/generate_sample_data.py
python etl/generate_enrollments.py
python etl/generate_grades.py
python etl/generate_attendance.py
📊 SQL Analytics & Stored Logic
Views & Stored Procedures
student_transcripts: A consolidated view of academic performance.

attendance_summary: Calculates attendance percentages per enrollment.

enroll_student: A stored procedure to safely enroll students while checking for existing records.

fn_calculate_gpa: A function to calculate weighted GPAs based on course credits.

Analytics Queries
Queries located in sql-queries/analysis_queries.sql cover:

Course-level average grade calculations.

Identifying students with attendance below 75% for intervention.

Ranking top-performing students by weighted GPA.

📂 Project Structure
Plaintext
Student_Management/
│
├── data/                # CSV data exports
├── etl/                 # Python ETL scripts & CLI Application
├── logs/                # Traceability logs (Git ignored)
├── sql-queries/         # Database schema, views, and procedures
├── README.md            # Project documentation
└── ERD.pdf              # Entity Relationship Diagram
🛠️ Technologies Used
Database: PostgreSQL 16 (Port 5433)

Python Libraries: psycopg2, faker, random

Tools: pgAdmin 4, VS Code, Git
