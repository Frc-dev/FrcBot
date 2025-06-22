import sqlite3
import os
from constants import DB_PATH

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Join with the DB filename
conn = sqlite3.connect(DB_PATH)

# 2. Create a cursor object to execute SQL commands
cursor = conn.cursor()

# 3. Create a table
cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    map_name TEXT NOT NULL,
    beatmap_set_id INTEGER,
    beatmap_id INTEGER,
    mods TEXT NOT NULL,
    unique_score_id
    acc_95 FLOAT,
    acc_98 FLOAT,
    acc_100 FLOAT,
    updated_at DATETIME NOT NULL
)
""")

conn.commit()
conn.close()
