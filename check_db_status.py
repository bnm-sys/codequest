import psycopg2
import sys

def check_db():
    try:
        # Connect to the default 'postgres' database to check for 'codequest'
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="localhost",
            port="15432"
        )
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'codequest'")
        exists = cur.fetchone()
        conn.close()
        
        if exists:
            print("Database 'codequest' exists.")
            # Now try connecting to it
            conn_cq = psycopg2.connect(
                dbname="codequest",
                user="postgres",
                password="postgres",
                host="localhost",
                port="15432"
            )
            print("Successfully connected to 'codequest' database.")
            conn_cq.close()
        else:
            print("Database 'codequest' does NOT exist.")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error checking database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_db()
