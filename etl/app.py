from etl.students import add_student, list_students, delete_student
from etl.courses import add_course, list_courses
from etl.enrollments import enroll_student, record_grade, mark_attendance
from etl.reports import generate_csv, generate_pdf
from etl.database import setup_database


def menu():
    print("""
1. Add Student
2. List Students
3. Delete Student
4. Add Course
5. List Courses
6. Enroll Student
7. Record Grade
8. Mark Attendance
9. Generate CSV Report
10. Generate PDF Report
0. Exit
""")

def main():
    setup_database()

    actions = {
        "1": add_student,
        "2": list_students,
        "3": delete_student,
        "4": add_course,
        "5": list_courses,
        "6": enroll_student,
        "7": record_grade,
        "8": mark_attendance,
        "9": generate_csv,
        "10": generate_pdf
    }

    while True:
        menu()
        choice = input("Choose option: ")

        if choice == "0":
            print("Goodbye.")
            break
        elif choice in actions:
            actions[choice]()
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
