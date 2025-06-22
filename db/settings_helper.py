import sqlite3, os
from constants import VALID_MODS, VALID_ACCURACIES, VALID_ALGO
from FrcBot.db.database_helper import execute_query
from ossapi import Ossapi
from dotenv import load_dotenv

load_dotenv()

OSU_CLIENT_ID = os.getenv("OSU_CLIENT_ID")
OSU_CLIENT_SECRET = os.getenv("OSU_CLIENT_SECRET")
DB_PATH = "osu_scores.db"
api = Ossapi(OSU_CLIENT_ID, OSU_CLIENT_SECRET)

def create_db():
    """Create the database and the user_settings table if they don't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_settings (
        username TEXT PRIMARY KEY,
        banned_mods TEXT DEFAULT "HRDT,HDHRDT",
        acc_preference TEXT DEFAULT "98",
        fake_user INTEGER
    )
    """)
    
    conn.commit()
    conn.close()

def get_user_settings(username):
    """Retrieve user settings from the database"""
    query = "SELECT banned_mods, acc_preference, fake_user, algo FROM user_settings WHERE username = ?"
    result = execute_query(query, (username,))

    if result:
        banned_mods = result[0][0].split(',') if result[0][0] else []
        acc_preference = result[0][1]
        fake_user_id = result[0][2]
        algo = result[0][3]

        if fake_user_id is not None:
            user = api.user(int(fake_user_id)).username
        else:
            user = ""

        return banned_mods, acc_preference, user, algo
    else:
        query = """
            INSERT INTO user_settings (username) VALUES (?) 
        """
        result = execute_query(query, (username,))
        return get_user_settings(username)

def get_banned_mods(username):
    """Retrieve banned mods for a user"""
    query = "SELECT banned_mods FROM user_settings WHERE username = ?"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return [mod for mod in result[0].split(",") if mod]
    return []  # Default empty list for banned mods

import sqlite3

def update_banned_mods(username, new_banned_mods):
    """Update the banned mods for a user. Adds/removes valid mods, ignores duplicates and warns about invalid ones."""

    # Normalize input to uppercase strings
    if isinstance(new_banned_mods, str):
        new_banned_mods = [mod.strip().upper() for mod in new_banned_mods.split(',')]
    elif isinstance(new_banned_mods, list):
        new_banned_mods = [mod.strip().upper() for mod in new_banned_mods]
    else:
        raise ValueError("new_banned_mods should be a string or list.")

    normalized_mods = []
    invalid_mods = []

    # Normalize each mod against VALID_MODS keys and variants
    for mod in new_banned_mods:
        matched = None
        for key, variants in VALID_MODS.items():
            if mod in variants:
                matched = key
                break
        if matched:
            normalized_mods.append(matched)
        else:
            invalid_mods.append(mod)

    # Remove duplicates
    normalized_mods = list(set(normalized_mods))

    # Load current mods from DB or storage
    current_mods = set(get_banned_mods(username))

    # Toggle mods in current_mods set
    for mod in normalized_mods:
        if mod in current_mods:
            current_mods.remove(mod)
        else:
            current_mods.add(mod)

    updated_mods = ",".join(sorted(current_mods))

    # Save updated mods to DB
    query = """
        INSERT INTO user_settings (username, banned_mods) 
        VALUES (?, ?) 
        ON CONFLICT(username) DO UPDATE SET banned_mods = excluded.banned_mods
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (username, updated_mods))
    conn.commit()
    conn.close()

    # Return success flag and list of invalid mods for messaging
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
        INSERT INTO user_settings (username, acc_preference)
        VALUES (?, ?)
        """, (username, acc_preference))  # Empty banned_mods for the new user
    
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

def update_user_preference(fake_user, username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if the user exists
    cursor.execute("SELECT username FROM user_settings WHERE username = ?", (username,))
    result = cursor.fetchone()

    # If fake_user is 0, None, or empty string, clear the field
    if not fake_user or fake_user == "0":
        if result:
            cursor.execute("""
                UPDATE user_settings 
                SET fake_user = NULL 
                WHERE username = ?
            """, (username,))
        else:
            cursor.execute("""
                INSERT INTO user_settings (username, fake_user)
                VALUES (?, NULL)
            """, (username,))
    else:
        # Otherwise, look up the user and store their ID
        try:
            user = api.user(fake_user)
        except ValueError:
            conn.close()
            return False


        if result:
            cursor.execute("""
                UPDATE user_settings 
                SET fake_user = ? 
                WHERE username = ?
            """, (user.id, username))
        else:
            cursor.execute("""
                INSERT INTO user_settings (username, fake_user)
                VALUES (?, ?)
            """, (username, user.id))

    conn.commit()
    conn.close()
    return True

def update_algo_preference(algo, username):
    """Update the accuracy preference for a user"""
    if algo not in VALID_ALGO:
        return False  # Return False if the algo is invalid

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if the user exists in the table
    cursor.execute("SELECT username FROM user_settings WHERE username = ?", (username,))
    result = cursor.fetchone()
    
    # If the user doesn't exist, create a new record
    if not result:
        cursor.execute("""
        INSERT INTO user_settings (username, algo)
        VALUES (?, ?)
        """, (username, algo))
    
    # If the user exists, update the algo
    else:
        cursor.execute("""
        UPDATE user_settings 
        SET algo = ? 
        WHERE username = ?
        """, (algo, username))
    
    conn.commit()
    conn.close()
    return True