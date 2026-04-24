from .database import get_connection
from .validation import validate_date, validate_email, validate_non_empty


def add_student():
    try:
        first_name = validate_non_empty(input("First name: "), "First name")
        last_name = validate_non_empty(input("Last name: "), "Last name")
        email = validate_email(validate_non_empty(input("Email: "), "Email"))
        date_of_birth = validate_date(input("Date of birth (YYYY-MM-DD): "))

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO students (first_name, last_name, email, date_of_birth)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (first_name, last_name, email, date_of_birth),
                )
        print("Student added.")
    except Exception as exc:
        print("Error:", exc)


def list_students():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT student_id, first_name, last_name, email, date_of_birth, registered_at
                FROM students
                ORDER BY student_id
                """
            )
            for row in cursor.fetchall():
                print(row)


def delete_student():
    student_id = input("Student ID: ").strip()
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
            deleted = cursor.rowcount
    print("Student deleted." if deleted else "Student not found.")
