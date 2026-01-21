Student Records Management System

Project Overview

This project implements a simple Student Records Management System using Python and PostgreSQL.
It demonstrates an end-to-end ETL pipeline that loads student, course, and enrollment data from CSV files into a relational database.

The goal of the project is to show practical data engineering fundamentals:

- Structured data modeling
- ETL pipeline design
- Database interaction using Python
- Reproducible project structure

Folder Structure:

Student_Management/
│
├── data/
│   ├── students.csv
│   ├── courses.csv
│   └── enrollments.csv
│
├── etl/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   └── run_etl.py
│
├── logs/
│   └── etl.log
│
├── .gitignore
├── requirements.txt
└── README.md

ETL Process

Extract

The extract step reads raw CSV files containing students, courses, and enrollment data.
The data is loaded into memory using Python’s CSV or pandas functionality.

Transform

 Transformations are applied to ensure data consistency:
- Data type validation
- Handling missing values
- Standardizing column names

Load

The cleaned data is loaded into a PostgreSQL database.
Tables are created if they do not already exist, and records are inserted using SQL statements executed from Python.

The ETL process can be run end-to-end using the main script:
python etl/run_etl.py

Requirements
- Python 3.x
- PostgreSQL
- Required Python packages listed in `requirements.txt`

Notes
Environment variables such as database credentials are expected to be configured locally.

