#Raytheon 2022-2023 Unmanned Aerial Systems (UAS) Showcase

# Carlos Mella-Rijo, ID No. 1001736758
# The University of Texas at Arlington
# Department of  Electrical Engineering
# Electrical Engineering Senior Design Team

# This is a script that connects to an IRC Channel and
# publishes a message when a sensor on our drone is hit, as per
# the requirements for the competition.

from dronekit import connect 
import socket, datetime, time, signal, sys 

#Message and channel declaration for use in IRC

channel = "#RTXDrone"
h = 1
hits = str(h)
msg = "RTXDC_2023_UTA_UGV_Hit_" + hits + "_42_"

# PWM Signal Handler
def signal_handler(sig,frame):
    GPIO.cleanup()
    sys.exit(0)
    
#Callback Function For PWM
def pwm_callback(chan):
    if GPIO.input(12):
        now = datetime.datetime.now()
        timing = now.strftime("%I:%M:%S%p)
        vehicle.armed = False
        s.send(('PRIVMSG ' + channel + ' :' + msg + timing + GPS + '\r\n').encode())
         print('PRIVMSG ' + channel + ' :' + msg + timing + GPS + '\r\n')
        time.sleep(6)
        h = h + 1
        vehicle.armed = True
                              
#Set up Pin and Interrupt for GPIO Pin
if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(12, GPIO.IN)
    GPIO.add_event_detect(12, GPIO.RISING, callback=pwm_callback, bouncetime=200)
    signal.signal(signal.SIGINT, signal_handler)
                              
#Establish connection with vehicle through USB Port 
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
