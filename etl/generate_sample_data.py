from faker import Faker
import psycopg2
import random

fake = Faker()

conn = psycopg2.connect(
    dbname="student_records_db",
    user="postgres",
    password="123456",
    host="localhost",
    port="5433"
)

cur = conn.cursor()

# ---- Students ----
students = []
for _ in range(300):
    students.append((
        fake.first_name(),
        fake.last_name(),
        fake.unique.email(),
        fake.date_of_birth(minimum_age=18, maximum_age=30)
    ))

cur.executemany("""
    INSERT INTO students (first_name, last_name, email, date_of_birth)
    VALUES (%s, %s, %s, %s)
""", students)

# ---- Courses ----
courses = []
for _ in range(25):
    courses.append((
        fake.unique.word().title(),        # Course Name
        fake.unique.bothify(text='??-###').upper(), # Course Code (e.g., EN-482)
        random.randint(1, 6)               # Credits
    ))

# Updated to include the course_code column
cur.executemany("""
    INSERT INTO courses (course_name, course_code, credits)
    VALUES (%s, %s, %s)
""", courses)

conn.commit()
cur.close()
conn.close()

print("Sample students and courses inserted successfully.")