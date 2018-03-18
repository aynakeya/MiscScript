import socket
import sys

def newsocket(addr="0.0.0.0",port=6666):
    try:
        socketserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socketserver.bind((addr,port))
        print("Sever Open")
        print("Listen at port %s" % port)
        return socketserver
    except:
        print("Unable to listen at this port %s" % port)
        return -1

def sendmessges(skt,udpserver=("127.0.0.1",6666)):
    if skt == -1 :
        return -1
    print("Connect to %s at port %s" % udpserver)
    messagecount = 0
    while True:
        try:
            data = input("Enter the Text:")
            if data == "stop-client":
                break
            skt.sendto(("%s" % data).encode("utf-8"), udpserver)
            messagecount += 1
        except:
            print("Error")
    return messagecount

try:
    serverip = input("Enter the sever ip: ")
    serverport = int(input("Enter the port: "))
    udpserver = (serverip,int(serverport))
except:
    print("Error")
    sys.exit()

print("Sent %s messages" % sendmessges(newsocket(port=7777),udpserver))