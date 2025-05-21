import os
import datetime
from getMapInfo import OsuParser
from calculatePerformance import calculate_performance
from databaseHelper import store_records_in_batch
from dotenv import load_dotenv

load_dotenv()

def insert_data_on_demand(mapList):
    


def main():
    # Path to the root directory where your osu! maps are stored
    root_dir = os.getenv("SONGS_ROOT_DIR")
    
    # Initialize the OsuParser with the root directory
    osu_parser = OsuParser(root_dir)
    
    # Get metadata for the first 10 osu! files
    maps_metadata = osu_parser.get_first_n_osu_files()

    mods = {
        0: 'NM',
        8: 'HD',
        16: 'HR',
        64: 'DT'
    }

    modCombinations = [
        [0], [8], [16], [64],
        [8, 16], [8, 64], [16, 64],
        [8, 16, 64]
    ]

    accuracyCombinations = [95, 98, 100]

    processed = 0
    batch = 100

    # Initialize the list to store map results for future database insertions
    map_results = []  # Optional: collect for future use

    # Iterate over the maps metadata
    for metadata in maps_metadata:
        beatmap_id = metadata.get('BeatmapID')
        beatmap_set_id = metadata.get('BeatmapSetID')
        map_name = metadata.get('Map_Name')
        osu_file_path = os.path.join(root_dir, metadata.get('Osu_File_Path'))

        print(f"\nProcessing map: {map_name}")
        print(f"BeatmapID: {beatmap_id}, BeatmapSetID: {beatmap_set_id}")
        print(f"File Path: {osu_file_path}")

        try:
            parsed_map = calculate_performance(map_path=osu_file_path)['map']
        except ValueError as e:
            print(f"Skipping map due to error: {e}")
            continue

        # Iterate over mod combinations
        for mod_combo in modCombinations:
            total_mod_value = sum(mod_combo)
            readable_mods = '+'.join([mods[m] for m in mod_combo if m != 0]) or 'NM'
            unique_score_id = f"{beatmap_set_id}_{beatmap_id}_{readable_mods or 'NM'}"
            acc_pp_map = {}

            # Iterate over accuracy combinations and calculate PP
            for acc in accuracyCombinations:
                result = calculate_performance(
                    existingMap=parsed_map,
                    accuracy=acc,
                    mods=total_mod_value
                )
                acc_pp_map[acc] = result['performance']

            # Prepare the record to be inserted into the database
            record = {
                "map_name": map_name,
                "beatmap_set_id": int(beatmap_set_id) if beatmap_set_id else None,
                "beatmap_id": int(beatmap_id) if beatmap_id and beatmap_id.isdigit() else None,
                "mods": readable_mods,
                "unique_score_id": unique_score_id,
                "acc_95": acc_pp_map.get(95),
                "acc_98": acc_pp_map.get(98),
                "acc_100": acc_pp_map.get(100),
                "updated_at": datetime.datetime.now().isoformat()
            }

            map_results.append(record)  # Store it for future DB insertion
            processed += 1

            # If batch size is reached, store records and reset the batch
            if processed >= batch:
                store_records_in_batch(map_results)
                processed = 0
                map_results = []

    # Ensure remaining records are stored if any (after the loop ends)
    if map_results:
        store_records_in_batch(map_results)

if __name__ == "__main__":
    main()
