import sqlite3

def create_user_settings_table():
    conn = sqlite3.connect("osu_scores.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            username TEXT PRIMARY KEY,
            banned_mods TEXT DEFAULT 'HRDT,HDHRDT',
            acc_preference TEXT DEFAULT '98',
            fake_user INTEGER
        )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_user_settings_table()
