-- Students
CREATE INDEX IF NOT EXISTS idx_students_email
ON students(email);

-- Enrollments
CREATE INDEX IF NOT EXISTS idx_enrollments_student_id
ON enrollments(student_id);

CREATE INDEX IF NOT EXISTS idx_enrollments_course_id
ON enrollments(course_id);

-- Grades
CREATE INDEX IF NOT EXISTS idx_grades_enrollment_id
ON grades(enrollment_id);

-- Attendance
CREATE INDEX IF NOT EXISTS idx_attendance_enrollment_id
ON attendance(enrollment_id);

CREATE INDEX IF NOT EXISTS idx_attendance_date
ON attendance(attendance_date);
