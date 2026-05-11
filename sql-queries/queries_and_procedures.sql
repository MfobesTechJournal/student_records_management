-- ============================================================================
-- Phase 5: SQL Query Development - Beginner Friendly
-- Student Records Management System - Simple Queries and Stored Procedures
-- PostgreSQL Implementation
-- ============================================================================

-- This file contains:
-- 1. Simple views for common queries
-- 2. Basic analytical queries (students by course, grades, attendance, GPA)
-- 3. Essential stored procedures (add enrollment, record grades, mark attendance)
-- Written for beginners with clear, simple SQL


-- =============================================================================
-- SECTION 1: VIEWS (Simplified)
-- =============================================================================

-- View: Student Transcripts
-- Shows courses a student is enrolled in with average grades
CREATE OR REPLACE VIEW vw_student_transcripts AS
SELECT 
    s.student_id,
    s.student_number,
    s.first_name,
    s.last_name,
    c.course_code,
    c.course_name,
    e.academic_year,
    e.term,
    ROUND(AVG(g.grade_value)::NUMERIC, 2) AS average_grade,
    CASE 
        WHEN ROUND(AVG(g.grade_value)::NUMERIC, 2) >= 50 THEN 'Pass'
        WHEN ROUND(AVG(g.grade_value)::NUMERIC, 2) >= 40 THEN 'Supplementary'
        ELSE 'Failed'
    END AS grade_status
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
LEFT JOIN grades g ON e.enrollment_id = g.enrollment_id
WHERE s.status = 'active'
GROUP BY s.student_id, s.student_number, s.first_name, s.last_name, 
         c.course_code, c.course_name, e.academic_year, e.term, e.enrollment_id
ORDER BY s.student_id, e.academic_year DESC;


-- View: Course Rosters
-- Shows students in each course with attendance counts
CREATE OR REPLACE VIEW vw_course_rosters AS
SELECT 
    c.course_code,
    c.course_name,
    s.student_number,
    s.first_name,
    s.last_name,
    e.academic_year,
    e.term,
    COUNT(a.attendance_id) AS total_classes,
    SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS classes_attended
FROM courses c
JOIN enrollments e ON c.course_id = e.course_id
JOIN students s ON e.student_id = s.student_id
LEFT JOIN attendance a ON e.enrollment_id = a.enrollment_id
WHERE c.status = 'active' AND s.status = 'active'
GROUP BY c.course_id, c.course_code, c.course_name, s.student_id, s.student_number, s.first_name, 
         s.last_name, e.academic_year, e.term, e.enrollment_id
ORDER BY c.course_code, s.student_id;


-- View: Student Attendance Reports
-- Shows attendance records for each student
CREATE OR REPLACE VIEW vw_attendance_reports AS
SELECT 
    s.student_number,
    s.first_name,
    s.last_name,
    c.course_code,
    c.course_name,
    e.academic_year,
    COUNT(a.attendance_id) AS total_classes,
    SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS classes_present,
    SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) AS classes_absent
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
LEFT JOIN attendance a ON e.enrollment_id = a.enrollment_id
WHERE s.status = 'active'
GROUP BY s.student_number, s.first_name, s.last_name, c.course_code, 
         c.course_name, e.academic_year
ORDER BY s.student_number, c.course_code;


-- =============================================================================
-- SECTION 2: GRADE WEIGHTS & WEIGHTED GPA CALCULATION
-- =============================================================================

-- Grade Weights Table: Defines how much each assessment contributes
CREATE TABLE IF NOT EXISTS grade_weights (
    grade_type VARCHAR PRIMARY KEY,
    weight NUMERIC(5,2) CHECK (weight > 0 AND weight <= 100)
);

INSERT INTO grade_weights (grade_type, weight) VALUES
('assignment', 30),
('test', 30),
('exam', 40)
ON CONFLICT (grade_type) DO NOTHING;


-- View: Student Course Results (Weighted Average)
-- Shows each course with final weighted average for each student
CREATE OR REPLACE VIEW vw_student_course_results AS
SELECT
    s.student_id,
    s.student_number,
    s.first_name,
    s.last_name,
    c.course_code,
    c.course_name,
    e.academic_year,
    e.term,
    ROUND(
        SUM(g.grade_value * gw.weight) / SUM(gw.weight),
        2
    ) AS final_average,
    CASE 
        WHEN ROUND(
            SUM(g.grade_value * gw.weight) / SUM(gw.weight),
            2
        ) >= 50 THEN 'Pass'
        WHEN ROUND(
            SUM(g.grade_value * gw.weight) / SUM(gw.weight),
            2
        ) >= 40 THEN 'Supplementary'
        ELSE 'Failed'
    END AS grade_status
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
JOIN grades g ON e.enrollment_id = g.enrollment_id
JOIN grade_weights gw ON g.grade_type = gw.grade_type
WHERE s.status = 'active'
GROUP BY
    s.student_id,
    s.student_number,
    s.first_name,
    s.last_name,
    c.course_code,
    c.course_name,
    e.academic_year,
    e.term,
    e.enrollment_id;


-- View: Student GPA (Weighted Across All Courses)
-- GPA is the average of all weighted course final averages
CREATE OR REPLACE VIEW vw_student_gpa AS
SELECT
    student_id,
    student_number,
    first_name,
    last_name,
    ROUND(AVG(final_average), 2) AS gpa
FROM vw_student_course_results
GROUP BY
    student_id,
    student_number,
    first_name,
    last_name;


-- =============================================================================
-- SECTION 2: ANALYTICAL QUERIES (Enhanced with Weighted GPA)
-- =============================================================================

-- Query 1: Get all students enrolled in a specific course with weighted average
CREATE OR REPLACE FUNCTION get_students_by_course(p_course_id INT)
RETURNS TABLE (
    student_number INT,
    first_name VARCHAR,
    last_name VARCHAR,
    academic_year VARCHAR,
    weighted_average NUMERIC
) AS $$
SELECT 
    s.student_number::INT,
    s.first_name,
    s.last_name,
    e.academic_year,
    ROUND(
        SUM(g.grade_value * gw.weight) / SUM(gw.weight),
        2
    ) AS weighted_average
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
JOIN grades g ON e.enrollment_id = g.enrollment_id
JOIN grade_weights gw ON g.grade_type = gw.grade_type
WHERE c.course_id = p_course_id AND s.status = 'active'
GROUP BY s.student_id, s.student_number, s.first_name, s.last_name, e.academic_year
ORDER BY s.last_name, s.first_name;
$$ LANGUAGE SQL;


-- Query 2: Calculate average grades per course
CREATE OR REPLACE FUNCTION get_course_grade_statistics()
RETURNS TABLE (
    course_code VARCHAR,
    course_name VARCHAR,
    total_students INT,
    total_grades INT,
    average_grade NUMERIC,
    highest_grade INT,
    lowest_grade INT
) AS $$
SELECT 
    c.course_code,
    c.course_name,
    COUNT(DISTINCT e.student_id) AS total_students,
    COUNT(g.grades_id) AS total_grades,
    ROUND(AVG(g.grade_value)::NUMERIC, 2) AS average_grade,
    MAX(g.grade_value) AS highest_grade,
    MIN(g.grade_value) AS lowest_grade
FROM courses c
LEFT JOIN enrollments e ON c.course_id = e.course_id
LEFT JOIN grades g ON e.enrollment_id = g.enrollment_id
WHERE c.status = 'active'
GROUP BY c.course_id, c.course_code, c.course_name
ORDER BY c.course_code;
$$ LANGUAGE SQL;


-- Query 3: Identify students with less than 75% attendance
CREATE OR REPLACE FUNCTION get_low_attendance_students()
RETURNS TABLE (
    student_number INT,
    first_name VARCHAR,
    last_name VARCHAR,
    course_code VARCHAR,
    total_classes INT,
    classes_attended INT,
    attendance_percentage NUMERIC
) AS $$
SELECT 
    s.student_number::INT,
    s.first_name,
    s.last_name,
    c.course_code,
    COUNT(a.attendance_id) AS total_classes,
    SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS classes_attended,
    ROUND((SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END)::NUMERIC / 
           COUNT(a.attendance_id) * 100), 2) AS attendance_percentage
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
LEFT JOIN attendance a ON e.enrollment_id = a.enrollment_id
WHERE s.status = 'active'
GROUP BY s.student_id, s.student_number, s.first_name, s.last_name, c.course_code
HAVING COUNT(a.attendance_id) > 0 AND (SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END)::NUMERIC / COUNT(a.attendance_id) * 100) < 75
ORDER BY s.student_number;
$$ LANGUAGE SQL;


-- Query 4: Rank top students by weighted GPA
CREATE OR REPLACE FUNCTION get_top_students_by_gpa(p_limit INT DEFAULT 10)
RETURNS TABLE (
    rank INT,
    student_number INT,
    first_name VARCHAR,
    last_name VARCHAR,
    gpa NUMERIC
) AS $$
SELECT
    ROW_NUMBER() OVER (ORDER BY gpa DESC) AS rank,
    student_number,
    first_name,
    last_name,
    gpa
FROM vw_student_gpa
ORDER BY gpa DESC
LIMIT p_limit;
$$ LANGUAGE SQL;


-- Query 5: Get enrollment statistics
CREATE OR REPLACE FUNCTION get_enrollment_statistics()
RETURNS TABLE (
    course_code VARCHAR,
    course_name VARCHAR,
    total_enrollments INT,
    unique_students INT,
    students_with_grades INT
) AS $$
SELECT 
    c.course_code,
    c.course_name,
    COUNT(e.enrollment_id) AS total_enrollments,
    COUNT(DISTINCT e.student_id) AS unique_students,
    COUNT(DISTINCT g.enrollment_id) AS students_with_grades
FROM courses c
LEFT JOIN enrollments e ON c.course_id = e.course_id
LEFT JOIN grades g ON e.enrollment_id = g.enrollment_id
WHERE c.status = 'active'
GROUP BY c.course_id, c.course_code, c.course_name
ORDER BY c.course_code;
$$ LANGUAGE SQL;


-- Query 6: Get detailed course breakdown for a student (weights & contributions)
CREATE OR REPLACE FUNCTION get_student_course_breakdown(p_student_id INT)
RETURNS TABLE (
    course_code VARCHAR,
    course_name VARCHAR,
    grade_type VARCHAR,
    grade_value INT,
    weight NUMERIC,
    weighted_contribution NUMERIC
) AS $$
SELECT
    c.course_code,
    c.course_name,
    g.grade_type,
    g.grade_value,
    gw.weight,
    ROUND(g.grade_value * gw.weight / 100, 2) AS weighted_contribution
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
JOIN grades g ON e.enrollment_id = g.enrollment_id
JOIN grade_weights gw ON g.grade_type = gw.grade_type
WHERE s.student_id = p_student_id
ORDER BY c.course_code, g.grade_type;
$$ LANGUAGE SQL;


-- Query 7: Get student GPA details
CREATE OR REPLACE FUNCTION get_student_gpa(p_student_id INT)
RETURNS TABLE (
    student_number INT,
    first_name VARCHAR,
    last_name VARCHAR,
    gpa NUMERIC
) AS $$
SELECT
    student_number,
    first_name,
    last_name,
    gpa
FROM vw_student_gpa
WHERE student_id = p_student_id;
$$ LANGUAGE SQL;


-- =============================================================================
-- SECTION 3: STORED PROCEDURES (Essential Only)
-- =============================================================================

-- Procedure 1: Add Student Enrollment
-- Validates student and course exist, then creates enrollment
CREATE OR REPLACE PROCEDURE add_student_enrollment(
    OUT p_enrollment_id INT,
    p_student_id INT,
    p_course_id INT,
    p_academic_year VARCHAR,
    p_term CHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check if student exists
    IF NOT EXISTS(SELECT 1 FROM students WHERE student_id = p_student_id) THEN
        RAISE EXCEPTION 'Student ID % not found', p_student_id;
    END IF;
    
    -- Check if course exists
    IF NOT EXISTS(SELECT 1 FROM courses WHERE course_id = p_course_id) THEN
        RAISE EXCEPTION 'Course ID % not found', p_course_id;
    END IF;
    
    -- Insert enrollment
    INSERT INTO enrollments (student_id, course_id, academic_year, term, enrollment_date)
    VALUES (p_student_id, p_course_id, p_academic_year, p_term, CURRENT_DATE)
    RETURNING enrollment_id INTO p_enrollment_id;
    
END $$;


-- Procedure 2: Record Student Grade with Validation
-- Adds a grade for an enrollment with weight validation
CREATE OR REPLACE PROCEDURE record_grade(
    OUT p_grades_id INT,
    p_enrollment_id INT,
    p_grade_type VARCHAR,
    p_grade_value INT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check if enrollment exists
    IF NOT EXISTS(SELECT 1 FROM enrollments WHERE enrollment_id = p_enrollment_id) THEN
        RAISE EXCEPTION 'Enrollment ID % not found', p_enrollment_id;
    END IF;
    
    -- Check if grade type is valid (exists in weights)
    IF NOT EXISTS(SELECT 1 FROM grade_weights WHERE grade_type = p_grade_type) THEN
        RAISE EXCEPTION 'Invalid grade type: %', p_grade_type;
    END IF;
    
    -- Validate grade value is 0-100
    IF p_grade_value < 0 OR p_grade_value > 100 THEN
        RAISE EXCEPTION 'Grade must be between 0 and 100';
    END IF;
    
    -- Insert grade
    INSERT INTO grades (enrollment_id, grade_type, grade_value, grade_date)
    VALUES (p_enrollment_id, p_grade_type, p_grade_value, CURRENT_DATE)
    RETURNING grades_id INTO p_grades_id;
    
END $$;


-- Procedure 3: Mark Attendance
-- Records attendance for a student in a course
CREATE OR REPLACE PROCEDURE mark_attendance(
    OUT p_attendance_id INT,
    p_enrollment_id INT,
    p_status VARCHAR,
    p_attendance_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check if enrollment exists
    IF NOT EXISTS(SELECT 1 FROM enrollments WHERE enrollment_id = p_enrollment_id) THEN
        RAISE EXCEPTION 'Enrollment ID % not found', p_enrollment_id;
    END IF;
    
    -- Insert or update attendance
    INSERT INTO attendance (enrollment_id, attendance_date, status)
    VALUES (p_enrollment_id, p_attendance_date, p_status)
    RETURNING attendance_id INTO p_attendance_id;
    
END $$;


-- =============================================================================
-- SECTION 4: USAGE EXAMPLES (Test Cases for Weighted GPA System)
-- =============================================================================

-- Verify grade weights are configured
SELECT * FROM grade_weights;

-- View: Student Course Results with Weighted Averages
SELECT * FROM vw_student_course_results LIMIT 5;

-- View: Student GPAs (Weighted across all courses)
SELECT * FROM vw_student_gpa LIMIT 5;

-- Query 1: Get all students in a specific course with weighted average (e.g., course_id = 1)
SELECT * FROM get_students_by_course(1);

-- Query 2: Get average grades for all courses
SELECT * FROM get_course_grade_statistics();

-- Query 3: Get students with poor attendance
SELECT * FROM get_low_attendance_students();

-- Query 4: Get top 10 students by weighted GPA
SELECT * FROM get_top_students_by_gpa(10);

-- Query 5: Get enrollment statistics
SELECT * FROM get_enrollment_statistics();

-- Query 6: Get detailed breakdown for a specific student (showing weights and contributions)
SELECT * FROM get_student_course_breakdown(1);

-- Query 7: Get GPA for a specific student
SELECT * FROM get_student_gpa(1);

-- Procedure 1: Add a new enrollment
-- CALL add_student_enrollment(NULL, 1, 2, '2024-2025', '1');

-- Procedure 2: Record a grade with validation
-- CALL record_grade(NULL, 1, 'test', 85);

-- Procedure 3: Mark attendance
-- CALL mark_attendance(NULL, 1, 'present', CURRENT_TIMESTAMP);
