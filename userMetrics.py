import os
import re
from collections import defaultdict

log_dir = "logs/msg"
log_line_re = re.compile(r"\[(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}\] User: ([^\s]+) - Message:")

users_per_month = defaultdict(set)

for filename in os.listdir(log_dir):
    if filename.endswith("_conversation_log.txt"):
        filepath = os.path.join(log_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                match = log_line_re.search(line)
                if match:
                    date_str, username = match.groups()
                    month = date_str[:7]
                    users_per_month[month].add(username.lower().strip())  # normalize username

with open("user_metrics.txt", "w", encoding="utf-8") as out_f:
    for month, users in sorted(users_per_month.items()):
        out_f.write(f"{month}: {len(users)} unique users\n")
