import psycopg2
import random
from datetime import date

DB_CONFIG = {
    "dbname": "student_records_db",
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
    "port": "5433"
}

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # Fetch students and courses
        cur.execute("SELECT student_id FROM students;")
        students = [row[0] for row in cur.fetchall()]

        cur.execute("SELECT course_id FROM courses;")
        courses = [row[0] for row in cur.fetchall()]

        enrollments = []

        for student_id in students:
            num_courses = random.randint(3, 6)
            selected_courses = random.sample(courses, num_courses)

            for course_id in selected_courses:
                enrollments.append(
                    (student_id, course_id, date.today())
                )

        insert_query = """
            INSERT INTO enrollments (student_id, course_id, enrollment_date)
            VALUES (%s, %s, %s)
            ON CONFLICT (student_id, course_id) DO NOTHING;
        """

        cur.executemany(insert_query, enrollments)
        conn.commit()

        print(f"Enrollments inserted: {cur.rowcount}")

    except Exception as e:
        conn.rollback()
        print("Error:", e)

    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
