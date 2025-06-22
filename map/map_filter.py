import json
import sqlite3
import re
from constants import DB_PATH

def load_user_file(username):
    filename = f"{username}.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return filename, json.load(f)
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        exit(1)

def parse_key(key):
    match = re.match(r"(\d+)-(\d+)\s+\|\s+mods:\s+(\w+)\s+\|\s+acc:\s+(\d+)", key)
    if not match:
        raise ValueError(f"Invalid key format: {key}")
    pp_min, pp_max, mods, acc = match.groups()
    return int(pp_min), int(pp_max), mods, int(acc)

def extract_ids(entry):
    match = re.search(r"beatmapsets/(\d+)#osu/(\d+)", entry)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def query_pp_from_db(conn, beatmap_set_id, beatmap_id, mods, acc):
    cursor = conn.cursor()
    acc_column = f"acc_{acc}"
    cursor.execute(f"""
        SELECT {acc_column} FROM scores
        WHERE beatmap_set_id = ? AND beatmap_id = ? AND mods = ?
    """, (beatmap_set_id, beatmap_id, mods))
    row = cursor.fetchone()
    return row[0] if row else None

def pick_key(keys, prompt="Select a key:"):
    for idx, key in enumerate(keys, 1):
        print(f"{idx}. {key}")
    while True:
        sel = input(f"{prompt} (1-{len(keys)}): ")
        if sel.isdigit() and 1 <= int(sel) <= len(keys):
            return keys[int(sel)-1]
        print("Invalid choice.")

def main():
    username = input("Enter username: ").strip()
    filename, data = load_user_file(username)
    keys = list(data.keys())
    if not keys:
        print("No keys in file."); return

    print("Source keys:")
    source_key = pick_key(keys, "Select source key")
    print("\nDestination keys:")
    dest_key   = pick_key(keys, "Select destination key")

    dst_pp_min, dst_pp_max, dst_mods, dst_acc = parse_key(dest_key)

    conn = sqlite3.connect(DB_PATH)
    matched = []

    print(f"\nChecking entries from '{source_key}' against '{dest_key}':")
    print(f" Mods={dst_mods}, Acc={dst_acc}, PP range={dst_pp_min}-{dst_pp_max}\n")

    for entry in data[source_key]:
        bsid, bid = extract_ids(entry)
        if bsid is None:
            print(f"❌ Skipping (no IDs): {entry}")
            continue

        pp = query_pp_from_db(conn, bsid, bid, dst_mods, dst_acc)
        pp_disp = f"{pp:.1f}" if isinstance(pp, (int,float)) else "–"
        in_range = pp is not None and dst_pp_min <= pp <= dst_pp_max

        status = "✅" if in_range else "❌"
        print(f"{status} {entry}")
        print(f"   → set:{bsid} map:{bid} mods:{dst_mods} acc:{dst_acc}% pp:{pp_disp}\n")

        if in_range:
            matched.append(entry)

    conn.close()

    if not matched:
        print("No entries matched the destination filters.")
        return

    # Append matched entries to destination key (avoid duplicates)
    dest_list = data[dest_key]
    added = 0
    for e in matched:
        if e not in dest_list:
            dest_list.append(e)
            added += 1

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"\nDone—added {added} entries to '{dest_key}' in {filename}.")

if __name__ == "__main__":
    main()
