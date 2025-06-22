import os
import re

class OsuParser:
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def extract_metadata_from_file(self, file_path, fallback_set_id):
        artist = title = version = None
        beatmap_id = None
        beatmapset_id = fallback_set_id

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        inside_metadata = False
        for line in lines:
            line = line.strip()
            if line == "[Metadata]":
                inside_metadata = True
                continue
            elif line.startswith("[") and inside_metadata:
                break

            if inside_metadata:
                if line.startswith("Title:"):
                    title = line.split("Title:", 1)[1].strip()
                elif line.startswith("Artist:"):
                    artist = line.split("Artist:", 1)[1].strip()
                elif line.startswith("Version:"):
                    version = line.split("Version:", 1)[1].strip()

            if line.startswith("BeatmapID:"):
                beatmap_id = line.split("BeatmapID:", 1)[1].strip()
            elif line.startswith("BeatmapSetID:"):
                beatmapset_id = line.split("BeatmapSetID:", 1)[1].strip()

        # If BeatmapID or BeatmapSetID is missing, we attempt to use fallback logic
        if not beatmap_id and version:
            beatmap_id = version  # If no BeatmapID, set BeatmapID to Version
        if not beatmapset_id and title:
            # Extract the first set of numbers (digits) from the title to be the BeatmapSetID
            match = re.match(r'(\d+)', title)
            if match:
                beatmapset_id = match.group(1)  # Set the first set of numbers as BeatmapSetID

        map_name = None
        if artist and title and version:
            map_name = f"{artist} - {title} [{version}]"

        relative_path = os.path.relpath(file_path, start=self.root_dir)

        return {
            'BeatmapID': beatmap_id,
            'BeatmapSetID': beatmapset_id,
            'Map_Name': map_name,
            'Osu_File_Path': relative_path
        }

    def get_first_n_osu_files(self, limit=None):
        collected = 0
        results = []

        for folder_name in os.listdir(self.root_dir):
            folder_path = os.path.join(self.root_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue

            match = re.match(r"(\d+)", folder_name)
            fallback_set_id = match.group(1) if match else None

            for file_name in os.listdir(folder_path):
                if not file_name.endswith(".osu"):
                    continue

                file_path = os.path.join(folder_path, file_name)
                metadata = self.extract_metadata_from_file(file_path, fallback_set_id)
                results.append(metadata)

                collected += 1
                if limit and collected >= limit:
                    return results

        return results
