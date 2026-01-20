import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
import logging
from db_config import DB_CONFIG

# -------------------------
# LOGGING SETUP
# -------------------------
logging.basicConfig(
    filename="logs/etl.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# -------------------------
# CONNECT TO DATABASE
# -------------------------
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

try:
    # -------------------------
    # LOAD STUDENTS
    # -------------------------
    students_df = pd.read_csv("data/students.csv")

    insert_students_sql = """
        INSERT INTO students (student_id, first_name, last_name, email)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (student_id) DO NOTHING;
    """

    students_data = [
        (row.student_id, row.first_name, row.last_name, row.email)
        for row in students_df.itertuples()
    ]

    execute_batch(cur, insert_students_sql, students_data)
    conn.commit()
    logging.info("Students loaded successfully")

    # -------------------------
    # LOAD COURSES
    # -------------------------
    courses_df = pd.read_csv("data/courses.csv")

    insert_courses_sql = """
        INSERT INTO courses (course_id, course_name)
        VALUES (%s, %s)
        ON CONFLICT (course_id) DO NOTHING;
    """

    courses_data = [
        (row.course_id, row.course_name)
        for row in courses_df.itertuples()
    ]

    execute_batch(cur, insert_courses_sql, courses_data)
    conn.commit()
    logging.info("Courses loaded successfully")

    # -------------------------
    # LOAD ENROLLMENTS
    # -------------------------
    enrollments_df = pd.read_csv("data/enrollments.csv")

    insert_enrollments_sql = """
        INSERT INTO enrollments (enrollment_id, student_id, course_id, enrollment_date)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (enrollment_id) DO NOTHING;
    """

    enrollments_data = [
        (row.enrollment_id, row.student_id, row.course_id, row.enrollment_date)
        for row in enrollments_df.itertuples()
    ]

    execute_batch(cur, insert_enrollments_sql, enrollments_data)
    conn.commit()
    logging.info("Enrollments loaded successfully")

    print("ETL load completed successfully.")

except Exception as e:
    conn.rollback()
    logging.error(f"ETL load failed: {e}")
    print("ETL load failed. Check logs.")

finally:
    cur.close()
    conn.close()
