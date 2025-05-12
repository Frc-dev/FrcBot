import sqlite3

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

def store_records_in_batch(records):
    """Store multiple performance records in the database in a batch."""
    # Open a connection to the database
    conn = connect_to_db()

    # Create the table if it doesn't exist
    create_table_if_not_exists(conn)

    # Get existing unique_score_ids in the database
    existing_ids = get_existing_unique_score_ids(conn)
    
    # Prepare the SQL statement for batch insertion
    sql = '''
        INSERT OR IGNORE INTO scores (
            map_name,
            beatmap_set_id,
            beatmap_id,
            mods,
            unique_score_id,
            acc_95,
            acc_98,
            acc_100,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    
    # Filter out records that already exist
    filtered_records = [
        record for record in records if record['unique_score_id'] not in existing_ids
    ]
    
    if filtered_records:
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
                    record['acc_100'],
                    record['updated_at']
                ) for record in filtered_records
            ])
        print(f"Inserted {len(filtered_records)} records.")
    else:
        print("No new records to insert.")
    
    # Close the connection
    conn.close()
