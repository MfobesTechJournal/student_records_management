from .database import get_connection
from .validation import validate_non_empty


def add_course():
    try:
        course_name = validate_non_empty(input("Course name: "), "Course name")
        course_code = validate_non_empty(input("Course code: "), "Course code").upper()
        credits = int(validate_non_empty(input("Credits: "), "Credits"))

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO courses (course_name, course_code, credits)
                    VALUES (%s, %s, %s)
                    """,
                    (course_name, course_code, credits),
                )
        print("Course added.")
    except Exception as exc:
        print("Error:", exc)


def list_courses():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT course_id, course_name, course_code, credits
                FROM courses
                ORDER BY course_id
                """
            )
            courses = cursor.fetchall()

    if not courses:
        print("No courses found.")
        return

    for course in courses:
        print(course)
