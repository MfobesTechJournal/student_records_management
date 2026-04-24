from .database import get_connection
from .validation import validate_date, validate_grade, validate_non_empty


def enroll_student():
    student_id = input("Student ID: ").strip()
    course_id = input("Course ID: ").strip()
    enrollment_date = validate_date(input("Enrollment date (YYYY-MM-DD): "))

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO enrollments (student_id, course_id, enrollment_date)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (student_id, course_id) DO NOTHING
                    """,
                    (student_id, course_id, enrollment_date),
                )
        print("Student enrolled.")
    except Exception as exc:
        print("Error:", exc)


def record_grade():
    enrollment_id = input("Enrollment ID: ").strip()
    grade = validate_grade(validate_non_empty(input("Grade: "), "Grade"))
    graded_at = validate_date(input("Grade date (YYYY-MM-DD): "))

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO grades (enrollment_id, grade, graded_at)
                VALUES (%s, %s, %s)
                """,
                (enrollment_id, grade, graded_at),
            )
    print("Grade recorded.")


def mark_attendance():
    enrollment_id = input("Enrollment ID: ").strip()
    attendance_date = validate_date(input("Attendance date (YYYY-MM-DD): "))
    present_raw = validate_non_empty(input("Present? (yes/no): "), "Present flag").lower()
    present = present_raw in {"yes", "y", "true", "1"}

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO attendance (enrollment_id, attendance_date, present)
                VALUES (%s, %s, %s)
                """,
                (enrollment_id, attendance_date, present),
            )
    print("Attendance marked.")
