import irc.client
import irc.bot
import threading
import time
from   datetime   import datetime

"""
    @brief: IRCBot inherits from the irc.client.SimpleIRCClient class. It represents a
                basic template for creating an IRC bot, which connects to an IRC server
                and a specified channel. Both UAVBot and UGVHitListener inherit from
                this class
"""
class IRCBot(irc.client.SimpleIRCClient):
    def __init__(self, bot_name, server, channel):
        # Initialize the bot by connecting to the IRC server and joining the channel
        irc.client.SimpleIRCClient.__init__(self)

        # Set the server and channel information
        self.server  = server
        self.channel = channel

        # Set the bot's initial connection status to False
        self.connected = False

        # Connect the bot to the server and join the channel
        self.connect(self.server, 6667, bot_name)
        self.connection.join(self.channel)

    def on_welcome(self, connection, event):
        # When the bot successfully joins the channel, set its connection status to True
        connection.join(self.channel)
        self.connected = True
        print(f"{self.__class__.__name__} connected to {self.server} and joined {self.channel}")
    
    # Disconnect the bot from the server
    def end(self, bot_name):
        # Check if the bot is currently connected to the server
        if self.connected:
            self.connection.part(self.channel)                                    # Leave the channel the bot is currently in
            self.connection.quit(bot_name + " is disconnecting from the server.") # Send a quit message to the IRC server and disconnect the bot
            self.connected = False

"""
    @brief: UGVBot is an IRC bot that joins the IRC server and sends messages
                when the drone fires its laser. The message contains all the
                content required by Raytheon
"""
class UGVBot(IRCBot):
    def __init__(self):
        # Call the parent constructor to connect to the IRC server and join the channel
        IRCBot.__init__(self, "UTA_UGV", "irc.libera.chat", "#RTXDrone")

    # Send fire message to channel
    def send_hit_message(self, aruco_id, time_of_hit, location):

        time_of_hit = time_of_hit.strftime("%m-%d-%Y %I:%M:%S")

        # Format the message with the given information
        message = f"RTXDC_2023 UTA_UGV_Hit_42_{time_of_hit}_{location}"

        # Send the message to the channel
        self.connection.privmsg(self.channel, message)

# Create a function to run the IRC bot in a separate thread
def run_bot(bot):
    bot.start()

print("Creating the IRC bots...")

# Create and start the UGVBot in a separate thread
ugv_bot    = UGVBot()
ugv_thread = threading.Thread(target = run_bot, args = (ugv_bot,))
ugv_thread.start()

# Wait for the UGVBot to connect to the server
while not ugv_bot.connected:
    time.sleep(1)

print("Made it past the IRC bot initialization")

# Pull GPS Coordinates latitude and longitude from Mavlink stream
lat  = vehicle.location.global_relative_frame.lat
lon  = vehicle.location.global_relative_frame.lon

# Write GPS part of string message, convert GPS coords to strings so it can be encoded 
location     = f"{lat}_{lon}"
current_time = datetime.now()

# Send hit message to server
ugv_bot.send_hit_message(current_time, location)

# End the IRC bot connections
ugv_bot.end("UTA_UGV")
