import random
from settingsHelper import update_banned_mods, update_acc_preference, get_user_settings
from fetchTopScores import fetch_top_scores
from getRecommendations import get_recommendations
from constants import VALID_MODS, VALID_ACCURACIES  # Import constants

def handle_recommendation_command(irc, username):
        top_scores = fetch_top_scores(username)
        if not top_scores or len(top_scores) < 10:
            irc.conn.privmsg(username, "Not enough data to generate recommendations.")
            return

        tenth_score = top_scores[-1]
        pp = float(tenth_score.get("pp", 0))

        banned_mods, acc_pref = get_user_settings(username)
        all_recs = get_recommendations(pp, acc_pref)

        filtered = [rec for rec in all_recs if rec[3] not in banned_mods]

        if filtered:
            chosen = random.choice(filtered)
            map_name = chosen[0]
            mods = chosen[3]
            acc_95_pp = int(chosen[4])
            acc_98_pp = int(chosen[5])
            acc_100_pp = int(chosen[6])

            irc.conn.privmsg(
                username,
                f"{map_name} | {mods} | 95%: {acc_95_pp}pp, 98%: {acc_98_pp}pp, 100%: {acc_100_pp}pp"
            )
        else:
            irc.conn.privmsg(username, "No maps found in that PP range that match your preferences.")

def handle_settings_command(irc, username, args):
    if not args:
        banned_mods, acc_pref = get_user_settings(username)
        irc.conn.privmsg(username, f"Your settings:")
        irc.conn.privmsg(username, f"  Banned Mods: {', '.join(banned_mods) if banned_mods else 'None'}")
        irc.conn.privmsg(username, f"  Accuracy Preference: {acc_pref}")
        return

    if args[0] == "banned_mods":
        if len(args) == 1:
            banned_mods, _ = get_user_settings(username)
            irc.conn.privmsg(username, f"Current banned mods: {', '.join(banned_mods) if banned_mods else 'None'}")
        else:
            new_banned = args[1:]
            success, invalid = update_banned_mods(username, new_banned)
            if success:
                irc.conn.privmsg(username, f"Updated banned mods: {', '.join(new_banned)}")
            else:
                irc.conn.privmsg(username, f"Valid mods: {', '.join(VALID_MODS)}")

    elif args[0] == "acc_preference":
        if len(args) == 2 and args[1] in VALID_ACCURACIES:
            result = update_acc_preference(username, args[1])
            if result:
                irc.conn.privmsg(username, f"Updated accuracy preference to {args[1]}")
            else:
                irc.conn.privmsg(username, "Error updating accuracy preference.")
        else:
            irc.conn.privmsg(username, f"Valid accuracy values: {', '.join(VALID_ACCURACIES)}")

    else:
        irc.conn.privmsg(username, "Unknown !settings command. Options: banned_mods, acc_preference")

def main():
    # Prompt user for their username at the start
    username = input("Please enter your username: ").strip()
    
    # Make sure the username is not empty
    if not username:
        print("Invalid username. Please restart and enter a valid username.")
        return
    
    # Start the command loop
    while True:
        command = input("Enter command (!r to recommend, !settings to adjust settings, q to quit): ").strip()

        if command == "q":
            break

        elif command == "!r":
                handle_recommendation_command(username)

        if command.startswith("!settings"):
            _, *args = command.split()

            if len(args) == 0:
                # Show the current settings if no subcommand is provided
                banned_mods, acc_preference = get_user_settings(username)
                print(f"Current settings for {username}:")
                print(f"  Banned Mods: {' '.join(banned_mods) if banned_mods else 'None'}")
                print(f"  Accuracy Preference: {acc_preference}")
            elif args[0] == "banned_mods":
                if len(args) > 1:
                    # Update banned mods by adding the new mods (whole mod combinations, no split)
                    new_banned_mods = args[1:]  # This is a list of mod combinations like ['HD+HR+DT', 'HD']
                    result, invalid_mods = update_banned_mods(username, new_banned_mods)
                    
                    if result:
                        print(f"Updated banned mods for {username}: {', '.join(new_banned_mods)}")
                    else:
                        print(f"Invalid mods: {', '.join(invalid_mods)}")
                        print(f"Valid mod combinations: {', '.join(VALID_MODS)}")
                else:
                    # Show current banned mods if no new ones are provided
                    banned_mods, _ = get_user_settings(username)
                    print(f"Current banned mods for {username}: {', '.join(banned_mods) if banned_mods else 'None'}")


            elif args[0] == "acc_preference":
                if len(args) == 2 and args[1] in VALID_ACCURACIES:
                    # Update accuracy preference
                    result = update_acc_preference(username, args[1])
                    if result:
                        print(f"Updated accuracy preference for {username}: {args[1]}")
                    else:
                        print(f"Invalid accuracy preference. Valid values are: {', '.join(VALID_ACCURACIES)}")
                else:
                    print(f"Invalid accuracy preference. Valid values are: {', '.join(VALID_ACCURACIES)}")

            else:
                print("Unknown !settings command. Available options: banned_mods, acc_preference")

if __name__ == "__main__":
    main()
