import sys
import irc.bot
import requests

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.shipList = list()

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print ('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)

        #read in the ship list and lower case it
        with open('shiplist.txt') as f:
            self.shipList = f.read().split("\n")
        f.close
        self.shipList = [x.lower() for x in self.shipList]
            

    def on_welcome(self, c, e):
        print ('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):

        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0][1:]
            print ('Received command: ' + cmd)
            self.do_command(e, cmd)
        return

    def do_command(self, e, cmd):
        c = self.connection
        commandList = cmd.split()
        command = commandList[0]


        if command == "test":
            print("current command: {} ".format(commandList))

        elif command == "ship":            
            shipList = self.shipList
            ship = commandList[1].lower()
            if ship in shipList:
                message = "https://wiki.eveuniversity.org/" + ship
                c.privmsg(self.channel, message)
            else:
                message = ship + " is not a ship"
                c.privmsg(self.channel, message)
            print("processed command ship for " + ship)
        # The command was not recognized
        else:
            print("Did not understand command: " + cmd)

def main():
    if len(sys.argv) != 5:
        print("Usage: twitchbot <username> <client id> <token> <channel>")
        sys.exit(1)

    username = sys.argv[1]
    client_id = sys.argv[2]
    token = sys.argv[3]
    channel = sys.argv[4]

    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

if __name__ == "__main__":
    main()
