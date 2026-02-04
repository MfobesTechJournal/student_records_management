-- Enroll Student Procedure

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
CREATE OR REPLACE PROCEDURE sp_record_attendance(
    p_enrollment_id INT,
    p_attendance_date DATE,
    p_present BOOLEAN
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO attendance (enrollment_id, attendance_date, present)
    VALUES (p_enrollment_id, p_attendance_date, p_present)
    ON CONFLICT (enrollment_id, attendance_date) DO NOTHING;
END;
$$;

-- Record Grade Procedure
CREATE OR REPLACE PROCEDURE sp_record_grade(
    p_enrollment_id INT,
    p_grade NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO grades (enrollment_id, grade, graded_at)
    VALUES (p_enrollment_id, p_grade, CURRENT_DATE)
    ON CONFLICT (enrollment_id)
    DO UPDATE SET grade = EXCLUDED.grade, graded_at = CURRENT_DATE;
END;
$$;

-- Calculate GPA Procedure (weighted by credits)
CREATE OR REPLACE FUNCTION fn_calculate_gpa(p_student_id INT)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    total_points NUMERIC := 0;
    total_credits INT := 0;
    gpa NUMERIC;
BEGIN
    SELECT
        SUM(g.grade * c.credits),
        SUM(c.credits)
    INTO total_points, total_credits
    FROM grades g
    JOIN enrollments e ON g.enrollment_id = e.enrollment_id
    JOIN courses c ON e.course_id = c.course_id
    WHERE e.student_id = p_student_id;

    IF total_credits > 0 THEN
        gpa := total_points / total_credits;
    ELSE
        gpa := 0;
    END IF;

    RETURN gpa;
END;
$$;

-- Get Transcript Status Procedure
CREATE OR REPLACE FUNCTION fn_get_transcript_status(p_student_id INT)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    gpa NUMERIC;
BEGIN
    gpa := fn_calculate_gpa(p_student_id);

    IF gpa >= 3.5 THEN
        RETURN 'Honors';
    ELSIF gpa >= 2.0 THEN
        RETURN 'Pass';
    ELSE
        RETURN 'Fail';
    END IF;
END;
$$;
