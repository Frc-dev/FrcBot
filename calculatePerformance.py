import rosu_pp_py as rosu
import requests
import tempfile
import os

def calculate_performance(map_path=None, existingMap=None, accuracy=100.0, mods=0, game_mode=rosu.GameMode.Osu):
    if existingMap is None:
        if map_path is None:
            raise ValueError("Either map_path or existingMap must be provided.")
        map = rosu.Beatmap(path=map_path)
        
        # Skip if the map isn't standard osu!
        if map.mode != rosu.GameMode.Osu:
            raise ValueError(f"Skipping non-std map: {map_path} (Mode: {map.mode})")

        map.convert(game_mode)
    else:
        map = existingMap

    perf = rosu.Performance(
        accuracy=accuracy,
        mods=mods
    )

    attrs = perf.calculate(map)

    return {
        'map': map,
        'performance': attrs.pp
    }

# --- CONFIG: replace with your osu! app credentials ---
OSU_CLIENT_ID = os.getenv("OSU_CLIENT_ID")
OSU_CLIENT_SECRET = os.getenv("OSU_CLIENT_SECRET")

# OAuth token URL and API base
TOKEN_URL = "https://osu.ppy.sh/oauth/token"
API_BASE = "https://osu.ppy.sh/api/v2"

def get_oauth_token(client_id, client_secret):
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": "public"
    }
    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_beatmap_info(token, beatmap_id):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = f"{API_BASE}/beatmaps/{beatmap_id}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def download_osu_file_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def calculate_pp_from_beatmap_content(osu_content, accuracy=100.0, mods=0):
    with tempfile.NamedTemporaryFile("w+", suffix=".osu", delete=True) as tmpfile:
        tmpfile.write(osu_content)
        tmpfile.flush()

        beatmap = rosu.Beatmap(path=tmpfile.name)
        if beatmap.mode != rosu.GameMode.Osu:
            print(f"Skipping non-standard osu! mode: {beatmap.mode}")
            return None
        beatmap.convert(rosu.GameMode.Osu)

        perf = rosu.Performance(accuracy=accuracy, mods=mods)
        result = perf.calculate(beatmap)
        return result.pp

def main():
    print('running this')
    # Example beatmap_id and mods
    beatmap_id = 378205
    accuracy = 98.0
    mods = 8  # HD

    # Get OAuth token
    token = get_oauth_token(OSU_CLIENT_ID, OSU_CLIENT_SECRET)
    print("Got OAuth token")

    # Get beatmap info
    beatmap_info = get_beatmap_info(token, beatmap_id)
    print(f"Got beatmap info: {beatmap_info['version']} by {beatmap_info['creator']}")

    # The beatmap info contains a 'url' field to download the .osu file
    osu_file_url = beatmap_info.get('url')
    if not osu_file_url:
        print("Beatmap download URL not found in response")
        return

    osu_content = download_osu_file_from_url(osu_file_url)
    print("Downloaded .osu file content")

    # Calculate performance points
    pp = calculate_pp_from_beatmap_content(osu_content, accuracy=accuracy, mods=mods)
    if pp is not None:
        print(f"PP for beatmap {beatmap_id} with mods {mods} at {accuracy}%: {pp:.2f}")

if __name__ == "__main__":
    main()