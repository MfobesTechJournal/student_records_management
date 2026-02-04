from .validation import validate_non_empty
from .database import get_connection

def add_student():
    try:
        name = validate_non_empty(input("Student name: "), "Name")
        email = validate_non_empty(input("Student email: "), "Email")

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, email) VALUES (%s, %s)",
            (name, email)
        )
        conn.commit()
        conn.close()
        print("Student added.")
    except Exception as e:
        print("Error:", e)

def list_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    for row in cursor.fetchall():
        print(row)
    conn.close()

def delete_student():
    student_id = input("Student ID: ")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    print("Student deleted.")
