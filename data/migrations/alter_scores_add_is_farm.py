import sqlite3
from constants import DB_PATH

def add_algo_column():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add the fake_user column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE scores ADD COLUMN is_farm INTEGER DEFAULT 0")
        print("Added 'is_farm' column successfully.")
    except sqlite3.OperationalError as e:
        # This error usually means the column already exists
        if "duplicate column name" in str(e).lower():
            print("'is_farm' column already exists.")
        else:
            raise

    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_algo_column()
