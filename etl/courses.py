from .validation import validate_non_empty
from .database import get_connection


def add_course():
    try:
        name = validate_non_empty(input("Course name: "), "Course name")
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO courses (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
        print("Course added.")
    except Exception as e:
        print("Error:", e)

def list_courses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    if not courses:
        print("No courses found.")
        return

    for course in courses:
        print(course)

