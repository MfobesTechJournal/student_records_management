import csv
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from .database import get_connection

def generate_csv():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.first_name || ' ' || s.last_name AS student_name,
               s.email,
               c.course_name,
               e.enrollment_date
        FROM enrollments e
        JOIN students s ON e.student_id = s.student_id
        JOIN courses c ON e.course_id = c.course_id
    """)

    with open("report.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Student", "Email", "Course", "Enrollment Date"])
        writer.writerows(cursor.fetchall())

    conn.close()
    print("CSV report generated.")

def generate_pdf():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.first_name || ' ' || s.last_name AS student_name,
               c.course_name,
               e.enrollment_date
        FROM enrollments e
        JOIN students s ON e.student_id = s.student_id
        JOIN courses c ON e.course_id = c.course_id
    """)

    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()
    content = []

    for row in cursor.fetchall():
        text = f"Student: {row[0]} | Course: {row[1]} | Enrollment Date: {row[2]}"
        content.append(Paragraph(text, styles["Normal"]))

    doc.build(content)
    conn.close()
    print("PDF report generated.")
