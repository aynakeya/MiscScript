import socket,threading,time

clients = {}

class client(object):
    def __init__(self,socket,addr,username):
        self.addr = addr[0]
        self.port = addr[1]
        self.username = username
        self.socket = socket

    def sendMsg(self,msg,username,admin):
        try:
            if admin:
                self.socket.send(("%s %s(管理员): %s" % (self.getTime(), username, msg)).encode("utf-8"))
            else:
                self.socket.send(("%s %s: %s" %(self.getTime(), username, msg)).encode("utf-8"))
            return True
        except:
            return False

    def recv(self,mtu=1024):
        try:
            data = self.socket.recv(mtu).decode("utf-8")
            if data == "-!-quit-!-" or not data:
                return False
            return data
        except:
            return False

    def close(self):
        try:
            self.socket.close()
            return True
        except:
            return False

    def getId(self):
        return "%s-%s" % (self.addr,self.port)
    def getTime(self):
        return str(time.strftime("%Y-%m-%d %H:%M:%S"))

def new_client(c):
    try:
        print("%s(%s) 尝试连接" %(c.addr,c.port))
        data = c.recv()
        if not data:
            return
        if len(data) >= 16:
            c.socket.send("用户名太长了")
            return
        c.username = data
        print("用户%s %s(%s)已连接" %(c.username,c.addr,c.port))
        c.socket.send("已连接".encode("utf-8"))
        while True:
            data = c.recv()
            if not data:
                break
            else:
                print("用户%s %s(%s) 发送了: %s" % (c.username,c.addr, c.port, data))
                broadcast(data,c.username)

    except socket.errno as e:
        print("Socket error: %s" % str(e))
    except Exception as e:
        print("Other exception: %s" % str(e))
    finally:
        print("%s(%s) 断开连接" % (c.addr, c.port))
        c.close()
        clients.pop(c.getId())

def broadcast(msg,username,admin=False):
    for c in clients.values():
        c.sendMsg(msg,username,admin)

def start_server(port,local=True,cnum=10):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if local:
        host = "127.0.0.1"
    else:
        host = socket.gethostname()
    server.bind((host, port))

    # 侦听客户端
    server.listen(cnum)
    print("服务器已开启")

    while True:
        # 接受客户端连接
        conn, addr = server.accept()
        c = client(conn,addr,"")
        clients[c.getId()] = c
        t = threading.Thread(target=new_client, args=(c,))
        t.start()


if __name__ == "__main__":
    start_server(12345,local=False)
    print("服务器已关闭")