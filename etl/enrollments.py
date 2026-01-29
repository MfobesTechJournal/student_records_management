from .database import get_connection
from .validation import validate_non_empty

def enroll_student():
    student_id = input("Student ID: ")
    course_id = input("Course ID: ")

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
            (student_id, course_id)
        )
        conn.commit()
        print("Student enrolled.")
    except Exception as e:
        print("Error:", e)
    conn.close()

def record_grade():
    student_id = input("Student ID: ")
    course_id = input("Course ID: ")
    grade = validate_non_empty(input("Grade: "), "Grade")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE enrollments
        SET grade = ?
        WHERE student_id = ? AND course_id = ?
    """, (grade, student_id, course_id))
    conn.commit()
    conn.close()
    print("Grade recorded.")

def mark_attendance():
    student_id = input("Student ID: ")
    course_id = input("Course ID: ")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE enrollments
        SET attendance = attendance + 1
        WHERE student_id = ? AND course_id = ?
    """, (student_id, course_id))
    conn.commit()
    conn.close()
    print("Attendance marked.")
