import psycopg2

def get_connection():
    return psycopg2.connect(
        database="pmbackend",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5433"
    )

# Optional: initialize DB
def init_db():
    print("Database connection setup complete.")
