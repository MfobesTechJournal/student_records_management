import csv
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from .database import get_connection

def generate_csv():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.name, s.email, c.name, e.grade, e.attendance
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN courses c ON e.course_id = c.id
    """)

    with open("report.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Student", "Email", "Course", "Grade", "Attendance"])
        writer.writerows(cursor.fetchall())

    conn.close()
    print("CSV report generated.")

def generate_pdf():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.name, c.name, e.grade, e.attendance
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN courses c ON e.course_id = c.id
    """)

    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()
    content = []

    for row in cursor.fetchall():
        text = f"Student: {row[0]} | Course: {row[1]} | Grade: {row[2]} | Attendance: {row[3]}"
        content.append(Paragraph(text, styles["Normal"]))

    doc.build(content)
    conn.close()
    print("PDF report generated.")
