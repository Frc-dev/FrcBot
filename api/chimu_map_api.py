import requests
import os
from datetime import datetime

base_url = "https://catboy.best"
pp_calc_endpoint = "/d/{}"
rate_limit_endpoint = "/api/ratelimits"
log_dir = "logs"
log_file = os.path.join(log_dir, "rate_limit_log.txt")

def log_rate_limit_event(message):
    """Log rate limit event to a file with timestamp."""
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)  # Optional: also print to console

def check_rate_limits():
    """Check if we're within safe rate limits for downloads."""
    try:
        response = requests.get(base_url + rate_limit_endpoint)
        response.raise_for_status()
        limits = response.json()

        remaining_downloads = limits["remaining"]["download"]
        daily_remaining_downloads = limits["daily"]["remaining"]["downloads"]

        print(f"Remaining downloads: {remaining_downloads}")
        print(f"Daily remaining downloads: {daily_remaining_downloads}")

        if remaining_downloads <= 0:
            msg = "Download rate limit reached (short-term). Skipping download."
            log_rate_limit_event(msg)
            return False
        if daily_remaining_downloads <= 0:
            msg = "Download rate limit reached (daily limit). Skipping download."
            log_rate_limit_event(msg)
            return False

        return True

    except requests.RequestException as err:
        msg = f"Failed to check rate limits: {err}"
        log_rate_limit_event(msg)
        return False

def download_beatmap(beatmap_id):
    url = base_url + pp_calc_endpoint.format(beatmap_id)

    try:
        print(f"Requesting: {url}")
        response = requests.get(url)
        response.raise_for_status()

        output_dir = "downloads"
        os.makedirs(output_dir, exist_ok=True)

        file_path = os.path.join(output_dir, f"{beatmap_id}.zip")

        if os.path.exists(file_path):
            print(f"File {file_path} already exists. Skipping save.")
            return

        with open(file_path, "wb") as f:
            f.write(response.content)

        print(f"File saved to {file_path}")

    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Connection Error:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Request failed:", err)

def main():
    beatmap_id = input("Enter a beatmap ID: ").strip()

    if check_rate_limits():
        download_beatmap(beatmap_id)
    else:
        print("Aborting download due to rate limits.")

if __name__ == "__main__":
    main()
