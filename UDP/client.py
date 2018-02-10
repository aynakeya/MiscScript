import socket
import sys

port = 7777
mtu = 1500
udpserver = ("127.0.0.1",6666)

try:
    sktsend = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
except:
    print("Unable to send at this port %s" % port)
    sktsend.close()
    sys.exit()

serverip = input("Enter the sever ip: ")
serverport = input("Enter the port: ")

try:
    udpserver = (serverip,int(serverport))
except:
    print("Error")
    sktsend.close()
    sys.exit()

sktsend.bind(("127.0.0.1",port))
print("UDP Client open at port %s" % port)
print("Connect to %s at port %s" % udpserver)

while True:
    try:
        data = input("Enter the Text:")
        if data == "stop-client":
            break
        sktsend.sendto(("%s" % data).encode("utf-8"), udpserver)
    except:
        print("Error")

print("Client Stop")
sktsend.close()