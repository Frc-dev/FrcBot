import json
import sqlite3
from constants import NUMERICAL_MODS  # Make sure constants.py is in the same directory

FARM_JSON = "farm_maps.json"
DB_PATH = "osu_scores.db"
UNMATCHED_JSON = "unmatched_maps.json"  # File to save unmatched maps

def load_farm_maps():
    with open(FARM_JSON, "r") as f:
        data = json.load(f)
        return data["maps"]

def get_mod_name(mod_value):
    return NUMERICAL_MODS.get(mod_value, f"Unknown({mod_value})")

def mark_as_farm(conn, map_entry):
    mod_name = get_mod_name(map_entry["mods"])
    print(f"Checking map: beatmap_id={map_entry['beatmap_id']}, beatmap_set_id={map_entry['beatmap_set_id']}, mods={mod_name}")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM scores
        WHERE beatmap_id = ? AND beatmap_set_id = ? AND mods = ?
    """, (map_entry["beatmap_id"], map_entry["beatmap_set_id"], mod_name))
    
    result = cursor.fetchone()
    if result:
        print(f"-> Match found: updating id={result[0]}")
        cursor.execute("""
            UPDATE scores
            SET is_farm = 1
            WHERE id = ?
        """, (result[0],))
        return True
    else:
        print("-> No match found.")
    return False

def main():
    maps = load_farm_maps()
    unmatched_maps = []

    conn = sqlite3.connect(DB_PATH)

    for i, entry in enumerate(maps):
        print(f"\nProcessing entry {i + 1}:")
        found = mark_as_farm(conn, entry)
        if not found:
            unmatched_maps.append(entry)

    conn.commit()
    conn.close()

    # Save unmatched maps to a JSON file
    with open(UNMATCHED_JSON, "w") as f:
        json.dump(unmatched_maps, f, indent=4)
    
    print(f"\n{len(unmatched_maps)} unmatched maps saved to {UNMATCHED_JSON}")

if __name__ == "__main__":
    main()
