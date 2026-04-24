import random
from datetime import date, timedelta

from faker import Faker
from psycopg2.extras import execute_values

from .database import get_connection


fake = Faker()


def seed_students_and_courses(student_count: int = 300, course_count: int = 25) -> None:
    students = [
        (
            fake.first_name(),
            fake.last_name(),
            fake.unique.email(),
            fake.date_of_birth(minimum_age=18, maximum_age=30),
        )
        for _ in range(student_count)
    ]

    courses = [
        (
            fake.unique.job()[:255],
            f"{fake.unique.lexify(text='???').upper()}{random.randint(100, 499)}",
            random.randint(2, 6),
        )
        for _ in range(course_count)
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(
                cur,
                """
                INSERT INTO students (first_name, last_name, email, date_of_birth)
                VALUES %s
                ON CONFLICT (email) DO NOTHING
                """,
                students,
            )
            execute_values(
                cur,
                """
                INSERT INTO courses (course_name, course_code, credits)
                VALUES %s
                ON CONFLICT (course_code) DO NOTHING
                """,
                courses,
            )

    print(f"Seeded up to {student_count} students and {course_count} courses.")


def seed_enrollments(min_courses: int = 3, max_courses: int = 6) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT student_id FROM students ORDER BY student_id;")
            student_ids = [row[0] for row in cur.fetchall()]

            cur.execute("SELECT course_id FROM courses ORDER BY course_id;")
            course_ids = [row[0] for row in cur.fetchall()]

            if not student_ids or not course_ids:
                raise RuntimeError("Students and courses must exist before generating enrollments.")

            enrollments = []
            for student_id in student_ids:
                sample_size = min(random.randint(min_courses, max_courses), len(course_ids))
                for course_id in random.sample(course_ids, sample_size):
                    enrollments.append((student_id, course_id, date.today()))

            execute_values(
                cur,
                """
                INSERT INTO enrollments (student_id, course_id, enrollment_date)
                VALUES %s
                ON CONFLICT (student_id, course_id) DO NOTHING
                """,
                enrollments,
            )

    print(f"Generated {len(enrollments)} enrollment rows.")


def seed_grades() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT e.enrollment_id
                FROM enrollments e
                LEFT JOIN grades g ON g.enrollment_id = e.enrollment_id
                WHERE g.enrollment_id IS NULL
                ORDER BY e.enrollment_id
                """
            )
            enrollment_ids = [row[0] for row in cur.fetchall()]

            if not enrollment_ids:
                print("No unenriched enrollments found for grades.")
                return

            grades = [
                (
                    enrollment_id,
                    round(random.uniform(45, 95), 2),
                    fake.date_between(start_date="-120d", end_date="today"),
                )
                for enrollment_id in enrollment_ids
            ]

            execute_values(
                cur,
                """
                INSERT INTO grades (enrollment_id, grade, graded_at)
                VALUES %s
                """,
                grades,
            )

    print(f"Generated {len(grades)} grade rows.")


def seed_attendance(min_sessions: int = 10, max_sessions: int = 20) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT enrollment_id FROM enrollments ORDER BY enrollment_id;")
            enrollment_ids = [row[0] for row in cur.fetchall()]

            if not enrollment_ids:
                print("No enrollments found for attendance generation.")
                return

            attendance_rows = []
            for enrollment_id in enrollment_ids:
                session_count = random.randint(min_sessions, max_sessions)
                start_day = date.today() - timedelta(days=90)

                for session_index in range(session_count):
                    attendance_rows.append(
                        (
                            enrollment_id,
                            start_day + timedelta(days=session_index * 3),
                            random.random() < 0.85,
                        )
                    )

            execute_values(
                cur,
                """
                INSERT INTO attendance (enrollment_id, attendance_date, present)
                VALUES %s
                """,
                attendance_rows,
            )

    print(f"Generated {len(attendance_rows)} attendance rows.")


def seed_all(student_count: int = 300, course_count: int = 25) -> None:
    seed_students_and_courses(student_count=student_count, course_count=course_count)
    seed_enrollments()
    seed_grades()
    seed_attendance()


if __name__ == "__main__":
    seed_all()
