import os
import re
from collections import defaultdict

log_dir = "logs/msg"
output_file = "user_metrics.txt"

log_line_re = re.compile(r"\[(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}\] User: ([^\s]+) - Message:")

users_per_month = defaultdict(set)

print(f"Looking in folder: {log_dir}")

try:
    files = os.listdir(log_dir)
    print(f"Files found: {files}")
except Exception as e:
    print(f"Error listing directory: {e}")
    exit(1)

for filename in files:
    if filename.endswith("_conversation_log.txt"):
        filepath = os.path.join(log_dir, filename)
        print(f"Processing file: {filename}")
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                match = log_line_re.search(line)
                if match:
                    date_str, username = match.groups()
                    print(f"Found user: {username} at date: {date_str}")
                    month = date_str[:7]
                    users_per_month[month].add(username.lower().strip())

with open(output_file, "w", encoding="utf-8") as out_f:
    for month, users in sorted(users_per_month.items()):
        out_f.write(f"{month}: {len(users)} unique users\n")

print(f"User metrics saved to {output_file}")
