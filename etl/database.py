import psycopg2 # Changed from sqlite3 to psycopg2

def get_connection():
    # Use the connection details from your pgAdmin properties
    return psycopg2.connect(
        dbname="student_records_db", # From your pgAdmin maintenance database
        user="postgres",              # Your pgAdmin username
        password="123456",            # The password you used for your connection
        host="localhost",             # Your local server address
        port="5433"                   # The specific port shown in your pgAdmin
    )

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