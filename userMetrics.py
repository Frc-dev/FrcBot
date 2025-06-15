import os
import re
from collections import defaultdict

log_dir = "logs/msg"
output_file = "user_metrics.txt"
#sorry
pattern_to_delete = "Message: type: quit"

log_line_re = re.compile(r"\[(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}\] User: ([^\s]+) - Message:")

users_per_month = defaultdict(set)

print(f"Scanning logs in: {log_dir}")

# Step 1: Delete files with 'type: quit'
deleted_files = []
for filename in os.listdir(log_dir):
    if filename.endswith("_conversation_log.txt"):
        filepath = os.path.join(log_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            if any(pattern_to_delete in line.lower() for line in f):
                os.remove(filepath)
                deleted_files.append(filename)
                print(f"Deleted file (contained spam): {filename}")

# Step 2: Process remaining files
for filename in os.listdir(log_dir):
    if filename.endswith("_conversation_log.txt"):
        filepath = os.path.join(log_dir, filename)
        print(f"Processing file: {filename}")

        months_in_file = set()

        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                match = log_line_re.search(line)
                if match:
                    date_str, _ = match.groups()
                    month = date_str[:7]
                    months_in_file.add(month)
                    print(f"  Found message on {date_str}")

        username_from_filename = filename.split("_conversation_log.txt")[0].lower().strip()
        print(f"  User in file: {username_from_filename}")
        for month in months_in_file:
            users_per_month[month].add(username_from_filename)
            print(f"    Adding user '{username_from_filename}' to month {month}")

# Step 3: Save metrics
print("\nSummary of unique users per month:")
with open(output_file, "w", encoding="utf-8") as out_f:
    for month, users in sorted(users_per_month.items()):
        line = f"{month}: {len(users)} unique users"
        print(line)
        out_f.write(line + "\n")

print(f"\n✅ User metrics saved to {output_file}")
print(f"🗑️  Total files deleted: {len(deleted_files)}")
