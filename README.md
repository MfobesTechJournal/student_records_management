**# Student Records Management System

## Project Overview
This project implements a complete Student Records Management System using PostgreSQL and Python.  
The system manages students, courses, enrollments, grades, and attendance while supporting analytics for academic performance and engagement.

Developed as part of the IBM Data Engineering Professional Certificate, this repository demonstrates core competencies in:

Relational Database Design (Normalization, Constraints, ERDs).

ETL Pipeline Development (Python, Faker, Batch Loading).

SQL Analytics (Complex Queries, Views, and Stored Procedures).



## Database Design
The database follows a normalized relational schema centered around enrollments.

Key design principles:
- Students enroll in courses through an enrollment table
- Grades and attendance reference enrollments to avoid duplication
- Referential integrity enforced using foreign keys
- Constraints ensure data validity (NOT NULL, UNIQUE, CHECK)

An ERD diagram is included in the repository.

---

## ETL Pipeline (Python)

### Data Generation
- Faker is used to generate realistic student data
- 300+ students and 25 courses are created
- Enrollments, grades, and attendance records are generated programmatically

### Extract
- Data is generated and saved as CSV files
- CSV files are stored in the `/data` directory

### Transform
- Missing values are handled before loading
- Email formats are validated
- Attendance records are aggregated
- Grades are validated within accepted ranges

### Load
- Data is loaded into PostgreSQL using batch inserts
- Transactions ensure rollback on failure
- Logging is implemented for traceability

To run ETL:
```bash
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
├── data/               # CSV files
├── etl/                # Python ETL scripts
├── logs/               # ETL logs (ignored in Git)
├── schema.sql          # Database schema
├── sql/                # Analytics queries
├── ERD.pdf             # Entity Relationship Diagram
├── README.md

Technologies Used

PostgreSQL

Python (psycopg2, Faker, pandas)

SQL

pgAdmin / psql
