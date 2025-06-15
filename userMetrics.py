import os
import re
from collections import defaultdict

log_dir = "logs/msg"
output_file = "user_metrics.txt"

log_line_re = re.compile(r"\[(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}\] User: ([^\s]+) - Message:")

users_per_month = defaultdict(set)

print(f"Looking in folder: {log_dir}")
print(f"Files found: {os.listdir(log_dir)}")

for filename in os.listdir(log_dir):
    if filename.endswith("_conversation_log.txt"):
        filepath = os.path.join(log_dir, filename)
        print(f"Processing file: {filename}")
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                match = log_line_re.search(line)
                if match:
                    date_str, username = match.groups()
                    print(f"Matched line: Date={date_str}, User={username}")
                    month = date_str[:7]
                    users_per_month[month].add(username)

with open(output_file, "w", encoding="utf-8") as out_f:
    for month, users in sorted(users_per_month.items()):
        out_f.write(f"{month}: {len(users)} unique users\n")

print(f"User metrics saved to {output_file}")
