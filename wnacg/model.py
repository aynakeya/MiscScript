import requests, os
from bs4 import BeautifulSoup
from pyaria2 import Aria2RPC
from config import Config


def httpConnect(url,headers,proxies,maxReconn=5):
    trial = 0
    while trial < maxReconn:
        try:
            return requests.get(url, headers=headers, proxies=proxies, timeout=5)
        except:
            trial += 1
            continue
    return None

class bookModel():
    durl = "https://wnacg.com/download-index-aid-%s.html"
    headers = {"authority": "wnacg.com",
               "method": "GET",
               "scheme": "https",
               "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
               'Connection': 'close'
               }

    def __init__(self, id):
        self.id = id
        self.filename = ""
        self.proxies = Config.proxies
        self.status = 404
        self.links = []


    def getInfo(self):
        raw_data = httpConnect(self.durl % self.id,self.headers,self.proxies)
        links = []
        if raw_data == None:
            return False
        soup = BeautifulSoup(raw_data.content.decode("utf8"), features="html.parser")
        self.filename = soup.title.string.replace("的下載地址 - 紳士漫畫-專註分享漢化本子|邪惡漫畫", "")
        self.status = 200
        for e in soup.find_all(name="a", attrs={"class": "down_btn"}):
            if e.get("href") != None:
                links.append(e.get("href"))
        for e in soup.find_all(name="p", attrs={"class": "download_filename"}):
            self.filename = e.text
            break
        self.links = links
        return True

    def getFilename(self):
        if len(self.links) == 0:
            return ""
        suffix = self.links[0].split(".")[-1]
        fn = ".".join(self.filename.split(".")[:-1:])
        if self.filename.split(".")[-1] == suffix:
            return self.filename

        return ".".join([self.filename, suffix])

    def export(self,dir, fn):
        path = os.path.join(dir, fn)
        if not os.path.exists(dir):
            os.mkdir(dir)
        with open(path, "a+", encoding="utf8") as f:
            f.write("[Filename:%s]\n" % self.filename)
            for l in self.links:
                f.write("%s\n" % l)
            f.write("[END]")


class ariaDownloader():
    def __init__(self, url=Config.aria2rpc, token=Config.aria2token):
        self.rpc = Aria2RPC(url=url, token=token)

    def download(self, url, route, filename):
        self.rpc.addUri([url], {"dir": route, "out": filename, })

class simpleDownloader():
    def __init__(self):
        if Config.proxyDownload:
            self.proxies = Config.proxies
        else:
            self.proxies = {}
        self.headers = Config.commonHeaders


    def download(self, url, route, fn):
        raw_data = httpConnect(url,self.headers,self.proxies)
        if raw_data == None:
            return False
        path = os.path.join(route, fn)
        if not os.path.exists(route):
            os.mkdir(route)
        with open(path,"wb+") as f:
            f.write(raw_data.content)
        return True

downloaders = {"aria":ariaDownloader,"simple":simpleDownloader}