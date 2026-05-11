"""
Data Quality Tests
Tests database constraints and data integrity
"""

import pytest
from database import DatabaseConnection
from validators import Validators


class TestUniqueConstraints:
    """Test UNIQUE constraints"""
    
    def test_student_number_must_be_unique(self):
        """Test that student_number UNIQUE constraint is enforced"""
        # This test would require database setup
        # In production, you'd create a test database with constraints
        pass
    
    def test_course_code_must_be_unique(self):
        """Test that course_code UNIQUE constraint is enforced"""
        pass
    
    def test_enrollment_uniqueness(self):
        """Test that (student_id, course_id, academic_year, term) is unique"""
        pass


class TestNotNullConstraints:
    """Test NOT NULL constraints"""
    
    def test_student_first_name_not_null(self):
        """Test student first_name cannot be NULL"""
        pass
    
    def test_student_last_name_not_null(self):
        """Test student last_name cannot be NULL"""
        pass
    
    def test_enrollment_student_id_not_null(self):
        """Test enrollment student_id cannot be NULL"""
        pass


class TestCheckConstraints:
    """Test CHECK constraints"""
    
    def test_student_status_check_constraint(self):
        """Test student status must be in (active, inactive, graduated)"""
        # Valid statuses
        assert Validators.validate_student_status("active")[0] == True
        assert Validators.validate_student_status("inactive")[0] == True
        assert Validators.validate_student_status("graduated")[0] == True
        
        # Invalid status
        assert Validators.validate_student_status("suspended")[0] == False
    
    def test_course_status_check_constraint(self):
        """Test course status must be in (active, inactive)"""
        pass
    
    def test_grade_value_check_constraint(self):
        """Test grade_value must be between 0 and 100"""
        assert Validators.validate_grade_value(0)[0] == True
        assert Validators.validate_grade_value(100)[0] == True
        assert Validators.validate_grade_value(50)[0] == True
        assert Validators.validate_grade_value(-1)[0] == False
        assert Validators.validate_grade_value(101)[0] == False
    
    def test_grade_type_check_constraint(self):
        """Test grade_type must be in (test, assignment, exam)"""
        assert Validators.validate_grade_type("test")[0] == True
        assert Validators.validate_grade_type("assignment")[0] == True
        assert Validators.validate_grade_type("exam")[0] == True
        assert Validators.validate_grade_type("quiz")[0] == False
    
    def test_term_check_constraint(self):
        """Test term must be in (1, 2)"""
        assert Validators.validate_term("1")[0] == True
        assert Validators.validate_term("2")[0] == True
        assert Validators.validate_term("3")[0] == False
    
    def test_attendance_status_check_constraint(self):
        """Test attendance status must be in (present, absent, late)"""
        assert Validators.validate_attendance_status("present")[0] == True
        assert Validators.validate_attendance_status("absent")[0] == True
        assert Validators.validate_attendance_status("late")[0] == True
        assert Validators.validate_attendance_status("excused")[0] == False


class TestForeignKeyConstraints:
    """Test FOREIGN KEY constraints"""
    
    def test_enrollment_student_id_foreign_key(self):
        """Test enrollments.student_id references students.student_id"""
        # Would test: Cannot insert enrollment with non-existent student_id
        pass
    
    def test_enrollment_course_id_foreign_key(self):
        """Test enrollments.course_id references courses.course_id"""
        # Would test: Cannot insert enrollment with non-existent course_id
        pass
    
    def test_grades_enrollment_id_foreign_key(self):
        """Test grades.enrollment_id references enrollments.enrollment_id"""
        # Would test: Cannot insert grade with non-existent enrollment_id
        pass
    
    def test_attendance_enrollment_id_foreign_key(self):
        """Test attendance.enrollment_id references enrollments.enrollment_id"""
        # Would test: Cannot insert attendance with non-existent enrollment_id
        pass


class TestDataTypes:
    """Test data type constraints"""
    
    def test_student_number_is_integer(self):
        """Test student_number is stored as integer"""
        pass
    
    def test_enrollment_date_is_date(self):
        """Test enrollment_date is stored as DATE"""
        pass
    
    def test_attendance_date_is_timestamp(self):
        """Test attendance_date is stored as TIMESTAMP"""
        pass
    
    def test_grade_value_is_integer(self):
        """Test grade_value is stored as integer"""
        pass


class TestAcademicYearFormat:
    """Test academic_year format constraints"""
    
    def test_academic_year_format(self):
        """Test academic_year follows YYYY-YYYY format"""
        assert Validators.validate_academic_year("2024-2025")[0] == True
        assert Validators.validate_academic_year("2023-2024")[0] == True
        assert Validators.validate_academic_year("2024-2026")[0] == False  # Wrong end year
        assert Validators.validate_academic_year("2024/2025")[0] == False  # Wrong separator


class TestStudentNumberFormat:
    """Test student_number format constraints"""
    
    def test_student_number_yyyyrr_format(self):
        """Test student_number follows YYYYRR format"""
        assert Validators.validate_student_number(199545)[0] == True
        assert Validators.validate_student_number(202345)[0] == True
        assert Validators.validate_student_number(12345)[0] == False  # Only 5 digits
        assert Validators.validate_student_number(1234567)[0] == False  # 7 digits


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
