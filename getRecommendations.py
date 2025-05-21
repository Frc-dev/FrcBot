import sqlite3

DB_PATH = "osu_scores.db"

def get_recommendations(pp_baseline, acc_preference="98"):
    acc_column_map = {
        "95": "acc_95",
        "98": "acc_98",
        "100": "acc_100"
    }

    # Default to 98% if something goes wrong
    acc_column = acc_column_map.get(acc_preference, "acc_98")

    range_percentage = 0.03  # 3% range 
    # Calculate the actual range based on PP baseline
    range_delta = pp_baseline * range_percentage
    lower_bound = pp_baseline - range_delta
    upper_bound = pp_baseline + range_delta

    print(f"Lower: {lower_bound} Upper: {upper_bound}")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = f"""
        SELECT map_name, beatmap_id, beatmap_set_id, mods, acc_95, acc_98, acc_100
        FROM scores
        WHERE {acc_column} BETWEEN ? AND ?
        ORDER BY {acc_column} DESC
        """
        cursor.execute(query, (lower_bound, upper_bound))
        results = cursor.fetchall()

        conn.close()
        return results

    except Exception as e:
        print(f"Database error: {e}")
        return []
