import os
from app.db import get_connection

def run_sql_file(file_path):
    with open(file_path, 'r') as f:
        sql = f.read()

    conn = get_connection()
    cur = conn.cursor()
    
    # Check if this is a schema file
    if file_path.endswith('DB-01-company_module_schema.sql'):
        # Check if tables exist before creating
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'companies'
            )
        """)
        
        if not cur.fetchone()[0]:
            print(f"✅ Creating tables from: {file_path}")
            cur.execute(sql)
            conn.commit()
        else:
            print(f"ℹ️ Tables already exist in: {file_path}")
    else:
        print(f"✅ Executing: {file_path}")
        cur.execute(sql)
        conn.commit()
    
    cur.close()
    conn.close()

def run_all_sql():
    sql_dir = "app/sql"
    for filename in sorted(os.listdir(sql_dir)):
        if filename.endswith(".sql"):
            run_sql_file(os.path.join(sql_dir, filename))

if __name__ == "__main__":
    run_all_sql()
