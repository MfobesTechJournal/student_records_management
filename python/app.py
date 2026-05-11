"""
Student Records Management System - Enhanced CLI Application
Features: CRUD with Delete, Search, Pagination, Sorting, and More
"""

import sys
import os
import csv
import hashlib
import uuid
import re
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from db_config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from validators import Validators

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# Institution Information (for audit compliance)
INSTITUTION_INFO = {
    'name': 'Educational Records System',
    'accreditation': 'Certified Academic Institution',
    'email': 'registrar@institution.edu',
    'phone': '+1 (555) 123-4567',
    'address': 'Academic Records Office',
}


# ========================================================================
# DATABASE CONNECTION MODULE
# ========================================================================

class DatabaseConnection:
    """Singleton database connection manager"""
    
    _engine = None
    
    @classmethod
    def get_engine(cls):
        """Get or create database engine"""
        if cls._engine is None:
            connection_string = f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            cls._engine = create_engine(connection_string)
        return cls._engine
    
    @classmethod
    def execute_query(cls, query):
        """Execute a SELECT query and return results"""
        engine = cls.get_engine()
        try:
            with engine.connect() as conn:
                result = conn.execute(text(query))
                return result.fetchall()
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    @classmethod
    def execute_scalar(cls, query):
        """Execute a query and return single value"""
        engine = cls.get_engine()
        try:
            with engine.connect() as conn:
                result = conn.execute(text(query))
                return result.scalar()
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    @classmethod
    def execute_procedure(cls, procedure_call):
        """Execute a stored procedure"""
        engine = cls.get_engine()
        try:
            with engine.connect() as conn:
                conn.execute(text(procedure_call))
                conn.commit()
                return True
        except Exception as e:
            raise Exception(f"Procedure execution failed: {str(e)}")
    
    @classmethod
    def test_connection(cls):
        """Test database connection"""
        engine = cls.get_engine()
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            return False



# ========================================================================
# DATABASE OPERATIONS MODULE
# ========================================================================

class StudentOperations:
    """Student management operations"""
    
    @staticmethod
    def add_student(student_number, first_name, last_name, date_of_birth, email, status='active'):
        """Add a new student to the database with proper ID return"""
        try:
            # Validate inputs first
            valid, msg = Validators.validate_student_number(student_number)
            if not valid:
                return False, msg
            
            valid, msg = Validators.validate_name(first_name)
            if not valid:
                return False, f"First name: {msg}"
            
            valid, msg = Validators.validate_name(last_name)
            if not valid:
                return False, f"Last name: {msg}"
            
            valid, msg = Validators.validate_date_of_birth(date_of_birth)
            if not valid:
                return False, msg
            
            valid, msg = Validators.validate_email(email)
            if not valid:
                return False, msg
            
            valid, msg = Validators.validate_student_status(status)
            if not valid:
                return False, msg
            
            # Escape single quotes in strings to prevent SQL injection
            first_name = first_name.replace("'", "''")
            last_name = last_name.replace("'", "''")
            email = email.replace("'", "''")
            
            query = f"""
                INSERT INTO students (student_number, first_name, last_name, date_of_birth, email, status)
                VALUES ({student_number}, '{first_name}', '{last_name}', '{date_of_birth}', '{email}', '{status.lower()}')
                RETURNING student_id;
            """
            result = DatabaseConnection.execute_query(query)
            if result and len(result) > 0:
                student_id = result[0][0]
                msg = f"Student {first_name} {last_name} (ID: {student_id}) added successfully"
                return True, msg, student_id
            return False, "Failed to retrieve student ID after insertion"
        except Exception as e:
            return False, f"Error adding student: {str(e)}"
    
    @staticmethod
    def get_all_students():
        """Get all students (newest first) with error handling"""
        try:
            query = """
                SELECT student_id, student_number, first_name, last_name, date_of_birth, email, status
                FROM students
                WHERE status != 'deleted'
                ORDER BY student_id DESC
            """
            result = DatabaseConnection.execute_query(query)
            return result if result else []
        except Exception as e:
            return []
    
    @staticmethod
    def get_student_by_id(student_id):
        """Get student by ID with error handling"""
        try:
            query = f"""
                SELECT student_id, student_number, first_name, last_name, date_of_birth, email, status
                FROM students
                WHERE student_id = {student_id} AND status != 'deleted'
            """
            result = DatabaseConnection.execute_query(query)
            if result and len(result) > 0:
                return result[0]
            return None
        except Exception as e:
            return None
    
    @staticmethod
    def get_student_by_number(student_number):
        """Get student by student number"""
        try:
            query = f"""
                SELECT student_id, student_number, first_name, last_name, date_of_birth, email, status
                FROM students
                WHERE student_number = {student_number}
            """
            result = DatabaseConnection.execute_query(query)
            return result[0] if result else None
        except Exception as e:
            return None
    
    @staticmethod
    def update_student_status(student_id, status):
        """Update student status"""
        try:
            query = f"""
                UPDATE students
                SET status = '{status.lower()}'
                WHERE student_id = {student_id}
            """
            DatabaseConnection.execute_procedure(query)
            return True, f"Student status updated to '{status}'"
        except Exception as e:
            return False, f"Error updating status: {str(e)}"


class CourseOperations:
    """Course management operations"""
    
    @staticmethod
    def get_all_courses():
        """Get all courses"""
        try:
            query = """
                SELECT course_id, course_code, course_name, credits, status
                FROM courses
                WHERE status = 'active'
                ORDER BY course_code
            """
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            return None
    
    @staticmethod
    def get_course_by_id(course_id):
        """Get course by ID"""
        try:
            query = f"""
                SELECT course_id, course_code, course_name, credits, status
                FROM courses
                WHERE course_id = {course_id}
            """
            result = DatabaseConnection.execute_query(query)
            return result[0] if result else None
        except Exception as e:
            return None


class EnrollmentOperations:
    """Enrollment management operations"""
    
    @staticmethod
    def add_enrollment(student_id, course_id, academic_year, term):
        """Add new enrollment"""
        try:
            query = f"""
                INSERT INTO enrollments (student_id, course_id, academic_year, term, enrollment_date)
                VALUES ({student_id}, {course_id}, '{academic_year}', '{term}', CURRENT_DATE)
                RETURNING enrollment_id;
            """
            result = DatabaseConnection.execute_query(query)
            if result:
                return True, f"Enrollment added successfully (ID: {result[0][0]})"
            return False, "Failed to add enrollment"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def get_all_enrollments():
        """Get all enrollments (newest first)"""
        try:
            query = """
                SELECT enrollment_id, student_id, course_id, academic_year, term, enrollment_date
                FROM enrollments
                ORDER BY enrollment_id DESC
            """
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            return []
    
    @staticmethod
    def get_enrollment_by_id(enrollment_id):
        """Get enrollment by ID"""
        try:
            query = f"""
                SELECT enrollment_id, student_id, course_id, academic_year, term, enrollment_date
                FROM enrollments
                WHERE enrollment_id = {enrollment_id}
            """
            result = DatabaseConnection.execute_query(query)
            return result[0] if result else None
        except Exception as e:
            return None
    
    @staticmethod
    def get_student_enrollments(student_id):
        """Get all enrollments for a student"""
        try:
            query = f"""
                SELECT e.enrollment_id, s.student_number, c.course_code, c.course_name, 
                       e.academic_year, e.term, e.enrollment_date
                FROM enrollments e
                JOIN students s ON e.student_id = s.student_id
                JOIN courses c ON e.course_id = c.course_id
                WHERE e.student_id = {student_id}
                ORDER BY e.academic_year DESC, e.term
            """
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            return None
    
    @staticmethod
    def get_course_enrollments(course_id):
        """Get all enrollments for a course"""
        try:
            query = f"""
                SELECT e.enrollment_id, s.student_id, s.student_number, s.first_name, s.last_name,
                       e.academic_year, e.term, e.enrollment_date
                FROM enrollments e
                JOIN students s ON e.student_id = s.student_id
                WHERE e.course_id = {course_id}
                ORDER BY s.student_number
            """
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            return None


class GradeOperations:
    """Grade management operations"""
    
    @staticmethod
    def add_grade(enrollment_id, grade_type, grade_value):
        """Add grade"""
        try:
            query = f"""
                INSERT INTO grades (enrollment_id, grade_type, grade_value, grade_date)
                VALUES ({enrollment_id}, '{grade_type}', {grade_value}, CURRENT_DATE)
                RETURNING grades_id;
            """
            result = DatabaseConnection.execute_query(query)
            if result:
                return True, f"Grade added successfully"
            return False, "Failed to add grade"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def get_all_grades():
        """Get all grades (newest first)"""
        try:
            query = """
                SELECT grades_id, enrollment_id, grade_type, grade_value, grade_date
                FROM grades
                ORDER BY grades_id DESC
            """
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            return []
    
    @staticmethod
    def get_grade_by_id(grade_id):
        """Get grade by ID"""
        try:
            query = f"""
                SELECT grades_id, enrollment_id, grade_type, grade_value, grade_date
                FROM grades
                WHERE grades_id = {grade_id}
            """
            result = DatabaseConnection.execute_query(query)
            return result[0] if result else None
        except Exception as e:
            return None
    
    @staticmethod
    def get_enrollment_grades(enrollment_id):
        """Get all grades for an enrollment"""
        try:
            query = f"""
                SELECT grades_id, grade_type, grade_value, grade_date
                FROM grades
                WHERE enrollment_id = {enrollment_id}
                ORDER BY grade_date DESC
            """
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            return None
    
    @staticmethod
    def get_student_transcript(student_id):
        """Get student transcript (all grades from all courses)"""
        try:
            query = f"""
                SELECT * FROM vw_student_transcripts
                WHERE student_id = {student_id}
                ORDER BY academic_year DESC
            """
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            return None


class AttendanceOperations:
    """Attendance management operations"""
    
    @staticmethod
    def mark_attendance(enrollment_id, status):
        """Mark attendance"""
        try:
            query = f"""
                INSERT INTO attendance (enrollment_id, attendance_date, status)
                VALUES ({enrollment_id}, CURRENT_DATE, '{status}')
                RETURNING attendance_id;
            """
            result = DatabaseConnection.execute_query(query)
            if result:
                return True, f"Attendance marked as '{status}'"
            return False, "Failed to mark attendance"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def get_all_attendance():
        """Get all attendance records (newest first)"""
        try:
            query = """
                SELECT attendance_id, enrollment_id, attendance_date, status
                FROM attendance
                ORDER BY attendance_id DESC
            """
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            return []
    
    @staticmethod
    def get_enrollment_attendance(enrollment_id):
        """Get attendance records for an enrollment"""
        try:
            query = f"""
                SELECT attendance_id, attendance_date, status
                FROM attendance
                WHERE enrollment_id = {enrollment_id}
                ORDER BY attendance_date DESC
            """
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            return None


class ReportOperations:
    """Report and statistics operations"""
    
    @staticmethod
    def get_course_grade_statistics():
        """Get grade statistics for all courses"""
        try:
            query = """SELECT * FROM get_course_grade_statistics()"""
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            return None
    
    @staticmethod
    def get_low_attendance_students():
        """Get students with <75% attendance"""
        try:
            query = """SELECT * FROM get_low_attendance_students()"""
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            return None
    
    @staticmethod
    def get_top_students_by_gpa(limit=10):
        """Get top students by GPA"""
        try:
            query = f"""SELECT * FROM get_top_students_by_gpa({limit})"""
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            return None
    
    @staticmethod
    def get_enrollment_statistics():
        """Get enrollment statistics for all courses"""
        try:
            query = """SELECT * FROM get_enrollment_statistics()"""
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            return None


# ========================================================================
# REPORT GENERATOR MODULE
# ========================================================================

class ReportGenerator:
    """Generate reports in CSV and PDF formats with audit compliance"""
    
    OUTPUT_DIR = "../reports"
    
    @classmethod
    def ensure_output_dir(cls):
        """Create output directory if it doesn't exist"""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
    
    @classmethod
    def generate_document_id(cls):
        """Generate unique audit-compliant document ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique = str(uuid.uuid4())[:8].upper()
        return f"DOC-{timestamp}-{unique}"
    
    @classmethod
    def generate_verification_code(cls, student_id, student_num, timestamp):
        """Generate tamper-evident verification code"""
        data = f"{student_id}{student_num}{timestamp}OFFICIAL".encode()
        return hashlib.sha256(data).hexdigest()[:16].upper()
    
    @classmethod
    def get_validity_period(cls):
        """Return report validity dates"""
        issued = datetime.now()
        expires = issued + timedelta(days=365)
        return issued, expires
    
    @classmethod
    def convert_to_4point0_scale(cls, percentage_grade):
        """
        Convert percentage grade (0-100) to 4.0 GPA scale
        A: 90-100 → 4.0
        B: 80-89 → 3.0
        C: 70-79 → 2.0
        D: 60-69 → 1.0
        F: 0-59 → 0.0
        """
        if percentage_grade is None:
            return 0.0
        
        grade = float(percentage_grade)
        if grade >= 90:
            return 4.0
        elif grade >= 80:
            return 3.0
        elif grade >= 70:
            return 2.0
        elif grade >= 60:
            return 1.0
        else:
            return 0.0
    
    @classmethod
    def determine_course_status(cls, gpa):
        """
        Determine course status based on GPA:
        - PASS: 50%+ (≥50)
        - QUALIFY FOR REASSESSMENT: 40-49% (40-49)
        - FAIL: ≤39%
        """
        if gpa is None:
            return "PENDING"
        
        grade = float(gpa)
        if grade >= 50:
            return "PASS"
        elif grade >= 40:
            return "QUALIFY FOR REASSESSMENT"
        else:
            return "FAIL"
    
    @classmethod
    def generate_student_transcript_csv(cls, student_id):
        """Generate student transcript as CSV"""
        try:
            cls.ensure_output_dir()
            
            # Get student info
            student = StudentOperations.get_student_by_id(student_id)
            if not student:
                return False, "Student not found"
            
            student_id, student_num, first_name, last_name, dob, email, status = student
            
            # Get transcript
            transcript = GradeOperations.get_student_transcript(student_id)
            if not transcript:
                return False, "No transcript data found"
            
            # Create filename
            filename = f"transcript_{student_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(cls.OUTPUT_DIR, filename)
            
            # Write CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header with student info
                writer.writerow(['STUDENT TRANSCRIPT'])
                writer.writerow([])
                writer.writerow(['Student Number:', student_num])
                writer.writerow(['Name:', f"{first_name} {last_name}"])
                writer.writerow(['Email:', email])
                writer.writerow(['Status:', status])
                writer.writerow([])
                
                # Transcript data
                writer.writerow(['Student ID', 'Student Number', 'First Name', 'Last Name', 
                                'Course Code', 'Course Name', 'Academic Year', 'Term', 'Average Grade'])
                
                for row in transcript:
                    writer.writerow(row)
            
            return True, f"Transcript saved to {filepath}"
        
        except Exception as e:
            return False, f"Error generating transcript: {str(e)}"
    
    @classmethod
    def generate_course_statistics_csv(cls):
        """Generate course grade statistics as CSV"""
        try:
            cls.ensure_output_dir()
            
            stats = ReportOperations.get_course_grade_statistics()
            if not stats:
                return False, "No statistics data found"
            
            filename = f"course_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(cls.OUTPUT_DIR, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                writer.writerow(['COURSE GRADE STATISTICS'])
                writer.writerow([])
                writer.writerow(['Course Code', 'Course Name', 'Total Students', 'Total Grades',
                                'Average Grade', 'Highest Grade', 'Lowest Grade'])
                
                for row in stats:
                    writer.writerow(row)
            
            return True, f"Statistics saved to {filepath}"
        
        except Exception as e:
            return False, f"Error generating statistics: {str(e)}"
    
    @classmethod
    def generate_enrollment_statistics_csv(cls):
        """Generate enrollment statistics as CSV"""
        try:
            cls.ensure_output_dir()
            
            stats = ReportOperations.get_enrollment_statistics()
            if not stats:
                return False, "No enrollment data found"
            
            filename = f"enrollment_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(cls.OUTPUT_DIR, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                writer.writerow(['ENROLLMENT STATISTICS'])
                writer.writerow([])
                writer.writerow(['Course Code', 'Course Name', 'Total Enrollments',
                                'Unique Students', 'Students with Grades'])
                
                for row in stats:
                    writer.writerow(row)
            
            return True, f"Enrollment statistics saved to {filepath}"
        
        except Exception as e:
            return False, f"Error generating enrollment statistics: {str(e)}"
    
    @classmethod
    def generate_low_attendance_csv(cls):
        """Generate low attendance report as CSV"""
        try:
            cls.ensure_output_dir()
            
            students = ReportOperations.get_low_attendance_students()
            if not students:
                return True, "No students with low attendance"
            
            filename = f"low_attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(cls.OUTPUT_DIR, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                writer.writerow(['LOW ATTENDANCE STUDENTS (<75%)'])
                writer.writerow([])
                writer.writerow(['Student Number', 'First Name', 'Last Name', 'Course Code',
                                'Total Classes', 'Classes Attended', 'Attendance Percentage'])
                
                for row in students:
                    writer.writerow(row)
            
            return True, f"Low attendance report saved to {filepath}"
        
        except Exception as e:
            return False, f"Error generating low attendance report: {str(e)}"
    
    @classmethod
    def generate_top_students_csv(cls, limit=10):
        """Generate top students by GPA report as CSV"""
        try:
            cls.ensure_output_dir()
            
            students = ReportOperations.get_top_students_by_gpa(limit)
            if not students:
                return False, "No student data found"
            
            filename = f"top_students_{limit}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = os.path.join(cls.OUTPUT_DIR, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                writer.writerow([f'TOP {limit} STUDENTS BY GPA'])
                writer.writerow([])
                writer.writerow(['Rank', 'Student Number', 'First Name', 'Last Name', 'GPA', 'Total Grades'])
                
                for row in students:
                    writer.writerow(row)
            
            return True, f"Top students report saved to {filepath}"
        
        except Exception as e:
            return False, f"Error generating top students report: {str(e)}"
    
    @classmethod
    def generate_student_transcript_pdf(cls, student_id):
        """Generate audit-compliant student transcript PDF for official academic records"""
        if not REPORTLAB_AVAILABLE:
            return False, "ReportLab not installed. Install with: pip install reportlab"
        
        try:
            cls.ensure_output_dir()
            
            # Get student info
            student = StudentOperations.get_student_by_id(student_id)
            if not student:
                return False, "Student not found"
            
            student_id, student_num, first_name, last_name, dob, email, status = student
            
            # Get transcript from database view
            query = f"SELECT * FROM vw_student_transcripts WHERE student_id = {student_id};"
            transcript = DatabaseConnection.execute_query(query)
            
            if not transcript:
                return False, "No transcript data found"
            
            # Generate audit compliance identifiers
            document_id = cls.generate_document_id()
            issued_date, expires_date = cls.get_validity_period()
            verification_code = cls.generate_verification_code(student_id, student_num, issued_date.strftime('%Y%m%d'))
            
            # Create PDF filename with document ID
            filename = f"transcript_{student_num}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join(cls.OUTPUT_DIR, filename)
            
            # Create PDF with audit-compliant margins
            doc = SimpleDocTemplate(filepath, pagesize=letter, 
                                   leftMargin=0.75*inch, rightMargin=0.75*inch,
                                   topMargin=0.5*inch, bottomMargin=1*inch)
            story = []
            styles = getSampleStyleSheet()
            
            # ========== OFFICIAL INSTITUTION HEADER ==========
            header_style = ParagraphStyle(
                'HeaderStyle',
                parent=styles['Normal'],
                fontSize=11,
                textColor=colors.HexColor('#1f4788'),
                alignment=1,
                spaceAfter=2,
                fontName='Helvetica-Bold'
            )
            subheader_style = ParagraphStyle(
                'SubHeaderStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#666666'),
                alignment=1,
                spaceAfter=1
            )
            
            story.append(Paragraph(INSTITUTION_INFO['name'], header_style))
            story.append(Paragraph(INSTITUTION_INFO['address'], subheader_style))
            story.append(Paragraph(f"Phone: {INSTITUTION_INFO['phone']} | Email: {INSTITUTION_INFO['email']}", subheader_style))
            story.append(Paragraph(f"Accreditation: {INSTITUTION_INFO['accreditation']}", subheader_style))
            story.append(Spacer(1, 0.2*inch))
            
            # ========== OFFICIAL TITLE ==========
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=26,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=12,
                alignment=1,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph('OFFICIAL ACADEMIC TRANSCRIPT', title_style))
            
            # ========== AUDIT COMPLIANCE SECTION ==========
            compliance_style = ParagraphStyle(
                'ComplianceStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#CC0000'),
                alignment=1,
                spaceAfter=6
            )
            story.append(Paragraph("This is an official academic record. Unauthorized reproduction or alteration is prohibited.", compliance_style))
            
            # ========== DOCUMENT IDENTIFIERS (Audit Trail) ==========
            audit_data = [
                ['Document ID:', document_id, 'Issued:', issued_date.strftime('%B %d, %Y')],
                ['Verification Code:', verification_code, 'Valid Until:', expires_date.strftime('%B %d, %Y')]
            ]
            
            audit_table = Table(audit_data, colWidths=[1.3*inch, 1.7*inch, 1.3*inch, 1.7*inch])
            audit_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f0f0')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (2, 0), (2, -1), colors.HexColor('#1f4788')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Courier'),
                ('FONTNAME', (3, 0), (3, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc'))
            ]))
            
            story.append(audit_table)
            story.append(Spacer(1, 0.2*inch))
            
            # ========== STUDENT INFORMATION SECTION ==========
            student_info_data = [
                ['Student Number:', str(student_num), 'Legal Name:', f"{first_name} {last_name}"],
                ['Date of Birth:', str(dob), 'Enrollment Status:', status.upper()],
                ['Email Address:', email, 'Record Last Updated:', datetime.now().strftime('%Y-%m-%d')]
            ]
            
            student_info_table = Table(student_info_data, colWidths=[1.2*inch, 1.8*inch, 1.2*inch, 1.8*inch])
            student_info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTNAME', (3, 0), (3, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f9f9f9')])
            ]))
            
            story.append(student_info_table)
            story.append(Spacer(1, 0.2*inch))
            
            # ========== ACADEMIC RECORD HEADER ==========
            record_header = ParagraphStyle(
                'RecordHeader',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=10,
                fontName='Helvetica-Bold',
                borderPadding=5
            )
            story.append(Paragraph('ACADEMIC RECORD - OFFICIAL COURSES AND GRADES', record_header))
            
            # ========== TRANSCRIPT TABLE ==========
            table_data = [['Course Code', 'Course Name', 'Academic Year', 'Term', 'Grade', 'Status']]
            
            for row in transcript:
                course_code = row[4]
                course_name = row[5][:28]
                academic_year = row[6]
                term = f"Term {row[7]}"
                avg_grade = f"{float(row[8]):.2f}" if row[8] else 'N/A'
                status_val = cls.determine_course_status(row[8])
                
                table_data.append([course_code, course_name, academic_year, term, avg_grade, status_val])
            
            table = Table(table_data, colWidths=[1*inch, 2.1*inch, 1*inch, 0.75*inch, 0.9*inch, 0.9*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('ALIGNMENT', (0, 0), (-1, 0), 'CENTER'),
                ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fafafa')),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#333333')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGNMENT', (0, 1), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1.2, colors.HexColor('#1f4788')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f0f7ff')])
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.3*inch))
            
            # ========== OFFICIAL CERTIFICATION & FOOTER ==========
            certification_style = ParagraphStyle(
                'CertificationStyle',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#1f4788'),
                fontName='Helvetica-Bold',
                spaceAfter=4,
                alignment=0
            )
            
            normal_style = ParagraphStyle(
                'NormalStyle',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#333333'),
                alignment=0,
                spaceAfter=2
            )
            
            story.append(Paragraph('CERTIFICATION:', certification_style))
            story.append(Paragraph('This official academic transcript is a complete and accurate record of the academic progress and achievements of the named student. This document is prepared in accordance with institutional policies and federal regulations governing educational records.', normal_style))
            story.append(Spacer(1, 0.15*inch))
            
            story.append(Paragraph('CONFIDENTIALITY NOTICE:', certification_style))
            story.append(Paragraph('This document contains confidential educational records protected under FERPA (Family Educational Rights and Privacy Act). Unauthorized access, use, or distribution is prohibited by federal law.', normal_style))
            story.append(Spacer(1, 0.2*inch))
            
            # ========== OFFICIAL FOOTER ==========
            footer_style = ParagraphStyle(
                'FooterStyle',
                parent=styles['Normal'],
                fontSize=7,
                textColor=colors.HexColor('#999999'),
                alignment=1,
                spaceAfter=1
            )
            
            story.append(Paragraph("═" * 80, footer_style))
            story.append(Paragraph(f"Verification Code: {verification_code}", footer_style))
            story.append(Paragraph(f"Generated: {issued_date.strftime('%B %d, %Y at %H:%M:%S')} | Valid Until: {expires_date.strftime('%B %d, %Y')}", footer_style))
            story.append(Paragraph(f"Contact: {INSTITUTION_INFO['email']} | {INSTITUTION_INFO['phone']}", footer_style))
            story.append(Paragraph("═" * 80, footer_style))
            
            # Build PDF
            doc.build(story)
            
            return True, f"Official transcript PDF saved to {filepath}"
        
        except Exception as e:
            return False, f"Error generating PDF: {str(e)}"


class PaginationManager:
    """Handle pagination for large datasets with enhanced feedback"""
    
    def __init__(self, items, page_size=5):
        self.items = items if items else []
        self.page_size = max(1, page_size)  # Ensure page_size is at least 1
        self.current_page = 0
        self.total_pages = (len(self.items) + self.page_size - 1) // self.page_size if self.items else 1
    
    def get_current_page(self):
        """Get current page items"""
        if not self.items:
            return []
        start = self.current_page * self.page_size
        end = start + self.page_size
        return self.items[start:end]
    
    def has_next(self):
        """Check if next page exists"""
        return self.current_page < self.total_pages - 1 if self.total_pages > 0 else False
    
    def has_prev(self):
        """Check if previous page exists"""
        return self.current_page > 0
    
    def next_page(self):
        """Go to next page"""
        if self.has_next():
            self.current_page += 1
            return True
        return False
    
    def prev_page(self):
        """Go to previous page"""
        if self.has_prev():
            self.current_page -= 1
            return True
        return False
    
    def jump_to_page(self, page_number):
        """Jump to specific page (1-indexed)"""
        if 1 <= page_number <= self.total_pages:
            self.current_page = page_number - 1
            return True
        return False
    
    def get_page_info(self):
        """Get detailed page information"""
        if not self.items:
            return "No items available"
        
        current_items_start = self.current_page * self.page_size + 1
        current_items_end = min((self.current_page + 1) * self.page_size, len(self.items))
        
        return (f"Page {self.current_page + 1}/{self.total_pages} | "
                f"Showing items {current_items_start}-{current_items_end} of {len(self.items)}")


class StudentRecordsApp:
    """Enhanced CLI application with CRUD, Search, Pagination"""
    
    def __init__(self):
        """Initialize application"""
        self.running = True
        self.validate_database_connection()
    
    def validate_database_connection(self):
        """Check database connection on startup"""
        if not DatabaseConnection.test_connection():
            print("\n❌ ERROR: Cannot connect to PostgreSQL database")
            print("   Make sure PostgreSQL is running and student_records_db exists")
            sys.exit(1)
        print("\n✅ Database connection successful\n")
    
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f"  {title}".center(70))
        print("="*70 + "\n")
    
    def print_menu(self, title, options):
        """Print formatted menu"""
        self.print_header(title)
        for key, label in options.items():
            print(f"  {key}. {label}")
        print("\n  0. Back to Main Menu")
        print("\n" + "="*70)
    
    def get_input(self, prompt, input_type=str, allow_empty=False, min_val=None, max_val=None):
        """Get validated user input with enhanced error handling"""
        while True:
            try:
                value = input(prompt).strip()
                
                # Check empty input
                if not value:
                    if allow_empty:
                        return value if input_type == str else None
                    print("  ❌ Input cannot be empty. Please try again.")
                    continue
                
                # Handle different input types
                if input_type == int:
                    try:
                        num = int(value)
                        if min_val is not None and num < min_val:
                            print(f"  ❌ Value must be at least {min_val}")
                            continue
                        if max_val is not None and num > max_val:
                            print(f"  ❌ Value must be at most {max_val}")
                            continue
                        return num
                    except ValueError:
                        print("  ❌ Invalid input. Please enter a valid integer.")
                        continue
                
                elif input_type == float:
                    try:
                        num = float(value)
                        if min_val is not None and num < min_val:
                            print(f"  ❌ Value must be at least {min_val}")
                            continue
                        if max_val is not None and num > max_val:
                            print(f"  ❌ Value must be at most {max_val}")
                            continue
                        return num
                    except ValueError:
                        print("  ❌ Invalid input. Please enter a valid decimal number.")
                        continue
                
                # Return string (already stripped)
                return value
                
            except KeyboardInterrupt:
                print("\n\n  ⚠️  Operation cancelled by user")
                return None
            except Exception as e:
                pass
                print(f"  ❌ An unexpected error occurred: {str(e)}")
                continue
    
    def confirm(self, prompt):
        """Get yes/no confirmation"""
        while True:
            response = input(f"\n{prompt} (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            print("❌ Please enter 'yes' or 'no'")
    
    def print_table(self, headers, rows, max_width=70):
        """Print formatted table"""
        if not rows:
            print("  No data to display\n")
            return
        
        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Print header
        header_row = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
        print("  " + header_row)
        print("  " + "-" * (len(header_row)))
        
        # Print rows
        for row in rows:
            data_row = " | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
            print("  " + data_row)
        print()
    
    # ========================================================================
    # STUDENT MANAGEMENT
    # ========================================================================
    
    def student_menu(self):
        """Student management menu"""
        while True:
            options = {
                '1': 'Add New Student',
                '2': 'Search Students',
                '3': 'View All Students (Paginated)',
                '4': 'View Student Details',
                '5': 'Update Student Status',
                '6': 'Delete Student',
                '7': 'Sort Students By'
            }
            self.print_menu("STUDENT MANAGEMENT", options)
            
            choice = input("  Select option: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.add_student()
            elif choice == '2':
                self.search_students()
            elif choice == '3':
                self.view_all_students_paginated()
            elif choice == '4':
                self.view_student_details()
            elif choice == '5':
                self.update_student_status()
            elif choice == '6':
                self.delete_student()
            elif choice == '7':
                self.sort_students()
            else:
                print("❌ Invalid option")
            
            input("\nPress Enter to continue...")
    
    def add_student(self):
        """Add new student with comprehensive validation and logging"""
        self.print_header("ADD NEW STUDENT")
        
        try:
            # Get and validate student number
            while True:
                student_number = self.get_input("  Student Number (YYYYRR): ", int)
                if student_number is None:
                    return
                valid, msg = Validators.validate_student_number(student_number)
                if valid:
                    break
                print(f"  ❌ {msg}. Please try again.")
            
            # Get and validate first name
            while True:
                first_name = self.get_input("  First Name: ")
                if first_name is None:
                    return
                valid, msg = Validators.validate_name(first_name)
                if valid:
                    break
                print(f"  ❌ {msg}. Please try again.")
            
            # Get and validate last name
            while True:
                last_name = self.get_input("  Last Name: ")
                if last_name is None:
                    return
                valid, msg = Validators.validate_name(last_name)
                if valid:
                    break
                print(f"  ❌ {msg}. Please try again.")
            
            # Get and validate date of birth
            while True:
                dob = self.get_input("  Date of Birth (YYYY-MM-DD): ")
                if dob is None:
                    return
                valid, msg = Validators.validate_date_of_birth(dob)
                if valid:
                    break
                print(f"  ❌ {msg}. Please try again.")
            
            # Get and validate email
            while True:
                email = self.get_input("  Email: ")
                if email is None:
                    return
                valid, msg = Validators.validate_email(email)
                if valid:
                    break
                print(f"  ❌ {msg}. Please try again.")
            
            # Add student
            result = StudentOperations.add_student(
                student_number, first_name, last_name, dob, email
            )
            
            # Handle both old (2-tuple) and new (3-tuple) return formats
            if len(result) == 3:
                success, message, student_id = result
                print(f"\n{'✅' if success else '❌'} {message}")
                if success:
                    pass
            else:
                success, message = result
                print(f"\n{'✅' if success else '❌'} {message}")
                if success:
                    pass
        
        except Exception as e:
            pass
            print(f"\n  ❌ An unexpected error occurred: {str(e)}")
    
    
    def search_students(self):
        """Search students by name or number (case-insensitive, partial match)"""
        self.print_header("SEARCH STUDENTS")
        
        try:
            search_term = self.get_input("  Search (name or student number): ")
            if search_term is None:
                return
            
            if not search_term.strip():
                print("  ❌ Search term cannot be empty\n")
                return
            
            all_students = StudentOperations.get_all_students()
            if not all_students:
                print("  ❌ No students found in database\n")
                return
            
            # Case-insensitive partial match search
            search_lower = search_term.lower()
            students = []
            
            for student in all_students:
                # Search by ID, student number, or name (case-insensitive, partial match)
                student_id, student_num, first_name, last_name, dob, email, status = student
                
                if (str(student_id).startswith(search_lower) or
                    str(student_num).startswith(search_lower) or
                    first_name.lower().startswith(search_lower) or
                    last_name.lower().startswith(search_lower) or
                    f"{first_name} {last_name}".lower().find(search_lower) != -1):
                    students.append(student)
            
            if students:
                headers = ["ID", "Num", "First Name", "Last Name", "DOB", "Email", "Status"]
                print(f"  Found {len(students)} student(s):\n")
                self.print_table(headers, students)
                pass
            else:
                print(f"  ❌ No students found matching '{search_term}'\n")
                pass
        
        except Exception as e:
            pass
            print(f"  ❌ Error during search: {str(e)}\n")
    
    def view_all_students_paginated(self):
        """View students with pagination and comprehensive navigation"""
        self.print_header("VIEW ALL STUDENTS (PAGINATED - NEWEST FIRST)")
        
        try:
            students = StudentOperations.get_all_students()
            if not students:
                print("  ℹ️  No students found in database\n")
                return
            
            paginator = PaginationManager(students, page_size=5)
            
            while True:
                try:
                    print(f"  📄 {paginator.get_page_info()}\n")
                    
                    headers = ["ID", "Num", "First Name", "Last Name", "DOB", "Email", "Status"]
                    current = paginator.get_current_page()
                    self.print_table(headers, current)
                    
                    # Build navigation options
                    nav_options = []
                    if paginator.has_prev():
                        nav_options.append("p=Previous")
                    if paginator.has_next():
                        nav_options.append("n=Next")
                    nav_options.append("q=Quit")
                    
                    print("  Navigation: " + " | ".join(nav_options))
                    choice = input("  Enter choice: ").strip().lower()
                    
                    if choice == 'n':
                        if paginator.has_next():
                            paginator.next_page()
                            print()
                        else:
                            print("  ⚠️  Already on last page\n")
                    elif choice == 'p':
                        if paginator.has_prev():
                            paginator.prev_page()
                            print()
                        else:
                            print("  ⚠️  Already on first page\n")
                    elif choice == 'q':
                        break
                    else:
                        print("  ❌ Invalid option. Please use p, n, or q\n")
                
                except KeyboardInterrupt:
                    print("\n\n  ⚠️  Navigation cancelled\n")
                    break
                except Exception as e:
                    pass
                    print(f"  ❌ Error: {str(e)}\n")
                    break
        
        except Exception as e:
            pass
            print(f"  ❌ Error retrieving students: {str(e)}\n")
    
    def view_student_details(self):
        """View detailed student information with error handling"""
        self.print_header("VIEW STUDENT DETAILS")
        
        try:
            student_id = self.get_input("  Enter Student ID: ", int, min_val=1)
            if student_id is None:
                return
            
            student = StudentOperations.get_student_by_id(student_id)
            
            if not student:
                print(f"  ❌ Student with ID {student_id} not found\n")
                pass
                return
            
            print("\n  " + "="*64)
            print(f"  Student ID:         {student[0]}")
            print(f"  Student Number:     {student[1]}")
            print(f"  Full Name:          {student[2]} {student[3]}")
            print(f"  Date of Birth:      {student[4]}")
            print(f"  Email:              {student[5]}")
            print(f"  Status:             {student[6]}")
            print("  " + "="*64 + "\n")
            pass
        
        except Exception as e:
            pass
            print(f"  ❌ Error retrieving student details: {str(e)}\n")
    
    def update_student_status(self):
        """Update student status"""
        self.print_header("UPDATE STUDENT STATUS")
        
        student_id = self.get_input("  Student ID: ", int)
        student = StudentOperations.get_student_by_id(student_id)
        
        if not student:
            print("  ❌ Student not found\n")
            return
        
        print(f"\n  Current Status: {student[6]}")
        print("  New Status Options: active, inactive, graduated")
        status = self.get_input("  New Status: ").lower()
        
        if status not in ['active', 'inactive', 'graduated']:
            print("  ❌ Invalid status\n")
            return
        
        success, message = StudentOperations.update_student_status(student_id, status)
        print(f"  {'✅' if success else '❌'} {message}\n")
    
    def delete_student(self):
        """Delete a student (soft delete via status)"""
        self.print_header("DELETE STUDENT")
        
        student_id = self.get_input("  Student ID: ", int)
        student = StudentOperations.get_student_by_id(student_id)
        
        if not student:
            print("  ❌ Student not found\n")
            return
        
        print(f"\n  Student: {student[2]} {student[3]} (ID: {student[0]})")
        print("  ⚠️  WARNING: This action will mark the student as deleted")
        
        if self.confirm("  Are you absolutely sure you want to delete this student?"):
            try:
                query = f"""
                    UPDATE students
                    SET status = 'inactive'
                    WHERE student_id = {student_id}
                """
                DatabaseConnection.execute_procedure(query)
                print("\n  ✅ Student marked as deleted (status set to inactive)\n")
            except Exception as e:
                print(f"\n  ❌ Error: {e}\n")
        else:
            print("\n  ❌ Deletion cancelled\n")
    
    def sort_students(self):
        """Sort students by different criteria"""
        self.print_header("SORT STUDENTS")
        
        print("  Sort by:")
        print("  1. Student Number (Ascending)")
        print("  2. Student Number (Descending)")
        print("  3. First Name (A-Z)")
        print("  4. Last Name (A-Z)")
        
        choice = self.get_input("\n  Select sort option: ")
        
        students = StudentOperations.get_all_students()
        if not students:
            print("  No students found\n")
            return
        
        if choice == '1':
            students.sort(key=lambda x: x[1])
            title = "Students Sorted by Number (Ascending)"
        elif choice == '2':
            students.sort(key=lambda x: x[1], reverse=True)
            title = "Students Sorted by Number (Descending)"
        elif choice == '3':
            students.sort(key=lambda x: x[2])
            title = "Students Sorted by First Name"
        elif choice == '4':
            students.sort(key=lambda x: x[3])
            title = "Students Sorted by Last Name"
        else:
            print("  ❌ Invalid option\n")
            return
        
        print(f"\n  {title}\n")
        headers = ["ID", "Num", "First Name", "Last Name", "DOB", "Email", "Status"]
        self.print_table(headers, students)
    
    # ========================================================================
    # ENROLLMENT MANAGEMENT
    # ========================================================================
    
    def enrollment_menu(self):
        """Enrollment management menu"""
        while True:
            options = {
                '1': 'Add Student to Course',
                '2': 'View All Enrollments (Paginated)',
                '3': 'Search Enrollments',
                '4': 'Delete Enrollment',
                '5': 'View Course Roster'
            }
            self.print_menu("ENROLLMENT MANAGEMENT", options)
            
            choice = input("  Select option: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.add_enrollment()
            elif choice == '2':
                self.view_all_enrollments_paginated()
            elif choice == '3':
                self.search_enrollments()
            elif choice == '4':
                self.delete_enrollment()
            elif choice == '5':
                self.view_course_roster()
            else:
                print("❌ Invalid option")
            
            input("\nPress Enter to continue...")
    
    def add_enrollment(self):
        """Add enrollment with comprehensive validation"""
        self.print_header("ADD ENROLLMENT")
        
        try:
            # Get and validate student ID
            student_id = self.get_input("  Enter Student ID: ", int, min_val=1)
            if student_id is None:
                return
            
            student = StudentOperations.get_student_by_id(student_id)
            if not student:
                print(f"  ❌ Student with ID {student_id} not found\n")
                pass
                return
            print(f"  ✅ Student found: {student[2]} {student[3]}")
            
            # Get and validate course ID
            course_id = self.get_input("  Enter Course ID: ", int, min_val=1)
            if course_id is None:
                return
            
            course = CourseOperations.get_course_by_id(course_id)
            if not course:
                print(f"  ❌ Course with ID {course_id} not found\n")
                pass
                return
            print(f"  ✅ Course found: {course[1]}")
            
            # Get and validate academic year
            while True:
                academic_year = self.get_input("  Academic Year (YYYY-YYYY, e.g., 2024-2025): ")
                if academic_year is None:
                    return
                valid, msg = Validators.validate_academic_year(academic_year)
                if valid:
                    break
                print(f"  ❌ {msg}. Please try again.")
            
            # Get and validate term
            while True:
                term = self.get_input("  Term (1=Fall, 2=Spring): ")
                if term is None:
                    return
                valid, msg = Validators.validate_term(term)
                if valid:
                    break
                print(f"  ❌ {msg}. Please try again.")
            
            # Add enrollment
            success, message = EnrollmentOperations.add_enrollment(
                student_id, course_id, academic_year, term
            )
            print(f"\n  {'✅' if success else '❌'} {message}\n")
            if success:
                pass
        
        except Exception as e:
            pass
            print(f"\n  ❌ Error: {str(e)}\n")
    
    def view_all_enrollments_paginated(self):
        """View enrollments with pagination and navigation (newest first)"""
        self.print_header("VIEW ALL ENROLLMENTS (PAGINATED - NEWEST FIRST)")
        
        try:
            enrollments = EnrollmentOperations.get_all_enrollments()
            if not enrollments:
                print("  ℹ️  No enrollments found in database\n")
                return
            
            paginator = PaginationManager(enrollments, page_size=5)
            
            while True:
                try:
                    print(f"  📄 {paginator.get_page_info()}\n")
                    
                    headers = ["Enroll ID", "Student ID", "Course ID", "Year", "Term", "Date"]
                    current = paginator.get_current_page()
                    self.print_table(headers, current)
                    
                    # Build navigation options
                    nav_options = []
                    if paginator.has_prev():
                        nav_options.append("p=Previous")
                    if paginator.has_next():
                        nav_options.append("n=Next")
                    nav_options.append("q=Quit")
                    
                    print("  Navigation: " + " | ".join(nav_options))
                    choice = input("  Enter choice: ").strip().lower()
                    
                    if choice == 'n':
                        if paginator.has_next():
                            paginator.next_page()
                            print()
                        else:
                            print("  ⚠️  Already on last page\n")
                    elif choice == 'p':
                        if paginator.has_prev():
                            paginator.prev_page()
                            print()
                        else:
                            print("  ⚠️  Already on first page\n")
                    elif choice == 'q':
                        break
                    else:
                        print("  ❌ Invalid option. Please use p, n, or q\n")
                
                except KeyboardInterrupt:
                    print("\n\n  ⚠️  Navigation cancelled\n")
                    break
                except Exception as e:
                    pass
                    print(f"  ❌ Error: {str(e)}\n")
                    break
        
        except Exception as e:
            pass
            print(f"  ❌ Error retrieving enrollments: {str(e)}\n")
    
    def search_enrollments(self):
        """Search enrollments by student or course with error handling"""
        self.print_header("SEARCH ENROLLMENTS")
        
        try:
            print("  Search by:")
            print("  1. Student ID")
            print("  2. Course ID")
            
            search_type = self.get_input("\n  Select (1 or 2): ")
            if search_type is None:
                return
            
            if search_type not in ['1', '2']:
                print("  ❌ Invalid search type. Please select 1 or 2\n")
                return
            
            search_value = self.get_input("  Enter search value: ", int, min_val=1)
            if search_value is None:
                return
            
            enrollments = EnrollmentOperations.get_all_enrollments()
            if not enrollments:
                print("  ℹ️  No enrollments found in database\n")
                return
            
            if search_type == '1':
                results = [e for e in enrollments if e[1] == search_value]
                search_label = f"Student ID {search_value}"
            else:  # search_type == '2'
                results = [e for e in enrollments if e[2] == search_value]
                search_label = f"Course ID {search_value}"
            
            if results:
                headers = ["Enroll ID", "Student ID", "Course ID", "Year", "Term", "Date"]
                print(f"\n  Found {len(results)} enrollment(s) for {search_label}:\n")
                self.print_table(headers, results)
                pass
            else:
                print(f"  ❌ No enrollments found for {search_label}\n")
                pass
        
        except Exception as e:
            pass
            print(f"  ❌ Error during search: {str(e)}\n")
    
    def delete_enrollment(self):
        """Delete enrollment"""
        self.print_header("DELETE ENROLLMENT")
        
        enrollment_id = self.get_input("  Enrollment ID: ", int)
        enrollment = EnrollmentOperations.get_enrollment_by_id(enrollment_id)
        
        if not enrollment:
            print("  ❌ Enrollment not found\n")
            return
        
        print(f"\n  Enrollment: Student {enrollment[1]} in Course {enrollment[2]}")
        
        if self.confirm("  Are you sure you want to delete this enrollment?"):
            try:
                query = f"DELETE FROM enrollments WHERE enrollment_id = {enrollment_id}"
                DatabaseConnection.execute_procedure(query)
                print("\n  ✅ Enrollment deleted\n")
            except Exception as e:
                print(f"\n  ❌ Error: {e}\n")
        else:
            print("\n  ❌ Deletion cancelled\n")
    
    def view_course_roster(self):
        """View course roster from view"""
        self.print_header("VIEW COURSE ROSTER")
        
        try:
            roster = DatabaseConnection.execute_query("SELECT * FROM vw_course_rosters LIMIT 10;")
            if roster:
                headers = ["Course Code", "Course Name", "Student Num", "First Name", "Last Name", 
                          "Year", "Term", "Total Classes", "Attended"]
                self.print_table(headers, roster)
            else:
                print("  No roster data found\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    # ========================================================================
    # GRADES & ATTENDANCE
    # ========================================================================
    
    def grades_attendance_menu(self):
        """Grades and attendance menu"""
        while True:
            options = {
                '1': 'Add Grade',
                '2': 'View Grades (Paginated)',
                '3': 'Search Grades',
                '4': 'Delete Grade',
                '5': 'Mark Attendance',
                '6': 'View All Attendance (Paginated)',
                '7': 'View Attendance Report'
            }
            self.print_menu("GRADES & ATTENDANCE", options)
            
            choice = input("  Select option: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.add_grade()
            elif choice == '2':
                self.view_grades_paginated()
            elif choice == '3':
                self.search_grades()
            elif choice == '4':
                self.delete_grade()
            elif choice == '5':
                self.mark_attendance()
            elif choice == '6':
                self.view_all_attendance_paginated()
            elif choice == '7':
                self.view_attendance_report()
            else:
                print("❌ Invalid option")
            
            input("\nPress Enter to continue...")
    
    def add_grade(self):
        """Add grade"""
        self.print_header("ADD GRADE")
        
        enrollment_id = self.get_input("  Enrollment ID: ", int)
        if not EnrollmentOperations.get_enrollment_by_id(enrollment_id):
            print("  ❌ Enrollment not found\n")
            return
        
        print("  Grade Type: test, assignment, exam")
        grade_type = self.get_input("  Grade Type: ").lower()
        grade_value = self.get_input("  Grade Value (0-100): ", int)
        
        if not Validators.validate_grade(grade_value):
            print("  ❌ Grade must be between 0 and 100\n")
            return
        
        success, message = GradeOperations.add_grade(
            enrollment_id, grade_type, grade_value
        )
        print(f"  {'✅' if success else '❌'} {message}\n")
    
    def view_grades_paginated(self):
        """View grades with pagination"""
        self.print_header("VIEW ALL GRADES (PAGINATED)")
        
        grades = GradeOperations.get_all_grades()
        if not grades:
            print("  No grades found\n")
            return
        
        paginator = PaginationManager(grades, page_size=5)
        
        while True:
            print(f"  {paginator.get_page_info()}\n")
            
            headers = ["Grade ID", "Enroll ID", "Type", "Value", "Date"]
            current = paginator.get_current_page()
            self.print_table(headers, current)
            
            nav_options = []
            if paginator.has_prev():
                nav_options.append("p=Previous")
            if paginator.has_next():
                nav_options.append("n=Next")
            nav_options.append("q=Quit")
            
            print("  Navigation: " + " | ".join(nav_options))
            choice = input("  Select: ").strip().lower()
            
            if choice == 'n' and paginator.has_next():
                paginator.next_page()
            elif choice == 'p' and paginator.has_prev():
                paginator.prev_page()
            elif choice == 'q':
                break
            else:
                print("  ❌ Invalid option")
            
            print()
    
    def search_grades(self):
        """Search grades"""
        self.print_header("SEARCH GRADES")
        
        enrollment_id = self.get_input("  Enrollment ID: ", int)
        grades = [g for g in GradeOperations.get_all_grades() if g[1] == enrollment_id]
        
        if grades:
            headers = ["Grade ID", "Enroll ID", "Type", "Value", "Date"]
            self.print_table(headers, grades)
        else:
            print("  ❌ No grades found\n")
    
    def delete_grade(self):
        """Delete grade"""
        self.print_header("DELETE GRADE")
        
        grade_id = self.get_input("  Grade ID: ", int)
        grade = GradeOperations.get_grade_by_id(grade_id)
        
        if not grade:
            print("  ❌ Grade not found\n")
            return
        
        print(f"\n  Grade: Type '{grade[2]}' with value {grade[3]}")
        
        if self.confirm("  Are you sure you want to delete this grade?"):
            try:
                query = f"DELETE FROM grades WHERE grades_id = {grade_id}"
                DatabaseConnection.execute_procedure(query)
                print("\n  ✅ Grade deleted\n")
            except Exception as e:
                print(f"\n  ❌ Error: {e}\n")
        else:
            print("\n  ❌ Deletion cancelled\n")
    
    def mark_attendance(self):
        """Mark attendance"""
        self.print_header("MARK ATTENDANCE")
        
        enrollment_id = self.get_input("  Enrollment ID: ", int)
        if not EnrollmentOperations.get_enrollment_by_id(enrollment_id):
            print("  ❌ Enrollment not found\n")
            return
        
        print("  Status: present, absent, late")
        status = self.get_input("  Attendance Status: ").lower()
        
        success, message = AttendanceOperations.mark_attendance(
            enrollment_id, status
        )
        print(f"  {'✅' if success else '❌'} {message}\n")
    
    def view_all_attendance_paginated(self):
        """View all attendance records with pagination (newest first)"""
        self.print_header("VIEW ALL ATTENDANCE RECORDS (PAGINATED)")
        
        attendance_records = AttendanceOperations.get_all_attendance()
        if not attendance_records:
            print("  No attendance records found\n")
            return
        
        paginator = PaginationManager(attendance_records, page_size=5)
        
        while True:
            print(f"  {paginator.get_page_info()}\n")
            
            headers = ["Attend ID", "Enroll ID", "Date", "Status"]
            current = paginator.get_current_page()
            self.print_table(headers, current)
            
            nav_options = []
            if paginator.has_prev():
                nav_options.append("p=Previous")
            if paginator.has_next():
                nav_options.append("n=Next")
            nav_options.append("q=Quit")
            
            print("  Navigation: " + " | ".join(nav_options))
            choice = input("  Select: ").strip().lower()
            
            if choice == 'n' and paginator.has_next():
                paginator.next_page()
            elif choice == 'p' and paginator.has_prev():
                paginator.prev_page()
            elif choice == 'q':
                break
            else:
                print("  ❌ Invalid option")
            
            print()
    
    def view_attendance_report(self):
        """View attendance report from view"""
        self.print_header("VIEW ATTENDANCE REPORT")
        
        try:
            report = DatabaseConnection.execute_query("SELECT * FROM vw_attendance_reports LIMIT 10;")
            if report:
                headers = ["Student Num", "First Name", "Last Name", "Course Code", "Course Name", 
                          "Year", "Total", "Present", "Absent"]
                self.print_table(headers, report)
            else:
                print("  No attendance data found\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    # ========================================================================
    # REPORTS
    # ========================================================================
    
    def reports_menu(self):
        """Reports menu"""
        while True:
            options = {
                '1': 'Student Transcript (View)',
                '2': 'Course Grade Statistics',
                '3': 'Enrollment Statistics',
                '4': 'Top Students by Weighted GPA',
                '5': 'Student Course Results (Weighted)',
                '6': 'Student GPA Breakdown',
                '7': 'Low Attendance Report',
                '8': 'Export All Reports to CSV',
                '9': 'Student Transcript as PDF ⭐',
                '10': 'Course Statistics as PDF ⭐',
                '11': 'Top Students as PDF ⭐'
            }
            self.print_menu("REPORTS", options)
            
            choice = input("  Select option: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.report_transcript()
            elif choice == '2':
                self.report_course_stats()
            elif choice == '3':
                self.report_enrollment_stats()
            elif choice == '4':
                self.report_top_students_weighted_gpa()
            elif choice == '5':
                self.report_course_results_weighted()
            elif choice == '6':
                self.report_student_gpa_breakdown()
            elif choice == '7':
                self.report_low_attendance()
            elif choice == '8':
                self.export_all_reports()
            elif choice == '9':
                self.export_transcript_pdf()
            elif choice == '10':
                self.export_course_stats_pdf()
            elif choice == '11':
                self.export_top_students_pdf()
            else:
                print("❌ Invalid option")
            
            input("\nPress Enter to continue...")
    
    def report_transcript(self):
        """Student transcript report"""
        self.print_header("STUDENT TRANSCRIPT REPORT")
        
        student_id = self.get_input("  Student ID: ", int)
        
        try:
            query = f"SELECT * FROM vw_student_transcripts WHERE student_id = {student_id};"
            result = DatabaseConnection.execute_query(query)
            
            if result:
                headers = ["Student ID", "Num", "First", "Last", "Course", "Name", "Year", "Term", "Avg Grade"]
                self.print_table(headers, result)
            else:
                print("  ❌ No transcript data found\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    def report_course_stats(self):
        """Course grade statistics"""
        self.print_header("COURSE GRADE STATISTICS")
        
        try:
            # Simplified query since procedures might not be available
            query = """
                SELECT 
                    c.course_code,
                    c.course_name,
                    COUNT(DISTINCT e.student_id) AS total_students,
                    COUNT(g.grades_id) AS total_grades,
                    ROUND(AVG(g.grade_value)::NUMERIC, 2) AS avg_grade
                FROM courses c
                LEFT JOIN enrollments e ON c.course_id = e.course_id
                LEFT JOIN grades g ON e.enrollment_id = g.enrollment_id
                WHERE c.status = 'active'
                GROUP BY c.course_id, c.course_code, c.course_name
                ORDER BY c.course_code;
            """
            result = DatabaseConnection.execute_query(query)
            
            if result:
                headers = ["Code", "Name", "Students", "Grades", "Avg Grade"]
                self.print_table(headers, result)
            else:
                print("  ❌ No data found\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    def report_enrollment_stats(self):
        """Enrollment statistics"""
        self.print_header("ENROLLMENT STATISTICS")
        
        try:
            query = """
                SELECT 
                    c.course_code,
                    c.course_name,
                    COUNT(e.enrollment_id) AS total_enrollments,
                    COUNT(DISTINCT e.student_id) AS unique_students
                FROM courses c
                LEFT JOIN enrollments e ON c.course_id = e.course_id
                WHERE c.status = 'active'
                GROUP BY c.course_id, c.course_code, c.course_name
                ORDER BY c.course_code;
            """
            result = DatabaseConnection.execute_query(query)
            
            if result:
                headers = ["Code", "Name", "Total Enrollments", "Unique Students"]
                self.print_table(headers, result)
            else:
                print("  ❌ No data found\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    def report_top_students_weighted_gpa(self):
        """Top students by weighted GPA"""
        self.print_header("TOP STUDENTS BY WEIGHTED GPA (4.0 SCALE)")
        print("  Weights: Assignment 30% | Test 30% | Exam 40%\n")
        
        try:
            query = """
                SELECT
                    ROW_NUMBER() OVER (ORDER BY gpa DESC) AS rank,
                    student_number,
                    first_name,
                    last_name,
                    gpa
                FROM vw_student_gpa
                ORDER BY gpa DESC
                LIMIT 10;
            """
            result = DatabaseConnection.execute_query(query)
            
            if result:
                headers = ["Rank", "Student #", "First Name", "Last Name", "GPA (4.0)"]
                # Convert GPA values to 4.0 scale
                converted_result = []
                for row in result:
                    converted_row = list(row)
                    converted_row[4] = f"{convert_to_4point0_gpa(row[4]):.2f}"
                    converted_result.append(tuple(converted_row))
                self.print_table(headers, converted_result)
            else:
                print("  ❌ No data found\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    def report_course_results_weighted(self):
        """View course results with weighted averages"""
        self.print_header("STUDENT COURSE RESULTS (WEIGHTED)")
        print("  Weights: Assignment 30% | Test 30% | Exam 40%\n")
        
        try:
            query = """
                SELECT 
                    student_number,
                    first_name,
                    last_name,
                    course_code,
                    course_name,
                    academic_year,
                    term,
                    final_average
                FROM vw_student_course_results
                ORDER BY student_number, course_code;
            """
            result = DatabaseConnection.execute_query(query)
            
            if result:
                headers = ["Num", "First", "Last", "Code", "Course", "Year", "Term", "Final Avg"]
                self.print_table(headers, result)
            else:
                print("  ❌ No data found\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    def report_student_gpa_breakdown(self):
        """View student GPA with course breakdown"""
        self.print_header("STUDENT GPA BREAKDOWN (4.0 SCALE)")
        print("  Weights: Assignment 30% | Test 30% | Exam 40%\n")
        
        student_id = self.get_input("  Enter Student ID: ", int)
        
        try:
            # Get student GPA
            gpa_query = f"SELECT * FROM vw_student_gpa WHERE student_id = {student_id};"
            gpa_result = DatabaseConnection.execute_query(gpa_query)
            
            if gpa_result:
                gpa_4scale = convert_to_4point0_gpa(gpa_result[0][4])
                print(f"\n  Student: {gpa_result[0][1]} ({gpa_result[0][2]} {gpa_result[0][3]})")
                print(f"  Overall GPA (4.0): {gpa_4scale:.2f}\n")
                
                # Get course breakdown
                course_query = f"""
                    SELECT 
                        course_code,
                        course_name,
                        final_average
                    FROM vw_student_course_results
                    WHERE student_id = {student_id}
                    ORDER BY course_code;
                """
                course_result = DatabaseConnection.execute_query(course_query)
                
                if course_result:
                    headers = ["Code", "Course Name", "Final Average"]
                    self.print_table(headers, course_result)
                else:
                    print("  No course data found\n")
            else:
                print("  ❌ Student not found\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    def report_top_students(self):
        """Top students by GPA (Legacy - calls weighted version)"""
        self.report_top_students_weighted_gpa()
    
    def report_low_attendance(self):
        """Low attendance report"""
        self.print_header("LOW ATTENDANCE REPORT (<75%)")
        
        try:
            query = """
                SELECT 
                    s.student_number,
                    s.first_name,
                    s.last_name,
                    c.course_code,
                    COUNT(a.attendance_id) AS total_classes,
                    SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS classes_present,
                    ROUND((SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END)::NUMERIC / 
                           COUNT(a.attendance_id) * 100), 2) AS attendance_pct
                FROM students s
                JOIN enrollments e ON s.student_id = e.student_id
                JOIN courses c ON e.course_id = c.course_id
                LEFT JOIN attendance a ON e.enrollment_id = a.enrollment_id
                WHERE s.status = 'active'
                GROUP BY s.student_id, s.student_number, s.first_name, s.last_name, c.course_code
                HAVING COUNT(a.attendance_id) > 0 AND 
                       (SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END)::NUMERIC / 
                        COUNT(a.attendance_id) * 100) < 75
                ORDER BY attendance_pct ASC;
            """
            result = DatabaseConnection.execute_query(query)
            
            if result:
                headers = ["Num", "First", "Last", "Course", "Total", "Present", "% Attendance"]
                self.print_table(headers, result)
            else:
                print("  No low attendance students found\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    def export_all_reports(self):
        """Export all reports to CSV"""
        self.print_header("EXPORT ALL REPORTS")
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ReportGenerator.generate_all_reports(timestamp)
            print(f"  ✅ Reports exported to reports/ directory\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    def export_transcript_pdf(self):
        """Export student transcript as PDF"""
        self.print_header("EXPORT STUDENT TRANSCRIPT AS PDF")
        
        student_id = self.get_input("  Student ID: ", int)
        
        try:
            success, message = ReportGenerator.generate_student_transcript_pdf(student_id)
            print(f"  {'✅' if success else '❌'} {message}\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    def export_course_stats_pdf(self):
        """Export course statistics as PDF"""
        self.print_header("EXPORT COURSE STATISTICS AS PDF")
        
        try:
            success, message = ReportGenerator.generate_course_statistics_pdf()
            print(f"  {'✅' if success else '❌'} {message}\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    def export_top_students_pdf(self):
        """Export top students as PDF"""
        self.print_header("EXPORT TOP STUDENTS AS PDF")
        
        limit = self.get_input("  Number of top students (default 10): ", int) or 10
        
        try:
            success, message = ReportGenerator.generate_top_students_pdf(limit)
            print(f"  {'✅' if success else '❌'} {message}\n")
        except Exception as e:
            print(f"  ❌ Error: {e}\n")
    
    # ========================================================================
    # MAIN MENU
    # ========================================================================
    
    def main_menu(self):
        """Main menu"""
        while self.running:
            self.print_header("STUDENT RECORDS MANAGEMENT SYSTEM (Enhanced)")
            print("  1. Student Management")
            print("  2. Enrollment Management")
            print("  3. Grades & Attendance")
            print("  4. Reports")
            print("  5. Help")
            print("  0. Exit")
            print("\n" + "="*70)
            
            choice = input("  Select option: ").strip()
            
            if choice == '0':
                print("\n  👋 Thank you for using Student Records System. Goodbye!\n")
                self.running = False
            elif choice == '1':
                self.student_menu()
            elif choice == '2':
                self.enrollment_menu()
            elif choice == '3':
                self.grades_attendance_menu()
            elif choice == '4':
                self.reports_menu()
            elif choice == '5':
                self.show_help()
            else:
                print("  ❌ Invalid option")
            
            input("\nPress Enter to continue...")
    
    def show_help(self):
        """Show help information"""
        self.print_header("HELP & FEATURES")
        
        help_text = """
  🎯 FEATURES:
  
  ✅ STUDENT MANAGEMENT
     • Add, Search, View (paginated), Sort, Update, Delete
     • Search by name or student number
     • Pagination for large datasets
     
  ✅ ENROLLMENT MANAGEMENT
     • Add, View (paginated), Search, Delete enrollments
     • View course rosters from database views
     
  ✅ GRADES & ATTENDANCE
     • Add, View (paginated), Search, Delete grades
     • Mark attendance with status (present/absent/late)
     • View attendance reports with statistics
     • Weighted GPA System: Assignment 30% | Test 30% | Exam 40%
     
  ✅ REPORTS (NEW WEIGHTED GPA FEATURES)
     • Student Transcripts (from vw_student_transcripts view)
     • Course Grade Statistics (aggregated data)
     • Enrollment Statistics
     • ⭐ Top Students by Weighted GPA (ranked by weighted average)
     • ⭐ Student Course Results (showing weighted final average)
     • ⭐ Student GPA Breakdown (per-course breakdown)
     • Low Attendance Report (< 75%)
     • Export all reports to CSV
  
  📊 WEIGHTED GPA CALCULATION
     • Formula: (Assignment × 0.30) + (Test × 0.30) + (Exam × 0.40)
     • Ensures comprehensive assessment of student performance
     • Views: vw_student_gpa, vw_student_course_results
  
  🔒 SAFETY FEATURES
     • Confirmation prompts for all deletions
     • Input validation for all fields
     • Graceful error handling
  
  📄 NAVIGATION
     • Page navigation: [n] Next | [p] Previous | [q] Quit
     • All menus support 0 to go back
     • Press Enter to continue after actions
        """
        print(help_text)


def main():
    """Main entry point"""
    app = StudentRecordsApp()
    app.main_menu()


if __name__ == "__main__":
    main()
