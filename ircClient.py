import irc.client
import time
from talkInterfaces import IRCInterface
from botInteraction import handle_recommendation_command
import os
from dotenv import load_dotenv
from datetime import datetime  # Import the datetime module

load_dotenv()

OSU_USERNAME = os.getenv("OSU_IRC_USERNAME")
OSU_IRC_PASSWORD = os.getenv("OSU_IRC_PASSWORD")

class OsuRecommendationBot:
    def __init__(self):
        self.client = irc.client.Reactor()
        self.conn = self.client.server().connect("irc.ppy.sh", 6667, OSU_USERNAME, password=OSU_IRC_PASSWORD)
        self.interface = IRCInterface(self.conn)

        self.conn.add_global_handler("welcome", self.on_connect)
        self.conn.add_global_handler("privmsg", self.on_privmsg)

    def log_conversation(self, sender, message, reply):
        """Function to log conversation to a file specific to the user"""
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create a unique log file for each user based on their username
        log_file_name = f"{sender}_conversation_log.txt"

        with open(log_file_name, "a") as log_file:
            log_file.write(f"[{timestamp}] User: {sender} - Message: {message}\n")
            log_file.write(f"[{timestamp}] Bot: {reply}\n\n")

    def on_connect(self, conn, event):
        print("Connected to Bancho IRC")

    def on_privmsg(self, conn, event):
        sender = event.source.split('!')[0]
        message = event.arguments[0].strip()

        # Get current timestamp for printing
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Print the message received from the user with timestamp
        print(f"[{timestamp}] [PM from {sender}]: {message}")
        
        reply = ""  # This will store the bot's reply

        if message == "!r":
            reply = handle_recommendation_command(self.interface, sender)
        elif message.startswith("!settings"):
            reply = "The !settings command is temporarily disabled while I fix some bugs. Thanks for your patience!"

        # Print the reply that the bot sends to the user with timestamp
        print(f"[{timestamp}] [PM to {sender}]: {reply}")

        # Log the conversation with timestamp
        self.log_conversation(sender, message, reply)

        # Send the reply to the user
        self.interface.send_message(sender, reply)

    def run(self):
        while True:
            self.client.process_once(timeout=0.2)
            time.sleep(0.1)

if __name__ == "__main__":
    bot = OsuRecommendationBot()
    bot.run()
