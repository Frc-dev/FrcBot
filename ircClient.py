import irc.client
import time
from botInteraction import handle_recommendation_command, handle_settings_command
from constants import VALID_MODS, VALID_ACCURACIES
import os
from dotenv import load_dotenv

load_dotenv()

OSU_USERNAME = os.getenv("OSU_IRC_USERNAME")
OSU_IRC_PASSWORD = os.getenv("OSU_IRC_PASSWORD")

class OsuRecommendationBot:
    def __init__(self):
        self.client = irc.client.Reactor()
        self.conn = self.client.server().connect("irc.ppy.sh", 6667, OSU_USERNAME, password=OSU_IRC_PASSWORD)
        self.conn.add_global_handler("welcome", self.on_connect)
        self.conn.add_global_handler("privmsg", self.on_privmsg)

    def on_connect(self, conn, event):
        print("Connected to Bancho IRC")

    def on_privmsg(self, conn, event):
        sender = event.source.split('!')[0]
        message = event.arguments[0].strip()
        print(f"[PM from {sender}]: {message}")

        if message == "!r":
            handle_recommendation_command(self, sender)

        elif message.startswith("!settings"):
            parts = message.split()
            handle_settings_command(self, sender, parts[1:] if len(parts) > 1 else [])

    def run(self):
        # This method runs the bot continuously
        while True:
            try:
                self.client.process_once(timeout=0.2)
                time.sleep(0.1)  # Keep the bot running and processing messages
            except Exception as e:
                print(f"Error occurred: {e}")
                time.sleep(10)  # Wait before retrying if an error occurs

def run_bot():
    """This method ensures the bot keeps running forever."""
    while True:
        try:
            bot = OsuRecommendationBot()
            bot.run()  # Run the IRC bot
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(10)  # Wait before retrying if an error occurs

if __name__ == "__main__":
    run_bot()
