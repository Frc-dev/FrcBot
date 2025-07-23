import random, os, time, json
from datetime import datetime
from db.settings_helper import update_banned_mods, update_acc_preference, get_user_settings, get_banned_mods, update_user_preference, update_algo_preference, update_pp_preference
from api.fetch_top_scores import fetch_top_scores
from db.get_recommendations import get_recommendations
from constants import VALID_MODS, VALID_ACCURACIES  # Import constants
from session_manager import is_local_client

def normalize_mods(mod_str):
    if not mod_str:
        return None
    mod_str = mod_str.lower()
    for key, variants in VALID_MODS.items():
        if mod_str in {v.lower() for v in variants}:
            return key
    return None

def get_beatmap_url(beatmap_set_id, beatmap_id):
    """
    Returns a properly formatted osu! beatmap URL.
    Returns None if IDs are invalid and a link can't be constructed.
    """
    if not beatmap_set_id or beatmap_set_id <= 0:
        return None  # beatmap_set_id is required for the full link

    if not beatmap_id or beatmap_id <= 0:
        return f"https://osu.ppy.sh/beatmapsets/{beatmap_set_id}"

    return f"https://osu.ppy.sh/beatmapsets/{beatmap_set_id}#osu/{beatmap_id}"

def get_unique_local_recommendation(username, pp, acc_pref, rec_mods, filtered):
    import os
    import json

    range_percentage = 0.03
    range_delta = pp * range_percentage
    lower_bound = pp - range_delta
    upper_bound = pp + range_delta

    title = f"{int(lower_bound)}-{int(upper_bound)} | mods: {rec_mods or 'any'} | acc: {acc_pref}"
    json_path = f"{username}.json"

    shown_replies = set()
    if os.path.exists(json_path):
        with open(json_path, "r") as jf:
            try:
                data = json.load(jf)
                shown_replies = set(data.get(title, []))
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    all_replies = []

    for rec in filtered:
        map_name, mods = rec[0], rec[3]
        acc_95_pp, acc_98_pp, acc_100_pp = int(rec[4]), int(rec[5]), int(rec[6])
        beatmap_set_id, beatmap_id = rec[2], rec[1]

        url = get_beatmap_url(beatmap_set_id, beatmap_id)

        core_reply = (
            f"[{url} {map_name}]" if url else f"{map_name}"
        )
        core_reply += f" | {mods} | 95%: {acc_95_pp}pp, 98%: {acc_98_pp}pp, 100%: {acc_100_pp}pp"

        all_replies.append(core_reply)

    # Now filter them
    filtered_replies = [r for r in all_replies if r not in shown_replies]

    if not filtered_replies:
        return "All recommendations in your range and filters have already been shown. Try changing your settings or wait for new maps."

    final_reply = random.choice(filtered_replies)
    display_reply = f"{final_reply} | Collection: {title} | Remaining: {len(filtered_replies) - 1}"

    data.setdefault(title, []).append(final_reply)

    with open(json_path, "w") as jf:
        json.dump(data, jf, indent=4)

    return display_reply



def handle_recommendation_command(username, rec_mods=None):
    # Get user settings (banned mods and accuracy preference)
    banned_mods, acc_pref, fake_user, algo, pp_pref = get_user_settings(username)

    rec_mods = normalize_mods(rec_mods)

    if fake_user:
        username = fake_user

    # Get top scores for the user
    top_scores = fetch_top_scores(username)
    if not top_scores or len(top_scores) < 10:
        return "Not enough data to generate recommendations."

    # Extract the PP (Performance Points) of the last score
    pp = float(top_scores[-1].get("pp", 0))

    if pp_pref:
        try:
            pp = float(pp_pref)
        except ValueError:
            return "Invalid PP preference set in your settings."

    # Get all recommendations based on PP and accuracy preference
    all_recs = get_recommendations(pp, acc_pref, algo, rec_mods)

    # Filter out recommendations based on banned mods
    filtered = [rec for rec in all_recs if rec[3] not in banned_mods]

    # Check if there are any valid recommendations
    if not filtered:
        return "No maps found in your PP range that match your preferences. Check your settings."

    local = is_local_client(username)

    if local:
        return get_unique_local_recommendation(username, pp, acc_pref, rec_mods, filtered)

    # Standard IRC path — pick random recommendation, no deduplication
    rec = random.choice(filtered)
    map_name, mods = rec[0], rec[3]
    acc_95_pp, acc_98_pp, acc_100_pp = int(rec[4]), int(rec[5]), int(rec[6])
    beatmap_set_id, beatmap_id = rec[2], rec[1]
    url = get_beatmap_url(beatmap_set_id, beatmap_id)

    if url:
        reply = f"[{url} {map_name}] | {mods} | 95%: {acc_95_pp}pp, 98%: {acc_98_pp}pp, 100%: {acc_100_pp}pp"
    else:
        reply = f"{map_name} | {mods} | 95%: {acc_95_pp}pp, 98%: {acc_98_pp}pp, 100%: {acc_100_pp}pp | (Download not available)"

    return reply

def handle_settings_command(username, args):
    banned_mods, acc_pref, fake_user, algo, pp_pref = get_user_settings(username)
    if not args:
        msg = f"Your settings: Banned Mods: {', '.join(banned_mods) if banned_mods else 'None'} | Accuracy Preference: {acc_pref} | Algorithm: {algo} | PP Preference: {'No' if not pp_pref or int(pp_pref) == 0 else pp_pref}"
        if fake_user:
            msg += f" | User: {fake_user}"
        msg += f" | Usage: mods acc user algo"
        return msg

    setting = args[0]

    if setting == "mods":
        if len(args) == 1:
            return f"Current banned mods: {', '.join(banned_mods) if banned_mods else 'None'}"
        else:
            # Join arguments and clean input
            raw_input = ' '.join(args[1:]).replace('[', '').replace(']', '')
            # Split on commas or spaces to handle both "DT HD" and "DT,HD"
            potential_mods = []
            for part in raw_input.split(','):
                potential_mods.extend(part.strip().split())

            normalized_mods = []
            invalid_mods = []

            for mod in potential_mods:
                mod_upper = mod.upper()
                # Find the key in VALID_MODS whose value set includes the mod_upper
                matched = None
                for key, variants in VALID_MODS.items():
                    if mod_upper in variants:
                        matched = key
                        break
                if matched:
                    normalized_mods.append(matched)
                else:
                    invalid_mods.append(mod)

            success, invalid = update_banned_mods(username, normalized_mods)
            updated_mods = get_banned_mods(username)

            reply = f"Updated banned mods: {', '.join(sorted(updated_mods)) if updated_mods else 'None'}"
            if invalid_mods or invalid:
                all_invalid = invalid_mods + invalid
                reply += f" | Ignored invalid mods: {', '.join(all_invalid)} | Valid mods: {', '.join(VALID_MODS)}"
            return reply

    elif setting == "acc":
        if len(args) == 2 and args[1] in VALID_ACCURACIES:
            result = update_acc_preference(username, args[1])
            return f"Updated accuracy preference to {args[1]}" if result else "Error updating accuracy preference."
        else:
            return f"Valid accuracy values: {', '.join(VALID_ACCURACIES)}"

    elif setting == "user":
        if len(args) == 1:
            return f"!settings user [username|user_id] to receive the recommendations as if you were that user. !settings user 0 to remove it"
        else:
            target = " ".join(args[1:])
            result = update_user_preference(target, username)
            return f"Updated user" if result else "Error fetching user."
        
    elif setting == "algo":
        if len(args) == 1:
            return f"!settings algo [farm|all] to change the bots algorithm, farm is the default and your classic farming companion, all will also give you very underweighted maps and is not suitable for farming"
        else:
            target = " ".join(args[1:])
            result = update_algo_preference(target, username)
            return f"Updated algorithm" if result else "Error fetching user."
        
    elif setting == "pp":
        if len(args) == 1:
            return f"Use !settings pp [value] to change the PP preference when getting recommendations. Set to 0 to disable."
        else:
            try:
                new_pp_pref = int(args[1])
                if new_pp_pref < 0:
                    return "PP preference must be a non-negative integer."
                update_pp_preference(new_pp_pref, username)
                return f"Updated PP preference to {new_pp_pref}."
            except ValueError:
                return "Invalid PP preference value. Please provide a valid integer."

    else:
        return "Unknown !settings command. Options: mods, acc, user, algo, pp"

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs", "feedback")
LOG_FILE = os.path.join(LOG_DIR, "feedback.txt")

def handle_feedback_command(username, args):
    # Ensure feedback directory exists
    os.makedirs(LOG_DIR, exist_ok=True)

    if not args:
        # No feedback provided
        return "Use !feedback <your message> to report bugs or provide suggestions to me directly. I promise I will read it."
    
    # Join everything after !feedback into one string
    message = " ".join(args).strip()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Append to file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {username}: {message}\n")

    return "Thanks for your feedback!"

user_sessions = {}
def start_np_session(username, map_info):
    user_sessions[username] = {
        "map_info": map_info,
        "timestamp": time.time()
    }

def get_valid_session(username):
    session = user_sessions.get(username)
    if session and (time.time() - session["timestamp"] <= 300):
        # Refresh timestamp to extend session
        session["timestamp"] = time.time()
        return session
    # Expire and clean up stale session
    user_sessions.pop(username, None)
    return None
