import requests
import csv
import json
from datetime import datetime
from constants import NUMERICAL_MODS

CSV_URL = "https://raw.githubusercontent.com/grumd/osu-pps/refs/heads/data/data/maps/osu/diffs.csv"
JSON_OUTPUT = "farm_maps.json"

def fetch_csv():
    response = requests.get(CSV_URL)
    response.raise_for_status()
    return response.text

def parse_entries(csv_data):
    reader = csv.DictReader(csv_data.splitlines())
    entries = []
    for row in reader:
        m = int(row["m"])
        if m in NUMERICAL_MODS:
            entries.append({
                "mods": m,
                "beatmap_id": int(row["b"]),
                "beatmap_set_id": int(row["s"])
            })
    return entries

def save_json(data):
    with open(JSON_OUTPUT, "w") as f:
        json.dump({
            "updated_at": datetime.utcnow().isoformat(),
            "maps": data
        }, f, indent=2)

def main():
    csv_data = fetch_csv()
    entries = parse_entries(csv_data)
    save_json(entries)

if __name__ == "__main__":
    main()
