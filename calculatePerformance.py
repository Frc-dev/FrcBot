import rosu_pp_py as rosu

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
