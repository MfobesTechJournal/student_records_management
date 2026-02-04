# TODO List for Student Management System Fixes

## High-Impact Fixes
- [x] Update sql-queries/schema.sql: Add NOT NULL constraints, CHECK for grades (0-100), UNIQUE on enrollments (student_id, course_id), change attendance.status to present BOOLEAN
- [x] Change SQLite-style ? placeholders to psycopg2 %s in etl/students.py, etl/enrollments.py, etl/courses.py
- [x] Fix sql-queries/procedures.sql: Remove duplicate procedures, add sp_record_attendance, add GPA calculation (weighted by credits) and transcript status logic procedures
- [x] Fix sql-queries/views.sql: Rename duplicate vw_course_rosters to vw_attendance_summary
- [x] Add validators in etl/validation.py: validate_email, validate_date, validate_grade
- [x] Standardize DB config to port 5432 in etl/generate_sample_data.py and etl/generate_attendance.py
- [x] Update README.md to remove claims about tests (since none exist)
- [x] Ensure etl/generate_attendance.py uses present BOOLEAN (already does, but verify)

## Followup Steps
- [ ] Verify schema changes don't break existing data
- [ ] Test CLI and ETL scripts
- [ ] Run analysis queries
