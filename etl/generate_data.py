from faker import Faker
import pandas as pd
import random

# Initialize Faker
fake = Faker()

# -------------------------
# CONFIGURATION
# -------------------------
NUM_STUDENTS = 30

COURSES = [
    {"course_id": 1, "course_name": "Database systems"},
    {"course_id": 2, "course_name": "Data Analytics"},
]

# -------------------------
# GENERATE STUDENTS
# -------------------------
students = []

for student_id in range(1, NUM_STUDENTS + 1):
    students.append({
        "student_id": student_id,
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.unique.email(),
    })

students_df = pd.DataFrame(students)

# -------------------------
# GENERATE COURSES
# -------------------------
courses_df = pd.DataFrame(COURSES)

# -------------------------
# GENERATE ENROLLMENTS
# -------------------------
enrollments = []
enrollment_id = 1

for student in students:
    # Each student enrolls in 1–2 courses
    enrolled_courses = random.sample(COURSES, k=random.randint(1, 2))

    for course in enrolled_courses:
        enrollments.append({
            "enrollment_id": enrollment_id,
            "student_id": student["student_id"],
            "course_id": course["course_id"],
            "enrollment_date": fake.date_between(start_date="-1y", end_date="today")
        })
        enrollment_id += 1

enrollments_df = pd.DataFrame(enrollments)

# -------------------------
# SAVE TO CSV FILES
# -------------------------
students_df.to_csv("data/students.csv", index=False)
courses_df.to_csv("data/courses.csv", index=False)
enrollments_df.to_csv("data/enrollments.csv", index=False)

print("Data generation complete.")
print(f"Students generated: {len(students_df)}")
print(f"Courses generated: {len(courses_df)}")
print(f"Enrollments generated: {len(enrollments_df)}")
