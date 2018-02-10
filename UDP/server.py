import socket
import sys

port = 6666
mtu = 1500

try:
    skt = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
except:
    print("Unable to listen at this port %s" % port)
    skt.close()
    sys.exit()

print("Sever Open")
skt.bind(("0.0.0.0",port))
print("Listen at port %s" % port)
while True:
    try:
        data, addr = skt.recvfrom(mtu)
        data = data.decode("utf-8")
        print("Recieve a message: \"%s\" from %s" % (data, addr))
        skt.sendto(("-%s-" % data).encode("utf-8"),addr)
    except:
        print("Error")
    if data == "stop-server":
        break


print("Server Close")
skt.close()