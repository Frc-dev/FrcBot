import json
import sqlite3
from insertData import insert_data_on_demand

FARM_JSON = "farm_maps.json"
DB_PATH = "osu_scores.db"

def load_farm_maps():
    with open(FARM_JSON, "r") as f:
        data = json.load(f)
        return data["maps"]

def mark_as_farm(conn, map_entry):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM scores
        WHERE beatmap_id = ? AND beatmap_set_id = ? AND mods = ?
    """, (map_entry["beatmap_id"], map_entry["beatmap_set_id"], map_entry["mods"]))
    
    result = cursor.fetchone()
    if result:
        cursor.execute("""
            UPDATE scores
            SET is_farm = 1
            WHERE id = ?
        """, (result[0],))
        print(f"Updated: {map_entry}")
        return True
    return False

def main():
    maps = load_farm_maps()
    unmatched_maps = []

    conn = sqlite3.connect(DB_PATH)

    for entry in maps:
        found = mark_as_farm(conn, entry)
        if not found:
            unmatched_maps.append(entry)

    conn.commit()
    conn.close()

    # You can now use unmatched_maps programmatically
    print(f"{len(unmatched_maps)} unmatched maps ready for insertion.")
    # For example:
    insert_data_on_demand(unmatched_maps)

if __name__ == "__main__":
    main()
