-- Enroll Student Prodedure

CREATE OR REPLACE PROCEDURE sp_enroll_student(
    p_student_id INT,
    p_course_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO enrollments (student_id, course_id, enrollment_date)
    VALUES (p_student_id, p_course_id, CURRENT_DATE)
    ON CONFLICT (student_id, course_id) DO NOTHING;
END;
$$;
-- Record Attendance Procedure
CREATE OR REPLACE PROCEDURE sp_enroll_student(
    p_student_id INT,
    p_course_id INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO enrollments (student_id, course_id, enrollment_date)
    VALUES (p_student_id, p_course_id, CURRENT_DATE)
    ON CONFLICT (student_id, course_id) DO NOTHING;
END;
$$;
-- Record Attendance Procedure
CREATE OR REPLACE PROCEDURE sp_record_grade(
    p_enrollment_id INT,
    p_grade NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO grades (enrollment_id, grade)
    VALUES (p_enrollment_id, p_grade)
    ON CONFLICT (enrollment_id)
    DO UPDATE SET grade = EXCLUDED.grade;
END;
$$;
