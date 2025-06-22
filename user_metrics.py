import os
import re
from collections import defaultdict

log_dir = "logs/msg"
output_file = "user_metrics.txt"

log_line_re = re.compile(r"\[(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}\] User: ([^\s]+) - Message:")

users_per_month = defaultdict(set)
deleted_files = []

print(f"Scanning logs in: {log_dir}")

for filename in os.listdir(log_dir):
    if not filename.endswith("_conversation_log.txt"):
        continue

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

    username = filename.split("_conversation_log.txt")[0].lower().strip()
    for month in months_in_file:
        users_per_month[month].add(username)
        print(f"  ➕ Added user '{username}' to month {month}")

# Output user metrics
print("\nSummary of unique users per month:")
with open(output_file, "w", encoding="utf-8") as out_f:
    for month, users in sorted(users_per_month.items()):
        line = f"{month}: {len(users)} unique users"
        print(line)
        out_f.write(line + "\n")

print(f"\nUser metrics saved to: {output_file}")
