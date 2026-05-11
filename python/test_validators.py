"""
Unit Tests for Validators
Tests input validation functions
"""

import pytest
from datetime import datetime, timedelta
from validators import Validators


class TestStudentNumberValidator:
    """Test student number validation"""
    
    def test_valid_student_number(self):
        """Test valid student number (YYYYRR format)"""
        valid, msg = Validators.validate_student_number(199545)
        assert valid == True
        assert msg == "Valid"
    
    def test_student_number_too_short(self):
        """Test student number with less than 6 digits"""
        valid, msg = Validators.validate_student_number(12345)
        assert valid == False
    
    def test_student_number_too_long(self):
        """Test student number with more than 6 digits"""
        valid, msg = Validators.validate_student_number(1234567)
        assert valid == False
    
    def test_student_number_future_year(self):
        """Test student number with future birth year"""
        future_year = datetime.now().year + 1
        valid, msg = Validators.validate_student_number(int(f"{future_year}45"))
        assert valid == False
    
    def test_student_number_past_year(self):
        """Test student number with very old birth year"""
        valid, msg = Validators.validate_student_number(194545)
        assert valid == False
    
    def test_student_number_not_integer(self):
        """Test student number that is not an integer"""
        valid, msg = Validators.validate_student_number("199545")
        assert valid == False


class TestEmailValidator:
    """Test email validation"""
    
    def test_valid_email(self):
        """Test valid email format"""
        valid, msg = Validators.validate_email("john.doe@example.com")
        assert valid == True
    
    def test_email_missing_at(self):
        """Test email without @ symbol"""
        valid, msg = Validators.validate_email("johndoeexample.com")
        assert valid == False
    
    def test_email_missing_domain(self):
        """Test email without domain"""
        valid, msg = Validators.validate_email("john@")
        assert valid == False
    
    def test_email_missing_extension(self):
        """Test email without extension"""
        valid, msg = Validators.validate_email("john@example")
        assert valid == False


class TestNameValidator:
    """Test name validation"""
    
    def test_valid_name(self):
        """Test valid name"""
        valid, msg = Validators.validate_name("John")
        assert valid == True
    
    def test_name_too_short(self):
        """Test name with only 1 character"""
        valid, msg = Validators.validate_name("A")
        assert valid == False
    
    def test_name_too_long(self):
        """Test name longer than 50 characters"""
        valid, msg = Validators.validate_name("A" * 51)
        assert valid == False
    
    def test_name_with_numbers(self):
        """Test name containing numbers"""
        valid, msg = Validators.validate_name("John123")
        assert valid == False
    
    def test_name_with_special_chars(self):
        """Test name with special characters"""
        valid, msg = Validators.validate_name("John@Doe")
        assert valid == False
    
    def test_name_with_hyphen(self):
        """Test valid name with hyphen"""
        valid, msg = Validators.validate_name("Mary-Jane")
        assert valid == True


class TestDateValidator:
    """Test date validation"""
    
    def test_valid_date(self):
        """Test valid date format"""
        valid, msg = Validators.validate_date("2024-01-15")
        assert valid == True
    
    def test_invalid_date_format(self):
        """Test invalid date format"""
        valid, msg = Validators.validate_date("01/15/2024")
        assert valid == False
    
    def test_invalid_month(self):
        """Test invalid month"""
        valid, msg = Validators.validate_date("2024-13-01")
        assert valid == False
    
    def test_invalid_day(self):
        """Test invalid day"""
        valid, msg = Validators.validate_date("2024-01-32")
        assert valid == False


class TestDateOfBirthValidator:
    """Test date of birth validation"""
    
    def test_valid_dob(self):
        """Test valid date of birth"""
        dob = (datetime.now() - timedelta(days=365*25)).strftime("%Y-%m-%d")
        valid, msg = Validators.validate_date_of_birth(dob)
        assert valid == True
    
    def test_dob_too_young(self):
        """Test person under 18"""
        dob = (datetime.now() - timedelta(days=365*17)).strftime("%Y-%m-%d")
        valid, msg = Validators.validate_date_of_birth(dob)
        assert valid == False
    
    def test_dob_too_old(self):
        """Test person over 100 years old"""
        # Use 120 years to ensure definitely over 100
        dob = (datetime.now() - timedelta(days=365*120)).strftime("%Y-%m-%d")
        valid, msg = Validators.validate_date_of_birth(dob)
        assert valid == False


class TestAcademicYearValidator:
    """Test academic year validation"""
    
    def test_valid_academic_year(self):
        """Test valid academic year"""
        valid, msg = Validators.validate_academic_year("2024-2025")
        assert valid == True
    
    def test_academic_year_no_hyphen(self):
        """Test academic year without hyphen"""
        valid, msg = Validators.validate_academic_year("20242025")
        assert valid == False
    
    def test_academic_year_wrong_end(self):
        """Test academic year where end year is not start+1"""
        valid, msg = Validators.validate_academic_year("2024-2026")
        assert valid == False
    
    def test_academic_year_invalid_format(self):
        """Test academic year with non-numeric values"""
        valid, msg = Validators.validate_academic_year("XXXX-XXXX")
        assert valid == False


class TestTermValidator:
    """Test term validation"""
    
    def test_valid_term_1(self):
        """Test term 1"""
        valid, msg = Validators.validate_term("1")
        assert valid == True
    
    def test_valid_term_2(self):
        """Test term 2"""
        valid, msg = Validators.validate_term("2")
        assert valid == True
    
    def test_invalid_term(self):
        """Test invalid term"""
        valid, msg = Validators.validate_term("3")
        assert valid == False


class TestGradeTypeValidator:
    """Test grade type validation"""
    
    def test_valid_grade_type_test(self):
        """Test grade type: test"""
        valid, msg = Validators.validate_grade_type("test")
        assert valid == True
    
    def test_valid_grade_type_assignment(self):
        """Test grade type: assignment"""
        valid, msg = Validators.validate_grade_type("assignment")
        assert valid == True
    
    def test_valid_grade_type_exam(self):
        """Test grade type: exam"""
        valid, msg = Validators.validate_grade_type("exam")
        assert valid == True
    
    def test_invalid_grade_type(self):
        """Test invalid grade type"""
        valid, msg = Validators.validate_grade_type("quiz")
        assert valid == False


class TestGradeValueValidator:
    """Test grade value validation"""
    
    def test_valid_grade_0(self):
        """Test minimum valid grade"""
        valid, msg = Validators.validate_grade_value(0)
        assert valid == True
    
    def test_valid_grade_100(self):
        """Test maximum valid grade"""
        valid, msg = Validators.validate_grade_value(100)
        assert valid == True
    
    def test_valid_grade_50(self):
        """Test middle-range grade"""
        valid, msg = Validators.validate_grade_value(50)
        assert valid == True
    
    def test_grade_below_range(self):
        """Test grade below 0"""
        valid, msg = Validators.validate_grade_value(-1)
        assert valid == False
    
    def test_grade_above_range(self):
        """Test grade above 100"""
        valid, msg = Validators.validate_grade_value(101)
        assert valid == False
    
    def test_grade_non_numeric(self):
        """Test non-numeric grade"""
        valid, msg = Validators.validate_grade_value("A")
        assert valid == False


class TestAttendanceStatusValidator:
    """Test attendance status validation"""
    
    def test_valid_status_present(self):
        """Test status: present"""
        valid, msg = Validators.validate_attendance_status("present")
        assert valid == True
    
    def test_valid_status_absent(self):
        """Test status: absent"""
        valid, msg = Validators.validate_attendance_status("absent")
        assert valid == True
    
    def test_valid_status_late(self):
        """Test status: late"""
        valid, msg = Validators.validate_attendance_status("late")
        assert valid == True
    
    def test_invalid_status(self):
        """Test invalid status"""
        valid, msg = Validators.validate_attendance_status("excused")
        assert valid == False


class TestStudentStatusValidator:
    """Test student status validation"""
    
    def test_valid_status_active(self):
        """Test status: active"""
        valid, msg = Validators.validate_student_status("active")
        assert valid == True
    
    def test_valid_status_inactive(self):
        """Test status: inactive"""
        valid, msg = Validators.validate_student_status("inactive")
        assert valid == True
    
    def test_valid_status_graduated(self):
        """Test status: graduated"""
        valid, msg = Validators.validate_student_status("graduated")
        assert valid == True
    
    def test_invalid_status(self):
        """Test invalid status"""
        valid, msg = Validators.validate_student_status("suspended")
        assert valid == False


class TestIntegerValidator:
    """Test integer validation"""
    
    def test_valid_integer(self):
        """Test valid integer"""
        valid, msg = Validators.validate_integer(42)
        assert valid == True
    
    def test_valid_integer_with_range(self):
        """Test valid integer within range"""
        valid, msg = Validators.validate_integer(50, min_val=1, max_val=100)
        assert valid == True
    
    def test_integer_below_min(self):
        """Test integer below minimum"""
        valid, msg = Validators.validate_integer(0, min_val=1, max_val=100)
        assert valid == False
    
    def test_integer_above_max(self):
        """Test integer above maximum"""
        valid, msg = Validators.validate_integer(101, min_val=1, max_val=100)
        assert valid == False
    
    def test_non_numeric_integer(self):
        """Test non-numeric value"""
        valid, msg = Validators.validate_integer("abc")
        assert valid == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
