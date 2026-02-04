import re
from datetime import datetime

def validate_non_empty(value, field):
    if not value.strip():
        raise ValueError(f"{field} cannot be empty")
    return value.strip()

def validate_email(value):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, value):
        raise ValueError("Invalid email format")
    return value

def validate_date(value):
    try:
        datetime.strptime(value, '%Y-%m-%d')
        return value
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD")

def validate_grade(value):
    try:
        grade = float(value)
        if not (0 <= grade <= 100):
            raise ValueError("Grade must be between 0 and 100")
        return grade
    except ValueError:
        raise ValueError("Grade must be a number between 0 and 100")
