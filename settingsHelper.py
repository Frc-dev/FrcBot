# settingsHelper.py
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
    # Assuming you have a method to retrieve from your database
    # The result will contain a tuple or dictionary with banned_mods and acc_preference
    query = "SELECT banned_mods, acc_preference FROM user_settings WHERE username = ?"
    result = execute_query(query, (username,))

    if result:
        banned_mods = result[0][0].split(',') if result[0][0] else []
        acc_preference = result[0][1]
        return banned_mods, acc_preference
    else:
        return [], "98"  # Default banned_mods and acc_preference if no settings are found

# settingsHelper.py

import sqlite3
from constants import VALID_MODS  # Import the constants for valid mods

# Database file path
DB_PATH = 'osu_scores.db'

# Function to get the banned mods for a user
def get_banned_mods(username):
    query = "SELECT banned_mods FROM user_settings WHERE username = ?"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return result[0].split(",")  # Assuming banned_mods are stored as a comma-separated list
    return []

def update_banned_mods(username, new_banned_mods):
    # Ensure new_banned_mods is a list
    if isinstance(new_banned_mods, str):
        new_banned_mods = [mod.strip() for mod in new_banned_mods.split(',')]
    elif not isinstance(new_banned_mods, list):
        raise ValueError("new_banned_mods should be either a string or a list.")

    # Validate mods
    invalid_mods = [mod for mod in new_banned_mods if mod not in VALID_MODS]
    if invalid_mods:
        return False, invalid_mods

    # Get current mods
    current_mods = get_banned_mods(username)

    # Toggle behavior: add if not in list, remove if in list
    updated_mods = set(current_mods)
    for mod in new_banned_mods:
        if mod in updated_mods:
            updated_mods.remove(mod)
        else:
            updated_mods.add(mod)

    # Save to DB
    query = "UPDATE user_settings SET banned_mods = ? WHERE username = ?"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (",".join(sorted(updated_mods)), username))
    conn.commit()
    conn.close()

    return True, []


def update_acc_preference(username, acc_preference):
    """Update the accuracy preference for a user in the database"""
    if acc_preference not in VALID_ACCURACIES:
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO user_settings (username, banned_mods, acc_preference)
    VALUES (?, ?, ?)
    ON CONFLICT(username) 
    DO UPDATE SET acc_preference = ?;
    """, (username, "", acc_preference, acc_preference))
    
    conn.commit()
    conn.close()
    return True

