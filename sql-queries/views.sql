--Student Transcript View

CREATE OR REPLACE VIEW vw_student_transcripts AS
SELECT
    s.student_id,
    s.first_name,
    s.last_name,
    c.course_name,
    g.grade
FROM students s
JOIN enrollments e ON s.student_id = e.student_id
JOIN courses c ON e.course_id = c.course_id
LEFT JOIN grades g ON e.enrollment_id = g.enrollment_id;

-- Course Roster View

CREATE OR REPLACE VIEW vw_course_rosters AS
SELECT
    c.course_name,
    s.student_id,
    s.first_name,
    s.last_name,
    s.email
FROM courses c
JOIN enrollments e ON c.course_id = e.course_id
JOIN students s ON e.student_id = s.student_id;

-- Attendance Summary View
CREATE OR REPLACE VIEW vw_course_rosters AS
SELECT
    c.course_name,
    s.student_id,
    s.first_name,
    s.last_name,
    s.email
FROM courses c
JOIN enrollments e ON c.course_id = e.course_id
JOIN students s ON e.student_id = s.student_id;

