from talkInterfaces import CLIInterface
from botInteraction import handle_recommendation_command, handle_settings_command

def main():
    interface = CLIInterface()
    username = input("Enter your osu! username: ").strip()

    while True:
        command = input("Enter command (!r, !settings, q): ").strip()

        if command == "q":
            break
        elif command == "!r":
            handle_recommendation_command(interface, username)
        elif command.startswith("!settings"):
            args = command.split()[1:]
            handle_settings_command(interface, username, args)
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
