from dronekit import connect
import socket, datetime, time

#Message and channel declared at beginning
testm = "What's up, buddy? The current time is: "
msg = "RTXDC_2023_UTA_UGV_Hit_42_"
channel = "#RTXDrone"
GPS = "GPSPlaceholder"
testing = "MOTOR IS RUNNING!!!"

#Commented out for now

#vehicle = connect('com5', wait_ready=False, baud=57600)
#lat = vehicle.location.global_relative_frame.lat
#long = vehicle.location.global_relative_frame.lon

#lat_str = str(lat)
#lon_str = str(long)

#GPS = 'lat_' + lat_str + '_long_' + lon_str


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = 'irc.libera.chat'
PORT = 6667
NICK = 'UTA_UGV'

s.connect((HOST, PORT))

nick_data = ('NICK ' + NICK + '\r\n')
s.send(nick_data.encode())

username_data = ('USER UTAGnd1 UTAGnd2 UTAGnd3 :UTAGnd4 \r\n')
s.send(username_data.encode())

s.send('JOIN #RTXDrone \r\n'.encode())

while True:
    result = s.recv(1024).decode('utf-8')
    print (result)

    hit = vehicle.channels['8']
    
    if result[:4] == "PING":
        s.send(("PONG" + result[4:] + "\r\n").encode())

    if len(result) ==0:
        break

    if "PRIVMSG" in result and "#RTXDrone" in result and ":hello" in result:
        now = datetime.datetime.now()
        time = now.strftime("%I:%M:%S%p")
        s.send(('PRIVMSG ' + channel + ' :' + testm + time + GPS + '\r\n').encode())
        
    #if hit != 0:
       # s.send(('PRIVMSG ' + channel + ' :' + testing + '\r\n').encode())
        #time.sleep(3) 
