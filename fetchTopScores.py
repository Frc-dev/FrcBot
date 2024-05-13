import json
import os
import datetime
import sqlite3
from ossapi import Ossapi
from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

OSU_CLIENT_ID = os.getenv("OSU_CLIENT_ID")
OSU_CLIENT_SECRET = os.getenv("OSU_CLIENT_SECRET")
DB_PATH = "osu_scores.db"

# Get top scores using v2 API
def fetch_top_scores(username):
    cache_file = os.path.join(CACHE_DIR, f"{username}.json")

    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)

        if cache_data.get('date') == datetime.datetime.now().strftime('%Y-%m-%d'):
            return cache_data.get('scores')

    api = Ossapi(OSU_CLIENT_ID, OSU_CLIENT_SECRET)
    user = api.user(username)
    if not user:
        print("Failed to get user.")
        return []

    scores = api.user_scores(user.id, 'best', mode='osu', limit=10)

    try:
        # Extract only serializable fields
        simplified_scores = [
            {
                'beatmap_id': score.beatmap.id,
                'pp': score.pp
            }
            for score in scores
        ]

        cache_data = {
            'date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'scores': simplified_scores
        }

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)

        return simplified_scores

    except Exception as e:
        print(f"Error fetching scores: {e}")
        return []

# Score-based recommendations from local DB
def get_recommendations(pp_baseline):
    percentage = 0.03
    lower_bound = pp_baseline * (1 - percentage)
    upper_bound = pp_baseline * (1 + percentage)

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = """
        SELECT map_name, beatmap_id, beatmap_set_id, mods, ROUND(acc_95), ROUND(acc_98), ROUND(acc_100)
        FROM scores
        WHERE acc_98 BETWEEN ? AND ?
        ORDER BY acc_98 DESC
        LIMIT 10;
        """
        cursor.execute(query, (lower_bound, upper_bound))
        results = cursor.fetchall()

        conn.close()
        return results

    except Exception as e:
        print(f"Database error: {e}")
        return []
