SELECT 
    students.name AS student_name, 
    students.email, 
    courses.course_name -- Adjust this if your column is named 'name' in the courses table
FROM students
JOIN enrollments ON students.id = enrollments.student_id
JOIN courses ON enrollments.course_id = courses.id
LIMIT 10;