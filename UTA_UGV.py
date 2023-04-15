import irc.client
import irc.bot
import threading
from   datetime   import datetime\
from dronekit import connect 
import socket, datetime, time, signal, sys, logging 
import RPi.GPIO as GPIO
"""
    @brief: IRCBot inherits from the irc.client.SimpleIRCClient class. It represents a
                basic template for creating an IRC bot, which connects to an IRC server
                and a specified channel. Both UAVBot and UGVHitListener inherit from
                this class
"""
# PWM Signal Handler
def signal_handler(sig,frame):
    GPIO.cleanup()
    sys.exit(0)
    
#Callback Function For PWM
def pwm_callback(chan):
    if GPIO.input(12):
        
        #Play Hit Sound - Tell user of hit - Disarm
        vehicle.play_tune('DBA','utf-8')
        print("The UGV has been hit. Marker: 42. Disarming...")
        vehicle.armed = False
        print("UGV Disarmed. Publishing Message...")
        
        # Send hit message to server
        ugv_bot.send_hit_message(current_time, location)
        
        hitlog = open("hitlog_file.txt", "a")
        hitlog.write('PRIVMSG ' + channel + ' :' + msg + timing + GPS + '\r\n')
        hitlog.close()
        time.sleep(6)
        h = h + 1
        print("Message has been published. Rearming...")
        vehicle.armed = True
        print("UGV Armed. Continuing Mission...")
                              
#Set up Pin and Interrupt for GPIO Pin
if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.IN)
    GPIO.add_event_detect(12, GPIO.RISING, callback=pwm_callback, bouncetime=500)
    signal.signal(signal.SIGINT, signal_handler)
                              


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

    # Send hit message to channel
    def send_hit_message(self, aruco_id, time_of_hit, location):

        time_of_hit = time_of_hit.strftime("%m-%d-%Y %I:%M:%S")

        # Format the message with the given information
        message = f"RTXDC_2023 UTA_UGV_Hit_42_{time_of_hit}_{location}"

        # Send the message to the channel
        self.connection.privmsg(self.channel, message)

# Create a function to run the IRC bot in a separate thread
def run_bot(bot):
    bot.start()

    
#Now startup sequence begins

print("Creating the IRC bots...")

# Create and start the UGVBot in a separate thread
ugv_bot    = UGVBot()
ugv_thread = threading.Thread(target = run_bot, args = (ugv_bot,))
ugv_thread.start()

# Wait for the UGVBot to connect to the server
while not ugv_bot.connected:
    time.sleep(1)

print("Made it past the IRC bot initialization")

#Establish connection with vehicle through USB Port 
print("Connecting to Vehicle on /dev/ttyAMA0...")
vehicle = connect('/dev/ttyAMA0', wait_ready=False, baud=921600)
print("Connected to UGV. Waiting for Mode: AUTO")

# Make the mode stabilize so that we don't get "auto mode not armable"
#   This will be switched to auto after the drone is armed
if vehicle.mode != 'AUTO':
    vehicle.wait_for_mode('AUTO')
    print('Mode: ', vehicle.mode)

print('Arming...')
vehicle.arm()

if vehicle.armed == True:
    print('Armed')
else:
    print('Could not arm...')

#Pull GPS Coordinates latitude and longitude from Mavlink stream
lat = vehicle.location.global_relative_frame.lat
long = vehicle.location.global_relative_frame.lon

# Write GPS part of string message, convert GPS coords to strings so it can be encoded 
location     = f"{lat}_{lon}"
current_time = datetime.now()


# End the IRC bot connections
ugv_bot.end("UTA_UGV")
