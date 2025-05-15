import sqlite3

DB_PATH = "osu_scores.db"

def migrate_user_settings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Step 1: Rename the old table
    cursor.execute("ALTER TABLE user_settings RENAME TO user_settings_old")

    # Step 2: Create new table with updated defaults
    cursor.execute("""
        CREATE TABLE user_settings (
            username TEXT PRIMARY KEY CHECK(length(username) <= 32),
            banned_mods TEXT DEFAULT 'HRDT,HDHRDT' CHECK(length(banned_mods) <= 128),
            acc_preference TEXT DEFAULT '98' CHECK(acc_preference IN ('95', '97', '98', '99', '100')),
            fake_user INTEGER
        )
    """)

    # Step 3: Copy data from old to new table
    cursor.execute("""
        INSERT INTO user_settings (username, banned_mods, acc_preference, fake_user)
        SELECT username,
               COALESCE(NULLIF(banned_mods, ''), 'HRDT,HDHRDT'),
               COALESCE(NULLIF(acc_preference, ''), '98'),
               fake_user
        FROM user_settings_old
    """)

    # Step 4: Drop the old table
    cursor.execute("DROP TABLE user_settings_old")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate_user_settings()
