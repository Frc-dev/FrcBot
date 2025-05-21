import requests
import csv
import json
from datetime import datetime

CSV_URL = "https://raw.githubusercontent.com/grumd/osu-pps/refs/heads/data/data/maps/osu/diffs.csv"
JSON_OUTPUT = "farm_maps.json"

MODS = {
    0: 'NM',
    8: 'HD',
    16: 'HR',
    64: 'DT',
    72: 'HDDT',
    24: 'HDHR',
    80: 'HRDT',
    88: 'HDHRDT',
}

def fetch_csv():
    response = requests.get(CSV_URL)
    response.raise_for_status()
    return response.text

def parse_entries(csv_data):
    reader = csv.DictReader(csv_data.splitlines())
    entries = []
    for row in reader:
        m = int(row["m"])
        if m in MODS:
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
