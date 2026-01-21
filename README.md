Student Records Management System

Project Overview



This project implements a relational database for managing student records, including enrollments, grades, and attendance. The core design principle is that enrollments sit at the center of all academic data, ensuring that grades and attendance are always tied to a specific student-course relationship.



The system includes:



A normalized PostgreSQL schema



A Python-based ETL pipeline



Sample data generation using Faker



Analytical SQL queries for academic performance and attendance insights



Database Design Summary



Students represent individuals registered in the system.



Courses represent academic offerings.



Enrollments link students to courses and act as the parent entity for:



Grades



Attendance records



This structure avoids ambiguity, duplication, and incorrect aggregation by ensuring that every grade and attendance record belongs to a specific enrollment, not just a student or a course.



An ERD diagram is included in the repository as a PNG file.



ETL Pipeline (Python)



The ETL pipeline is intentionally simple and transparent, focusing on correctness and clarity rather than complexity.



Tools Used



Python 3.12



Faker



pandas



psycopg2



PostgreSQL



Step 1: Data Generation (Extract)



Script: etl/generate\_data.py



This script generates realistic but synthetic data that matches the database schema.



What it does:



Creates 20–50 fake students using Faker



Uses predefined course IDs that already exist in the database



Generates enrollments linking students to courses



Writes the data to CSV files in the /data directory:



students.csv



courses.csv



enrollments.csv



Purpose:



Simulates real-world source data



Ensures referential integrity before loading



Step 2: Data Validation \& Transformation



Basic validation is performed in Python before loading:



Required fields are enforced



Foreign key relationships are checked implicitly by design



Data types are aligned with the database schema



The goal is to prevent invalid records from reaching the database.



Step 3: Data Loading (Load)



Script: etl/load\_data.py



What this script does:



Connects to PostgreSQL using credentials from environment variables



Loads CSV files in dependency order:



Students



Courses



Enrollments



Uses batch inserts for efficiency



Logs progress and errors to logs/etl.log



A successful run ends with:



ETL load completed successfully.



Environment Configuration



Database credentials are stored in a .env file and are not committed to GitHub.



Example .env structure:



DB\_HOST=localhost

DB\_PORT=5433

DB\_NAME=student\_records\_db

DB\_USER=postgres

DB\_PASSWORD=your\_password\_here





The ETL scripts read these values at runtime.



SQL Analysis



The project includes SQL queries that analyze:



Average grades per student and course



Attendance percentages per enrollment



Combined insights linking engagement (attendance) and performance (grades)



Screenshots of query results from pgAdmin are included in the repository.



Repository Structure

Student\_Management/

│

├── schema.sql

├── attendance.sql

├── data/

│   ├── students.csv

│   ├── courses.csv

│   └── enrollments.csv

│

├── etl/

│   ├── generate\_data.py

│   ├── load\_data.py

│   └── db\_config.py

│

├── logs/

│   └── etl.log

│

├── README.md

└── screenshots / diagrams



Key Insight



Grades show what a student knows.

Attendance shows how a student engages.



By anchoring both to enrollments, the database distinguishes capability from commitment, enabling accurate academic insight.

