from talkInterfaces import CLIInterface
from botInteraction import handle_recommendation_command, handle_settings_command, handle_feedback_command

def main():
    interface = CLIInterface()
    username = input("Enter your osu! username: ").strip()

    while True:
        command = input("Enter command (!r, !settings, !feedback, q): ").strip()

        if command == "q":
            break
        elif command == "!r":
            # Handle recommendation command and capture the reply
            reply = handle_recommendation_command(username)
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
        else:
            interface.send("Unknown command.")

if __name__ == "__main__":
    main()
