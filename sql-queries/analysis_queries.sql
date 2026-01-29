-- View all students in a specific course
SELECT
    c.course_name,
    s.student_id,
    s.first_name,
    s.last_name,
    s.email
FROM enrollments e
JOIN students s ON e.student_id = s.student_id
JOIN courses c ON e.course_id = c.course_id
WHERE c.course_name = 'Project Management'
ORDER BY s.last_name;

-- Course-level average grades

SELECT
    c.course_name,
    AVG(g.grade) AS avg_grade
FROM grades g
JOIN enrollments e ON g.enrollment_id = e.enrollment_id
JOIN courses c ON e.course_id = c.course_id
GROUP BY c.course_name
ORDER BY avg_grade DESC;

--  Identify students with <75% attendance

SELECT
    s.student_id,
    s.first_name,
    s.last_name,
    c.course_name,
    (SUM(CASE WHEN a.present THEN 1 ELSE 0 END) * 100.0 / COUNT(a.attendance_id)) AS attendance_percent
FROM attendance a
JOIN enrollments e ON a.enrollment_id = e.enrollment_id
JOIN students s ON e.student_id = s.student_id
JOIN courses c ON e.course_id = c.course_id
GROUP BY s.student_id, s.first_name, s.last_name, c.course_name
HAVING (SUM(CASE WHEN a.present THEN 1 ELSE 0 END) * 100.0 / COUNT(a.attendance_id)) < 75;

-- Rank top 10 students by GPA

SELECT
    s.student_id,
    s.first_name,
    s.last_name,
    AVG(g.grade) AS gpa
FROM grades g
JOIN enrollments e ON g.enrollment_id = e.enrollment_id
JOIN students s ON e.student_id = s.student_id
GROUP BY s.student_id, s.first_name, s.last_name
ORDER BY gpa DESC
LIMIT 10;

--Generate course enrollment stats

SELECT
    c.course_name,
    COUNT(e.student_id) AS num_students
FROM courses c
LEFT JOIN enrollments e ON c.course_id = e.course_id
GROUP BY c.course_name
ORDER BY num_students DESC;
