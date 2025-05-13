import sqlite3

def create_user_settings_table():
    conn = sqlite3.connect("osu_scores.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            username TEXT PRIMARY KEY,
            banned_mods TEXT DEFAULT '',
            acc_preference TEXT DEFAULT 'acc_98'
        )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_user_settings_table()
