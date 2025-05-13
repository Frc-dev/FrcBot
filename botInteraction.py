import random
from settingsHelper import update_banned_mods, update_acc_preference, get_user_settings
from fetchTopScores import fetch_top_scores
from getRecommendations import get_recommendations
from constants import VALID_MODS, VALID_ACCURACIES  # Import constants

def get_beatmap_url(beatmap_id):
    return f"https://osu.ppy.sh/beatmaps/{beatmap_id}"

def handle_recommendation_command(interface, username):
    top_scores = fetch_top_scores(username)
    if not top_scores or len(top_scores) < 10:
        interface.send(username, "Not enough data to generate recommendations.")
        return

    pp = float(top_scores[-1].get("pp", 0))
    banned_mods, acc_pref = get_user_settings(username)
    all_recs = get_recommendations(pp, acc_pref)
    filtered = [rec for rec in all_recs if rec[3] not in banned_mods]

    if filtered:
        chosen = random.choice(filtered)
        map_name, mods, acc_95_pp, acc_98_pp, acc_100_pp = chosen[0], chosen[3], int(chosen[4]), int(chosen[5]), int(chosen[6])
        url = get_beatmap_url(chosen[1])
        interface.send(username, f"[{url} {map_name}] | {mods} | 95%: {acc_95_pp}pp, 98%: {acc_98_pp}pp, 100%: {acc_100_pp}pp")
    else:
        interface.send(username, "No maps found in that PP range that match your preferences.")

def handle_settings_command(interface, username, args):
    if not args:
        banned_mods, acc_pref = get_user_settings(username)
        interface.send(username, f"Your settings:\n  Banned Mods: {', '.join(banned_mods) if banned_mods else 'None'}\n  Accuracy Preference: {acc_pref}")
        return

    if args[0] == "banned_mods":
        if len(args) == 1:
            banned_mods, _ = get_user_settings(username)
            interface.send(username, f"Current banned mods: {', '.join(banned_mods) if banned_mods else 'None'}")
        else:
            success, invalid = update_banned_mods(username, args[1:])
            if success:
                interface.send(username, f"Updated banned mods: {', '.join(args[1:])}")
            else:
                interface.send(username, f"Invalid mods: {', '.join(invalid)}\nValid mods: {', '.join(VALID_MODS)}")

    elif args[0] == "acc_preference":
        if len(args) == 2 and args[1] in VALID_ACCURACIES:
            result = update_acc_preference(username, args[1])
            interface.send(username, f"Updated accuracy preference to {args[1]}" if result else "Error updating accuracy preference.")
        else:
            interface.send(username, f"Valid accuracy values: {', '.join(VALID_ACCURACIES)}")
    else:
        interface.send(username, "Unknown !settings command. Options: banned_mods, acc_preference")