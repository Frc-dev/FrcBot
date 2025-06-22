import sqlite3
import random

def get_maps_in_pp_range(pp_min, pp_max, db_path="osu_scores.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT map_name, beatmap_id, beatmap_set_id, mods, acc_95, acc_98, acc_100
    FROM scores
    WHERE acc_98 BETWEEN ? AND ?
    ORDER BY acc_98 DESC
    LIMIT 10
    """

    cursor.execute(query, (pp_min, pp_max))
    results = cursor.fetchall()
    conn.close()

    return results


def connect_to_db(db_name="osu_scores.db"):
    """Create a connection to the SQLite database and return the connection object."""
    return sqlite3.connect(db_name)

def create_table_if_not_exists(conn):
    """Create the table if it doesn't exist."""
    with conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                map_name TEXT NOT NULL,
                beatmap_set_id INTEGER,
                beatmap_id INTEGER,
                mods TEXT NOT NULL,
                unique_score_id TEXT NOT NULL UNIQUE,
                acc_95 FLOAT,
                acc_98 FLOAT,
                acc_100 FLOAT,
                updated_at DATETIME NOT NULL
            )
        ''')

def get_existing_unique_score_ids(conn):
    """Get all unique_score_id values from the database."""
    cursor = conn.cursor()
    cursor.execute('SELECT unique_score_id FROM scores')
    existing_ids = {row[0] for row in cursor.fetchall()}  # Use a set for fast lookups
    return existing_ids

def store_records_in_batch(records, update_existing=False):
    """Store multiple performance records in the database in a batch.
    
    Args:
        records (list): List of dicts containing performance data.
        update_existing (bool): If True, update existing records on conflict.
    """
    # Open a connection to the database
    conn = connect_to_db()

    # Create the table if it doesn't exist
    create_table_if_not_exists(conn)

    if update_existing:
        # UPSERT: insert or update if conflict on unique_score_id
        sql = '''
            INSERT INTO scores (
                map_name,
                beatmap_set_id,
                beatmap_id,
                mods,
                unique_score_id,
                acc_95,
                acc_98,
                acc_99,
                acc_100,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(unique_score_id) DO UPDATE SET
                map_name=excluded.map_name,
                beatmap_set_id=excluded.beatmap_set_id,
                beatmap_id=excluded.beatmap_id,
                mods=excluded.mods,
                acc_95=excluded.acc_95,
                acc_98=excluded.acc_98,
                acc_99=excluded.acc_99,
                acc_100=excluded.acc_100,
                updated_at=excluded.updated_at
        '''
    else:
        # Insert or ignore duplicates
        sql = '''
            INSERT OR IGNORE INTO scores (
                map_name,
                beatmap_set_id,
                beatmap_id,
                mods,
                unique_score_id,
                acc_95,
                acc_98,
                acc_99,
                acc_100,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

    # If not updating existing records, filter out duplicates ahead of time
    if not update_existing:
        existing_ids = get_existing_unique_score_ids(conn)
        records = [
            record for record in records if record['unique_score_id'] not in existing_ids
        ]

    if records:
        with conn:
            conn.executemany(sql, [
                (
                    record['map_name'],
                    record['beatmap_set_id'],
                    record['beatmap_id'],
                    record['mods'],
                    record['unique_score_id'],
                    record['acc_95'],
                    record['acc_98'],
                    record['acc_99'],
                    record['acc_100'],
                    record['updated_at']
                ) for record in records
            ])
        action = "Upserted" if update_existing else "Inserted"
        print(f"{action} {len(records)} records.")
    else:
        print("No new records to insert." if not update_existing else "No records provided.")

    # Close the connection
    conn.close()

def get_user_settings(username):
    conn = sqlite3.connect("osu_scores.db")
    cursor = conn.cursor()

    cursor.execute("SELECT banned_mods, acc_preference FROM user_settings WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row:
        return {
            "banned_mods": row[0].split(",") if row[0] else [],
            "acc_preference": row[1]
        }
    else:
        # Return default settings if none found
        return {
            "banned_mods": [],
            "acc_preference": "acc_98"
        }

def update_user_settings(username, banned_mods=None, acc_preference=None):
    conn = sqlite3.connect("osu_scores.db")
    cursor = conn.cursor()

    # Fetch existing settings
    cursor.execute("SELECT banned_mods, acc_preference FROM user_settings WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row:
        current_banned, current_acc = row
    else:
        current_banned, current_acc = "", "acc_98"

    # Use new values if provided, otherwise fallback to existing
    banned_mods_str = ",".join(banned_mods) if banned_mods is not None else current_banned
    acc_preference_str = acc_preference if acc_preference is not None else current_acc

    cursor.execute("""
        INSERT INTO user_settings (username, banned_mods, acc_preference)
        VALUES (?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET banned_mods = ?, acc_preference = ?
    """, (username, banned_mods_str, acc_preference_str, banned_mods_str, acc_preference_str))

    conn.commit()
    conn.close()

def get_recommendation(baseline_pp, acc_preference='acc_98', banned_mods=[]):
    conn = sqlite3.connect("osu_scores.db")
    cursor = conn.cursor()

    lower_bound = baseline_pp - 10
    upper_bound = baseline_pp + 10

    banned_mods = set(banned_mods)

    query = f"""
        SELECT map_name, beatmap_id, beatmap_set_id, mods, acc_95, acc_98, acc_99, acc_100
        FROM scores
        WHERE {acc_preference} BETWEEN ? AND ?
    """

    cursor.execute(query, (lower_bound, upper_bound))
    all_rows = cursor.fetchall()
    conn.close()

    # Filter maps with disallowed mods
    filtered = []
    for row in all_rows:
        mods = row[3].split('+') if row[3] else []
        if not banned_mods.intersection(mods):
            filtered.append(row)

    if not filtered:
        return None

    chosen = random.choice(filtered)
    return {
        "map_name": chosen[0],
        "beatmap_id": chosen[1],
        "beatmap_set_id": chosen[2],
        "mods": chosen[3],
        "acc_95": chosen[4],
        "acc_98": chosen[5],
        "acc_99": chosen[6],
        "acc_100": chosen[7]
    }

def execute_query(query, params=()):
    # Open a database connection
    conn = sqlite3.connect('osu_scores.db')
    cursor = conn.cursor()

    try:
        # Execute the query with parameters
        cursor.execute(query, params)
        conn.commit()
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
    finally:
        conn.close()