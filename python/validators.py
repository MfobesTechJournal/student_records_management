"""
Input Validators Module
Validates user input before database operations
"""

import re
from datetime import datetime


class Validators:
    """Input validation functions"""
    
    @staticmethod
    def validate_student_number(student_number):
        """
        Validate student number format: YYYYRR (6 digits)
        Example: 199545 (birth year 1995, random suffix 45)
        """
        if not isinstance(student_number, int):
            return False, "Student number must be an integer"
        
        if len(str(student_number)) != 6:
            return False, "Student number must be exactly 6 digits (YYYYRR format)"
        
        year = int(str(student_number)[:4])
        if year < 1950 or year > datetime.now().year:
            return False, f"Birth year must be between 1950 and {datetime.now().year}"
        
        return True, "Valid"
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return True, "Valid"
        return False, "Invalid email format"
    
    @staticmethod
    def validate_name(name):
        """Validate first/last name"""
        if not name or len(name) < 2 or len(name) > 50:
            return False, "Name must be 2-50 characters"
        
        if not name.replace(" ", "").replace("-", "").isalpha():
            return False, "Name must contain only letters, spaces, or hyphens"
        
        return True, "Valid"
    
    @staticmethod
    def validate_date(date_str, format="%Y-%m-%d"):
        """Validate date format"""
        try:
            datetime.strptime(date_str, format)
            return True, "Valid"
        except ValueError:
            return False, f"Invalid date format. Use {format}"
    
    @staticmethod
    def validate_date_of_birth(date_str):
        """Validate date of birth (must be 18+ years old)"""
        valid, msg = Validators.validate_date(date_str)
        if not valid:
            return False, msg
        
        try:
            dob = datetime.strptime(date_str, "%Y-%m-%d")
            today = datetime.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            if age < 18:
                return False, "Student must be at least 18 years old"
            
            if age > 100:
                return False, "Invalid date of birth (age > 100)"
            
            return True, "Valid"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def validate_academic_year(year_str):
        """
        Validate academic year format: YYYY-YYYY
        Example: 2024-2025
        """
        if '-' not in year_str:
            return False, "Academic year must be in format YYYY-YYYY (e.g., 2024-2025)"
        
        parts = year_str.split('-')
        if len(parts) != 2:
            return False, "Academic year must have format YYYY-YYYY"
        
        try:
            year1 = int(parts[0])
            year2 = int(parts[1])
            
            if year2 != year1 + 1:
                return False, f"End year must be {year1 + 1} (start year + 1)"
            
            if year1 < 2000 or year1 > datetime.now().year + 5:
                return False, "Academic year must be realistic (2000-2030)"
            
            return True, "Valid"
        except ValueError:
            return False, "Academic year must contain valid integers"
    
    @staticmethod
    def validate_term(term):
        """Validate enrollment term: 1 or 2"""
        if term not in ['1', '2']:
            return False, "Term must be '1' (Fall) or '2' (Spring)"
        return True, "Valid"
    
    @staticmethod
    def validate_grade_type(grade_type):
        """Validate grade type"""
        valid_types = ['test', 'assignment', 'exam']
        if grade_type.lower() not in valid_types:
            return False, f"Grade type must be one of: {', '.join(valid_types)}"
        return True, "Valid"
    
    @staticmethod
    def validate_grade_value(grade_value):
        """Validate grade value (0-100)"""
        try:
            grade = int(grade_value)
            if grade < 0 or grade > 100:
                return False, "Grade must be between 0 and 100"
            return True, "Valid"
        except ValueError:
            return False, "Grade must be a number"
    
    @staticmethod
    def validate_attendance_status(status):
        """Validate attendance status"""
        valid_statuses = ['present', 'absent', 'late']
        if status.lower() not in valid_statuses:
            return False, f"Status must be one of: {', '.join(valid_statuses)}"
        return True, "Valid"
    
    @staticmethod
    def validate_student_status(status):
        """Validate student status"""
        valid_statuses = ['active', 'inactive', 'graduated']
        if status.lower() not in valid_statuses:
            return False, f"Status must be one of: {', '.join(valid_statuses)}"
        return True, "Valid"
    
    @staticmethod
    def validate_integer(value, min_val=None, max_val=None):
        """Validate integer input"""
        try:
            num = int(value)
            if min_val is not None and num < min_val:
                return False, f"Value must be at least {min_val}"
            if max_val is not None and num > max_val:
                return False, f"Value must be at most {max_val}"
            return True, "Valid"
        except ValueError:
            return False, "Input must be a valid integer"
    
    @staticmethod
    def validate_grade(grade_value):
        """Validate grade value"""
        try:
            grade = int(grade_value)
            if 0 <= grade <= 100:
                return True
            return False
        except:
            return False
