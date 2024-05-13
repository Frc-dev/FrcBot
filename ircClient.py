import irc.client
import time
from talkInterfaces import IRCInterface
from botInteraction import handle_recommendation_command
import os
from dotenv import load_dotenv

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

    def on_connect(self, conn, event):
        print("Connected to Bancho IRC")

    def on_privmsg(self, conn, event):
        sender = event.source.split('!')[0]
        message = event.arguments[0].strip()

        print(f"[PM from {sender}]: {message}")
        if message == "!r":
            handle_recommendation_command(self.interface, sender)
        elif message.startswith("!settings"):
            self.interface.send_message(sender, "The !settings command is temporarily disabled while I fix some bugs. Thanks for your patience!")

    def run(self):
        while True:
            self.client.process_once(timeout=0.2)
            time.sleep(0.1)

if __name__ == "__main__":
    bot = OsuRecommendationBot()
    bot.run()
