import psycopg2

from .secrets import get_db_config


def get_connection():
    cfg = get_db_config()
    conn = psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        database=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
    )
    return conn

def setup_database():
    conn = get_connection() 
    cur = conn.cursor()
    
    
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