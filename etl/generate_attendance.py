import psycopg2
import random
from datetime import date, timedelta

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
        
        cur.execute("SELECT enrollment_id FROM enrollments;")
        enrollment_ids = [row[0] for row in cur.fetchall()]

        if not enrollment_ids:
            print("No enrollments found.")
            return

        attendance_rows = []

        for enrollment_id in enrollment_ids:
            
            num_sessions = random.randint(10, 20)

            start_date = date.today() - timedelta(days=90)

            for i in range(num_sessions):
                attendance_date = start_date + timedelta(days=i * 3)
                present = random.random() < 0.85  

                attendance_rows.append(
                    (enrollment_id, attendance_date, present)
                )

        insert_query = """
            INSERT INTO attendance (enrollment_id, attendance_date, present)
            VALUES (%s, %s, %s);
        """

        cur.executemany(insert_query, attendance_rows)
        conn.commit()

        print(f"Attendance records inserted: {len(attendance_rows)}")

    except Exception as e:
        conn.rollback()
        print("Error generating attendance:", e)

    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
