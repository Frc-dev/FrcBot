class IRCInterface:
    def __init__(self, conn):
        self.conn = conn

    def send(self, username, message):
        self.conn.privmsg(username, message)
#hello

class CLIInterface:
    def send(self, username, message):
        print(message)
