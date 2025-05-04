import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_connection():
    # Get the database URL from environment variable
    db_url = os.getenv('DATABASE_URL')
    
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Use the URL directly with psycopg2
    return psycopg2.connect(db_url)

# Optional: initialize DB
def init_db():
    print("Database connection setup complete.")
