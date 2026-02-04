**# Student Records Management System

## Project Overview
This project implements a complete Student Records Management System using PostgreSQL and Python.  
The system manages students, courses, enrollments, grades, and attendance while supporting analytics for academic performance and engagement.

The project was developed as part of the IBM Data Engineering Professional Certificate and demonstrates relational database design, ETL development, and SQL-based analytics.



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
```

SQL Analytics

Implemented analytics include:

Viewing students enrolled in a specific course

Calculating course-level average grades

Identifying students with attendance below 75%

Ranking top students by GPA

Generating enrollment statistics per course

Queries are located in the sql/analysis_queries.sql file.

Views & Stored Procedures
Views

student_transcripts – consolidated student academic records

attendance_summary – attendance percentages per enrollment

Stored Procedures

enroll_student – enrolls a student in a course safely

record_grade – inserts or updates student grades

These are created directly in PostgreSQL.

Project Structure
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
