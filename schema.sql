DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS grades CASCADE;
DROP TABLE IF EXISTS enrollments CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS students CASCADE;

CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255) UNIQUE,
    date_of_birth DATE,
    registered_at DATE DEFAULT CURRENT_DATE
);

CREATE TABLE courses (
    course_id SERIAL PRIMARY KEY,
    course_name VARCHAR(255),
    course_code VARCHAR(50) UNIQUE,
    credits INT
);

CREATE TABLE enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id),
    course_id INT REFERENCES courses(course_id),
    enrollment_date DATE
);

CREATE TABLE grades (
    grade_id SERIAL PRIMARY KEY,
    enrollment_id INT REFERENCES enrollments(enrollment_id),
    grade DECIMAL,
    graded_at DATE
);

CREATE TABLE attendance (
    attendance_id SERIAL PRIMARY KEY,
    enrollment_id INT REFERENCES enrollments(enrollment_id),
    attendance_date DATE,
    status VARCHAR(50)
);
