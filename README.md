# Student Records Management System

A Python and PostgreSQL system for managing student records, course enrollments, grades, and attendance. Built as a portfolio project demonstrating relational database design, ETL pipeline development, and SQL analytics.

---

## What It Does

- Stores and manages students, courses, enrollments, grades, and attendance
- Generates realistic academic data using Faker (300+ students, 25 courses)
- Supports local PostgreSQL and AWS RDS / Aurora PostgreSQL
- Optionally resolves database credentials from AWS Secrets Manager

---

## Project Structure

```
Student_Management/
├── etl/
│   ├── seed_data.py              # Core seeding logic (students, courses, enrollments, grades, attendance)
│   ├── database.py               # Connection management and schema setup
│   ├── secrets.py                # Credential resolution (local .env or AWS Secrets Manager)
│   ├── students.py               # Student CRUD operations
│   ├── courses.py                # Course CRUD operations
│   ├── validation.py             # Input validation utilities
│   ├── generate_sample_data.py   # Seed students and courses
│   ├── generate_enrollments.py   # Seed enrollments
│   ├── generate_grades.py        # Seed grades
│   ├── generate_attendance.py    # Seed attendance
│   └── generate_academic_data.py # Run full seed pipeline in one command
├── sql-queries/
│   ├── schema.sql                # Database schema
│   └── analysis_queries.sql      # Analytics queries (GPA, attendance, performance)
├── data/                         # Generated CSV exports
├── logs/                         # ETL run logs (git-ignored)
├── .env.example                  # Environment variable template
└── requirements.txt
```

---

## Database Schema

The schema is normalized around the `enrollments` table, which links students to courses. Grades and attendance both reference enrollments to avoid duplication.

```
students ──┐
           ├──> enrollments ──> grades
courses  ──┘         │
                     └──> attendance
```

Key constraints:
- `students.email` is unique
- `courses.course_code` is unique
- `(student_id, course_id)` pair is unique in enrollments
- `grades.grade` is constrained between 0 and 100
- All foreign keys enforce referential integrity

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL (local or AWS RDS)

### Setup

```bash
# Clone the repository
git clone https://github.com/MfobesTechJournal/student_records_management.git
cd student_records_management

# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure your database connection
cp .env.example .env
# Edit .env with your database credentials
```

### Apply the Schema

```bash
python -m etl.database
```

### Seed All Data (one command)

```bash
python -m etl.generate_academic_data
```

### Or seed step by step

```bash
python -m etl.generate_sample_data    # Students and courses
python -m etl.generate_enrollments    # Enrollments
python -m etl.generate_grades         # Grades
python -m etl.generate_attendance     # Attendance
```

---

## AWS Support

The project supports AWS-hosted PostgreSQL databases and optional credential management via AWS Secrets Manager.

### Connecting to Amazon RDS or Aurora PostgreSQL

1. Copy `.env.example` to `.env`
2. Set your RDS endpoint as `DB_HOST`
3. Set `DB_SSLMODE=require` for AWS connections
4. Restrict inbound PostgreSQL access to your IP in the RDS security group

### Using AWS Secrets Manager

Store your credentials as a JSON secret:

```json
{
  "DB_HOST": "your-rds-endpoint.amazonaws.com",
  "DB_PORT": "5432",
  "DB_NAME": "student_management",
  "DB_USER": "postgres",
  "DB_PASSWORD": "your-password",
  "DB_SSLMODE": "require"
}
```

Then set in `.env`:

```
AWS_SECRETS_MANAGER_SECRET_NAME=your-secret-name
AWS_REGION=us-east-1
```

---

## SQL Analytics

Queries in `sql-queries/analysis_queries.sql` cover:

- Weighted GPA calculation per student
- Course-level average grade analysis
- Students with attendance below 75% (early intervention flag)
- Top performers ranked by GPA

---

## Tech Stack

| Tool | Purpose |
|---|---|
| PostgreSQL | Relational database |
| Python | ETL scripts and data generation |
| psycopg2 | PostgreSQL driver |
| Faker | Realistic test data generation |
| python-dotenv | Local environment variable loading |
| boto3 | AWS SDK (Secrets Manager, optional) |

---

## Security Notes

- `.env` is git-ignored and should never be committed
- No credentials are hardcoded anywhere in the codebase
- Production deployments should use AWS Secrets Manager instead of `.env`
