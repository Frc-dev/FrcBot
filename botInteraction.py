import random, os, time
from datetime import datetime
from settingsHelper import update_banned_mods, update_acc_preference, get_user_settings, get_banned_mods, update_user_preference
from fetchTopScores import fetch_top_scores
from getRecommendations import get_recommendations
from constants import VALID_MODS, VALID_ACCURACIES  # Import constants

def get_beatmap_url(beatmap_id):
    return f"https://osu.ppy.sh/beatmaps/{beatmap_id}"

def handle_recommendation_command(username):
    # Get user settings (banned mods and accuracy preference)
    banned_mods, acc_pref, fake_user = get_user_settings(username)

    if fake_user:
        username = fake_user

    # Get top scores for the user
    top_scores = fetch_top_scores(username)
    if not top_scores or len(top_scores) < 10:
        # If not enough data, return the message instead of sending it
        reply = "Not enough data to generate recommendations."
        return reply

    # Extract the PP (Performance Points) of the last score
    pp = float(top_scores[-1].get("pp", 0))

    # Get all recommendations based on PP and accuracy preference
    all_recs = get_recommendations(pp, acc_pref)
    
    # Filter out recommendations based on banned mods
    filtered = [rec for rec in all_recs if rec[3] not in banned_mods]

    # Check if there are any valid recommendations
    if filtered:
        # Select a random recommendation
        chosen = random.choice(filtered)
        map_name, mods, acc_95_pp, acc_98_pp, acc_100_pp = chosen[0], chosen[3], int(chosen[4]), int(chosen[5]), int(chosen[6])
        url = get_beatmap_url(chosen[1])
        
        # Store the message in the reply variable
        reply = f"[{url} {map_name}] | {mods} | 95%: {acc_95_pp}pp, 98%: {acc_98_pp}pp, 100%: {acc_100_pp}pp"
    else:
        # If no valid recommendations, store the message in the reply variable
        reply = "No maps found in that PP range that match your preferences."
    
    return reply

def handle_settings_command(username, args):
    banned_mods, acc_pref, fake_user = get_user_settings(username)
    if not args:
        msg = f"Your settings: Banned Mods: {', '.join(banned_mods) if banned_mods else 'None'} | Accuracy Preference: {acc_pref}"
        if fake_user:
            msg += f" | User: {fake_user}"
        msg += f" | Usage: banned_mods acc_preference user"
        return msg

    setting = args[0]

    if setting == "banned_mods":
        if len(args) == 1:
            return f"Current banned mods: {', '.join(banned_mods) if banned_mods else 'None'}"
        else:
            # Join arguments and clean input
            raw_input = ' '.join(args[1:]).replace('[', '').replace(']', '')
            new_banned_mods = [mod.strip() for mod in raw_input.split(',') if mod.strip()]

            # Fallback if input wasn't comma-separated
            if len(new_banned_mods) == 1 and ' ' in new_banned_mods[0]:
                new_banned_mods = new_banned_mods[0].split()

            success, invalid = update_banned_mods(username, new_banned_mods)
            updated_mods = get_banned_mods(username)

            reply = f"Updated banned mods: {', '.join(sorted(updated_mods)) if updated_mods else 'None'}"
            if invalid:
                reply += f" | Ignored invalid mods: {', '.join(invalid)} | Valid mods: {', '.join(VALID_MODS)}"
            return reply
        
    elif setting == "acc_preference":
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

    else:
        return "Unknown !settings command. Options: banned_mods, acc_preference"

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

def handle_playing_command(username, args):
    