import psycopg2
import random

DB_CONFIG = {
    "dbname": "student_records_db",
    "user": "postgres",
    "password": "123456",
    "host": "localhost",
    "port": 5433
}

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # Get all enrollment IDs that do NOT yet have grades
        cur.execute("""
            SELECT e.enrollment_id
            FROM enrollments e
            LEFT JOIN grades g ON e.enrollment_id = g.enrollment_id
            WHERE g.enrollment_id IS NULL;
        """)

        enrollment_ids = [row[0] for row in cur.fetchall()]

        if not enrollment_ids:
            print("No enrollments available for grading.")
            return

        grades = []

        for enrollment_id in enrollment_ids:
            # realistic grade distribution
            grade = round(random.uniform(45, 95), 2)
            grades.append((enrollment_id, grade))

        insert_query = """
            INSERT INTO grades (enrollment_id, grade)
            VALUES (%s, %s);
        """

        cur.executemany(insert_query, grades)
        conn.commit()

        print(f"Grades inserted: {len(grades)}")

    except Exception as e:
        conn.rollback()
        print("Error generating grades:", e)

    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
