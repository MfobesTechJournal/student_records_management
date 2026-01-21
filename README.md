ETL Pipeline



This project includes a Python-based ETL pipeline designed to generate, validate, and load student records data into PostgreSQL. The pipeline prioritizes correctness, traceability, and schema alignment rather than unnecessary complexity.



Tools Used



Python 3



Faker



pandas



psycopg2



PostgreSQL



Step 1: Data Generation (Extract)



Script: etl/generate\_data.py



The data generation script creates realistic synthetic data that conforms to the database schema.



What the script generates:



20–50 students with realistic names and email addresses



Predefined courses that already exist in the database



Enrollment records linking students to courses



The output is written to CSV files in the /data directory:



students.csv



courses.csv



enrollments.csv



This simulates real-world source files and ensures referential integrity before loading.



Step 2: Validation and Transformation



Basic validation is applied before loading:



Required fields are enforced



IDs align with database primary and foreign keys



Data types are compatible with the schema



The transformation step is intentionally minimal, ensuring that only valid and schema-compliant records are loaded.



Step 3: Load into PostgreSQL



Script: etl/load\_data.py



This script:



Reads database credentials from environment variables



Connects to PostgreSQL using psycopg2



Loads CSV files in dependency order (students → courses → enrollments)



Uses batch inserts for efficiency



Logs ETL execution details and errors to a local log file



A successful run ends with the message:



ETL load completed successfully.



Environment Configuration



Database credentials are stored in a .env file and excluded from version control.



Example .env structure:



DB\_HOST=localhost

DB\_PORT=5433

DB\_NAME=student\_records\_db

DB\_USER=postgres

DB\_PASSWORD=123456

