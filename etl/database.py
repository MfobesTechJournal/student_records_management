import os
import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5433"),
        database=os.getenv("DB_NAME", "student_records_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD","123456")
    )
    return conn

def setup_database():
    conn = get_connection() # Connects to PostgreSQL instead of school.db
    cur = conn.cursor()
    
    # Create the table using PostgreSQL syntax
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,    -- SERIAL is the Postgres way to do AUTOINCREMENT
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()
    print("PostgreSQL database setup complete!")

if __name__ == "__main__":
    setup_database()