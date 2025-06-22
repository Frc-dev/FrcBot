import sqlite3

def add_algo_column():
    conn = sqlite3.connect("osu_scores.db")
    cursor = conn.cursor()

    # Add the fake_user column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE scores ADD COLUMN acc_99 FLOAT")
        print("Added 'acc_99' column successfully.")
    except sqlite3.OperationalError as e:
        # This error usually means the column already exists
        if "duplicate column name" in str(e).lower():
            print("'acc_99' column already exists.")
        else:
            raise

    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_algo_column()
