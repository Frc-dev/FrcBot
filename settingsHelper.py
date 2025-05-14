import sqlite3
from constants import VALID_MODS, VALID_ACCURACIES
from databaseHelper import execute_query

DB_PATH = "osu_scores.db"

def create_db():
    """Create the database and the user_settings table if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_settings (
        username TEXT PRIMARY KEY,
        banned_mods TEXT,
        acc_preference TEXT
    )
    """)
    
    conn.commit()
    conn.close()

def get_user_settings(username):
    """Retrieve user settings from the database"""
    query = "SELECT banned_mods, acc_preference FROM user_settings WHERE username = ?"
    result = execute_query(query, (username,))

    if result:
        banned_mods = result[0][0].split(',') if result[0][0] else []
        acc_preference = result[0][1]
        return banned_mods, acc_preference
    else:
        return [], "98"  # Default banned_mods and acc_preference if no settings are found

def get_banned_mods(username):
    """Retrieve banned mods for a user"""
    query = "SELECT banned_mods FROM user_settings WHERE username = ?"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0].split(",")  # Assuming banned_mods are stored as a comma-separated list
    return []  # Default empty list for banned mods

def update_banned_mods(username, new_banned_mods):
    """Update the banned mods for a user. Adds/removes valid mods, ignores duplicates and warns about invalid ones."""

    print(f"{username}: {new_banned_mods}")

    # Normalize input
    if isinstance(new_banned_mods, str):
        new_banned_mods = [mod.strip().upper() for mod in new_banned_mods.split(',')]
    elif isinstance(new_banned_mods, list):
        new_banned_mods = [mod.strip().upper() for mod in new_banned_mods]
    else:
        raise ValueError("new_banned_mods should be a string or list.")

    # Separate valid and invalid mods
    valid_mods = [mod for mod in new_banned_mods if mod in VALID_MODS]
    invalid_mods = [mod for mod in new_banned_mods if mod not in VALID_MODS]

    # Remove duplicates
    valid_mods = list(set(valid_mods))

    # Load current mods
    current_mods = set(get_banned_mods(username))

    # Toggle logic
    for mod in valid_mods:
        if mod in current_mods:
            current_mods.remove(mod)
        else:
            current_mods.add(mod)

    updated_mods = ",".join(sorted(current_mods))

    # Save to DB
    query = """
        INSERT INTO user_settings (username, banned_mods, acc_preference) 
        VALUES (?, ?, ?) 
        ON CONFLICT(username) DO UPDATE SET banned_mods = excluded.banned_mods
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (username, updated_mods, "",))  # acc_preference left blank if unknown
    conn.commit()
    conn.close()

    # Return success with invalids (for messaging)
    return True, invalid_mods

def update_acc_preference(username, acc_preference):
    """Update the accuracy preference for a user"""
    if acc_preference not in VALID_ACCURACIES:
        return False  # Return False if the accuracy preference is invalid

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if the user exists in the table
    cursor.execute("SELECT username FROM user_settings WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    # If the user doesn't exist, create a new record with default banned_mods and the given acc_preference
    if not result:
        cursor.execute("""
        INSERT INTO user_settings (username, banned_mods, acc_preference)
        VALUES (?, ?, ?)
        """, (username, "", acc_preference))  # Empty banned_mods for the new user
    
    # If the user exists, update the acc_preference
    else:
        cursor.execute("""
        UPDATE user_settings 
        SET acc_preference = ? 
        WHERE username = ?
        """, (acc_preference, username))
    
    conn.commit()
    conn.close()
    return True
