import os
import re
from collections import defaultdict

log_dir = "FrcBot/logs"
output_file = "user_metrics.txt"

log_line_re = re.compile(r"\[(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}\] User: ([^\s]+) - Message:")

users_per_month = defaultdict(set)

for filename in os.listdir(log_dir):
    if filename.endswith("_conversation_log.txt"):
        filepath = os.path.join(log_dir, filename)

        months_in_file = set()  # Track months this user appears in

        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                match = log_line_re.search(line)
                if match:
                    date_str, username = match.groups()
                    month = date_str[:7]
                    months_in_file.add(month)

        # Add user once per month they appear in this file
        # username is the same for all lines in the file, so just get from filename or from last match
        # Safer to extract from filename:
        username = filename.split("_conversation_log.txt")[0].lower().strip()
        for month in months_in_file:
            users_per_month[month].add(username)

with open(output_file, "w", encoding="utf-8") as out_f:
    for month, users in sorted(users_per_month.items()):
        out_f.write(f"{month}: {len(users)} unique users\n")
