from talkInterfaces import CLIInterface
from botInteraction import handle_recommendation_command, handle_settings_command, handle_feedback_command
from sessionManager import set_local_flag

def main():
    interface = CLIInterface()
    username = input("Enter your osu! username: ").strip()

    while True:
        command = input("Enter command (!r, !settings, !feedback, q): ").strip()

        if command == "q":
            break
        elif command.startswith("!r"):
            # Handle recommendation command and capture the reply
            set_local_flag(username, True)
            args = command.split()[1:]
            if (len(args) == 1):
                args = args[0]
            else:
                args = None

            reply = handle_recommendation_command(username, args)
            interface.send(reply)  # Print the reply
        elif command.startswith("!settings"):
            # Extract arguments and handle settings command
            args = command.split()[1:]
            reply = handle_settings_command(username, args)
            interface.send(reply)  # Print the reply
        elif command.startswith("!feedback"):
            args = command.split()[1:]
            reply = handle_feedback_command(username, args)
            interface.send(reply)  # Print the reply
        elif command.startswith("!h"):
            reply = "Usage: !r, !settings, !feedback"
            interface.send(reply)
        else:
            interface.send("Unknown command.")

if __name__ == "__main__":
    main()
