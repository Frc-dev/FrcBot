import irc.client
import time
from talkInterfaces import IRCInterface
from botInteraction import handle_recommendation_command, handle_settings_command, handle_feedback_command
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

load_dotenv()

OSU_USERNAME = os.getenv("OSU_IRC_USERNAME")
OSU_IRC_PASSWORD = os.getenv("OSU_IRC_PASSWORD")
IGNORED_SENDERS = {"BanchoBot"}

class OsuRecommendationBot:
    def __init__(self):
        self.client = irc.client.Reactor()
        self.conn = self.client.server().connect("irc.ppy.sh", 6667, OSU_USERNAME, password=OSU_IRC_PASSWORD)
        self.interface = IRCInterface(self.conn)

        self.conn.add_global_handler("welcome", self.on_connect)
        self.conn.add_global_handler("privmsg", self.on_privmsg)
        self.conn.add_global_handler("action", self.on_action)

    def log_conversation(self, sender, message, reply):
        """Function to log conversation to a file specific to the user in the logs folder."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_directory = "logs/msg"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        
        log_file_name = os.path.join(log_directory, f"{sender}_conversation_log.txt")
        
        with open(log_file_name, "a") as log_file:
            log_file.write(f"[{timestamp}] User: {sender} - Message: {message}\n")
            log_file.write(f"[{timestamp}] Bot: {reply}\n\n")

    def log_error(self, error_message):
        """Function to log errors with timestamp in the logs/error directory"""
        log_directory = "logs/error"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        log_file_path = os.path.join(log_directory, "error_log.txt")

        logger = logging.getLogger()  # Root logger
        logger.setLevel(logging.ERROR)

        # Avoid adding multiple handlers
        if not logger.handlers:
            handler = logging.FileHandler(log_file_path)
            formatter = logging.Formatter('%(asctime)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        logger.error(error_message)

    def on_connect(self, conn, event):
        print("Connected to Bancho IRC")
        if not conn.is_connected():
            error_message = "Failed to connect to IRC server"
            self.log_error(error_message)

    def on_privmsg(self, conn, event):
        sender = event.source.split('!')[0]

        if sender in IGNORED_SENDERS:
            return
        
        message = event.arguments[0].strip()
        args = message.split()[1:]
        # Get current timestamp for printing
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            reply = ""  # This will store the bot's reply

            if message.startswith("!r"):
                #recommendation_command expects a string and not a list
                arg_str = args[0] if args else ""
                reply = handle_recommendation_command(sender, arg_str)
            elif message.startswith("!settings"):
                reply = handle_settings_command(sender, args)
            elif message.startswith("!feedback"):
                reply = handle_feedback_command(sender, args)
            elif message.startswith("!h"):
                reply = "Usage: !r, !settings, !feedback"

            # Print the reply that the bot sends to the user with timestamp
            print(f"[{timestamp}] [PM to {sender}]: {reply}")

            # Log the conversation with timestamp
            self.log_conversation(sender, message, reply)

            # Send the reply to the user
            self.interface.send(sender, reply)

        except Exception as e:
            # If an error occurs, log it and print the error
            error_message = f"Error while processing message from {sender}: {str(e)}"
            self.log_error(error_message)

    def on_action(self, conn, event):
        sender = event.source.split('!')[0]

        if sender in IGNORED_SENDERS:
            return

        # Extract and log the action message
        action_message = event.arguments[0] if event.arguments else ""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"[{timestamp}] [ACTION from {sender}]: {action_message}"
        self.log_conversation(sender, log_entry, "ACTION handled")

        # Placeholder for future /np functionality
        self.interface.send(sender, "/np command coming soon!")

    def run(self):
        try:
            start_time = time.time()  # Record the start time
            while True:
                # Process IRC events
                self.client.process_once(timeout=0.2)
                time.sleep(0.1)
                
        except Exception as e:
            error_message = f"Unexpected error in bot main loop: {str(e)}"
            self.log_error(error_message)

if __name__ == "__main__":
    bot = OsuRecommendationBot()
    try:
        bot.run()
    except Exception as e:
        # If an error happens during startup or runtime, log it and terminate gracefully
        error_message = f"Bot failed to start or run: {str(e)}"
        bot.log_error(error_message)
