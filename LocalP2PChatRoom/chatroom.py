import socket, json, time, threading, hashlib


class clientInfo():
    def __init__(self, ip, port, name, heartbeat):
        self.ip = ip
        self.port = port
        self.name = name
        self.id = hashlib.md5((self.ip + "-" + str(self.port)).encode("utf-8")).hexdigest()
        self.lastheartbeat = heartbeat

    @staticmethod
    def generateID(addr):
        return hashlib.md5((addr[0] + "-" + str(addr[1])).encode("utf-8")).hexdigest()

    @property
    def addr(self):
        return (self.ip, self.port)

    def setHeartbeat(self, heartbeat):
        self.lastheartbeat = heartbeat

    def checkAlive(self):
        return time.time() - self.lastheartbeat <= 60 * 5


class chatserver():
    def __init__(self, ip, port, bufsize):
        self.ip = ip
        self.port = port
        self.bufsize = bufsize
        self.udpserver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpserver.bind((ip, port))

    def sendRawText(self, addr, rawtext):
        """
        :param ci: clientInfo object
        :param rawtext: raw text msg
        :type ci: clientInfo
        :type rawtext: string
        """
        self.udpserver.sendto(rawtext.encode("utf-8"), addr)

    def sendJson(self, addr, jobj):
        self.sendRawText(addr, json.dumps(jobj))

    def sendCommand(self, addr, mtype, msg):
        self.sendJson(addr, {"type": mtype, "content": msg})

    def receiveRawText(self):
        try:
            data, addr = self.udpserver.recvfrom(self.bufsize)
            return str(data, encoding="utf-8"), addr
        except:
            return None, None

    def receiveJson(self):
        data, addr = self.receiveRawText()
        if (data is None):
            return data, addr
        try:
            return json.loads(data), addr
        except:
            return None, None


class chatclient():
    def __init__(self, ip, port, name, tracker, bufsize=1024):
        self.cInfo = clientInfo(ip, port, name, time.time())
        self.clients = {}
        self.ip = ip
        self.port = port
        self.name = name
        self.tracker = tracker
        self.outputLevel = 0
        self.status = True
        self.chatserver = chatserver(ip, port, bufsize)

    def getAllClients(self):
        tmpC = {}
        tmpC[self.cInfo.id] = self.cInfo
        tmpC.update(self.clients)
        return tmpC

    def sendHelloMsg(self, addr):
        self.chatserver.sendCommand(addr, "hello", self.name)

    def sendByeMsg(self, addr):
        self.chatserver.sendCommand(addr, "bye", self.name)

    def sendAliveMsg(self, addr):
        self.chatserver.sendCommand(addr, "alive", self.name)

    def sendTextMsg(self, addr, msg):
        self.chatserver.sendCommand(addr, "text", msg)

    def sendRequestClistMsg(self, addr):
        self.chatserver.sendCommand(addr, "request", self.name)

    def broadcastHelloMsg(self):
        for ci in self.getAllClients().values():
            self.sendHelloMsg(ci.addr)

    def broadcastByeMsg(self):
        for ci in self.getAllClients().values():
            self.sendByeMsg(ci.addr)

    def broadcastAliveMsg(self):
        for ci in self.getAllClients().values():
            self.sendAliveMsg(ci.addr)

    def broadcastTextMsg(self, msg):
        for ci in self.getAllClients().values():
            self.sendTextMsg(ci.addr, msg)

    def broadcastRequestClistMsg(self):
        for ci in self.getAllClients().values():
            self.sendRequestClistMsg(ci.addr)

    def sendClistMsg(self, addr):
        cis = []
        for ci in self.getAllClients().values():
            cis.append("%s,%s,%s" % (ci.ip, ci.port, ci.name))
        self.chatserver.sendCommand(addr, "clist", json.dumps(cis))

    def updateHeartBeat(self, id):
        if id == self.cInfo.id:
            self.cInfo.setHeartbeat(time.time())
            return
        if id in self.clients.keys():
            self.clients[id].setHeartbeat(time.time())
            return True
        else:
            return False

    def output(self, *args, level=2):
        if level >= self.outputLevel:
            print(*args)

    def start(self):
        rt = threading.Thread(target=self._recieveThread)
        st = threading.Thread(target=self._sendThread)
        ht = threading.Thread(target=self._heartbeatThread)
        ct = threading.Thread(target=self._checkaliveThread)
        rt.start()
        st.start()
        ht.start()
        ct.start()
        self.sendRequestClistMsg(self.tracker)
        rt.join()
        st.join()
        ht.join()
        ct.join()

    def _recieveThread(self):
        while self.status:
            data, addr = self.chatserver.receiveJson()
            self.output("Receive raw data", data, addr, level=0)
            if data is None:
                continue
            if data["type"] == "hello":
                if clientInfo.generateID(addr) == self.cInfo.id:
                    continue
                self.clients[clientInfo.generateID(addr)] = clientInfo(addr[0], addr[1], data["content"], time.time())
                self.output("Receive hello command from ", addr, level=1)

            if data["type"] == "alive":
                self.updateHeartBeat(clientInfo.generateID(addr))
                self.output("Receive alive command from ", addr, level=1)

            if data["type"] == "bye":
                if clientInfo.generateID(addr) == self.cInfo.id:
                    continue
                self.clients.pop(clientInfo.generateID(addr))
                self.output("Receive bye command from ", addr, level=1)

            if data["type"] == "text":
                self.output("Receive text command from ", addr, level=1)
                self.output(addr[0], self.getAllClients()[clientInfo.generateID(addr)].name, ":", data["content"])

            if data["type"] == "request":
                self.output("Receive request command from ", addr, level=1)
                self.sendClistMsg(addr)
                self.output("send clist command to ", addr, level=1)

            if data["type"] == "clist":
                self.output("Receive clist command from ", addr, level=1)
                clist = json.loads(data["content"])
                for ip, port, name in map(lambda a: a.split(","), clist):
                    ci = clientInfo(ip, int(port), name, time.time())
                    if ci.id == self.cInfo.id:
                        continue
                    self.clients[ci.id] = ci
                    self.output("add new client ", ip, port, name, level=1)
                self.output("update client number ", len(clist), level=1)
                self.broadcastHelloMsg()
                self.output("send hello command ", len(clist), level=1)

    def _sendThread(self):
        self.output("Enter text")
        while self.status:
            text = input("")
            if (len(text) > 0 and text[0] == "$"):
                if text[1::] == "exit":
                    self.status = False
                    self.broadcastByeMsg()
                    continue
            self.broadcastTextMsg(text)
            self.output("broadcast msg ", text, level=1)

    def _heartbeatThread(self):
        while self.status:
            self.broadcastAliveMsg()
            self.output("broadcast heartbeat ", level=1)
            time.sleep(1)

    def _checkaliveThread(self):
        while self.status:
            offline = []
            for id in self.clients:
                if not self.clients[id].checkAlive():
                    offline.append(id)
            for id in offline:
                self.clients.pop(id)
            time.sleep(1)


tracker = ("127.0.0.1", 10001)
pt = int(input("port: "))
name = input("name: ")
a = chatclient("127.0.0.1", pt, name, tracker)
a.start()
