#Raytheon 2022-2023 Unmanned Aerial Systems (UAS) Showcase

# Carlos Mella-Rijo, ID No. 1001736758
# The University of Texas at Arlington
# Department of  Electrical Engineering
# Electrical Engineering Senior Design Team

# This is a script that connects to an IRC Channel and
# publishes a message when a sensor on our drone is hit, as per
# the requirements for the competition.

from dronekit import connect # import connection lib from dronekit
import socket, datetime, time #import socket and time libs 

#Message declared at beginning  along with channel
msg = "RTXDC_2023_UTA_UGV_Hit_42_"
channel = "#RTXDrone"

#Establish connection with vehicle
vehicle = connect('/dev/ttyAMA0', wait_ready=False, baud=921600)

#Pull GPS Coordinates latitude and longitude from Mavlink stream
lat = vehicle.location.global_relative_frame.lat
long = vehicle.location.global_relative_frame.lon

#Convert GPS coords from int to strings so it can be encoded 
lat_str = str(lat)
lon_str = str(long)

#Write GPS part of string Message
GPS = 'lat_' + lat_str + '_long_' + lon_str


# Use socket lib to connect to IRC Server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = 'irc.libera.chat' #Hostname / Server Name
PORT = 6667 #TCP Port we will connect to server on
NICK = 'UTA_UGV' #Nickname for UTA UGV

#Connect to specified server on the specified port
s.connect((HOST, PORT))

#Entering Nickname for UTA UGV bot
nick_data = ('NICK ' + NICK + '\r\n')
s.send(nick_data.encode())

#Entering official username for UTA UGV bot
username_data = ('USER UTAGnd1 UTAGnd2 UTAGnd3 :UTAGnd4 \r\n')
s.send(username_data.encode())

#Joining command following irc protocol 
s.send('JOIN '+ channel + '\r\n'.encode())

while True: #while loop that runs indefinitely
    #print received messages to screen
    result = s.recv(1024).decode('utf-8')
    print (result)

    #ping-pong mechanism (so script continuously verifies packets to keep connection going)
    if result[:4] == "PING":
        s.send(("PONG" + result[4:] + "\r\n").encode())
    #disconnect if channel stops sending pings
    if len(result) ==0:
        break
    #if this message is published:
    if "PRIVMSG" in result and "#RTXDrone" in result and ":hello" in result:
        #Pull current time attribute from datetime class
        now = datetime.datetime.now()
        #Pull time in 12 hr format and convert to string
        time = now.strftime("%I:%M:%S_%p_")
        #Send this message to the channel:
        s.send(('PRIVMSG ' + channel + ' :' + msg + time + '\r\n').encode())
