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

# ---------- STUDENTS ----------
students = []
emails = set()

for _ in range(300):
    email = fake.unique.email()
    students.append((
        fake.first_name(),
        fake.last_name(),
        email,
        fake.date_of_birth(minimum_age=18, maximum_age=30)
    ))

cur.executemany("""
    INSERT INTO students (first_name, last_name, email, date_of_birth)
    VALUES (%s, %s, %s, %s)
""", students)

# ---------- COURSES ----------
courses = []
course_names = set()

for _ in range(25):
    course = fake.unique.job()[:150]
    courses.append((course, random.randint(2, 6)))

cur.executemany("""
    INSERT INTO courses (course_name, credits)
    VALUES (%s, %s)
""", courses)

conn.commit()
cur.close()
conn.close()

print("Students and courses inserted successfully.")
