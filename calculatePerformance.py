import rosu_pp_py as rosu

def calculate_performance(map_path=None, existingMap=None, accuracy=100.0, mods=0, game_mode=rosu.GameMode.Osu):
    """
    Calculate performance points (PP) and difficulty stars for a given osu! beatmap.
    
    Parameters:
    - map_path (str): Path to the .osu file (only used if no existing map is passed)
    - existingMap (rosu.Beatmap): An existing `rosu.Beatmap` object (optional)
    - accuracy (float): Accuracy of the player (default 100.0)
    - misses (int): Number of misses (default 0)
    - mods (int): Mods applied to the map (default 0)
    - game_mode (rosu.GameMode): Game mode (default osu!)

    Returns:
    - dict: Contains PP and Stars values
    """
    # Load a new beatmap if an existing one isn't provided
    if existingMap is None:
        if map_path is None:
            raise ValueError("Either map_path or existingMap must be provided.")
        map = rosu.Beatmap(path=map_path)
        map.convert(game_mode)
    else:
        map = existingMap


    # Set the performance parameters
    perf = rosu.Performance(
        accuracy=accuracy,
        mods=mods
    )

    # Calculate for the map
    attrs = perf.calculate(map)

    return {
        'map': map,
        'performance': attrs.pp
    }
