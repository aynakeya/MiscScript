import os, re, requests,ariaDownloader
from bs4 import BeautifulSoup

saveroute = r"E:\ProgramProject\xiee33pic\downloads"

headers = {
    "user-agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"}


class book:
    base_url = "https://m.xiee33.com/xesnmh/%s.html"
    page_url = "https://m.xiee33.com/xesnmh/%s_%s.html"
    imgReg = "([0-9]*)_([0-9]*).html"

    def __init__(self, bid):
        self.bid = bid
        self.title = ""
        self.category = ""
        self.status = 404
        self.getTitle()

    def getTitle(self):
        data = self.getPage(1)
        if data == None:
            return
        self.status = 200
        soup = BeautifulSoup(data, features="html.parser")
        title = soup.title.string.replace(" - 漫画 - 邪恶33", "").split(" ")
        for c in soup.find_all(name="a", attrs={"href": re.compile(self.imgReg)}):
            if c.img != None:
                if c.img.get("alt") != None:
                    title = c.img.get("alt").split("：")
        try:
            self.category, self.title = title[0], title[1]
        except:
            self.title = " ".join(title)
        if self.title[-1] == " ":
            self.title = self.title[:-1:]
        self.title = re.sub("[/\\\\:*?<>|]","",self.title)

    def getPage(self, p):
        if p == 1:
            url = self.base_url % self.bid
        else:
            url = self.page_url % (self.bid, p)
        raw_data = None
        for i in range(5):
            try:
                raw_data = requests.get(url, timeout=2)
                break
            except:
                continue
        if raw_data == None:
            return None
        if raw_data.status_code == 404:
            return None
        return raw_data.content.decode("GBK")

    def findImg(self, p):
        data = self.getPage(p)
        if data == None:
            return ""
        soup = BeautifulSoup(data, features="html.parser")
        # for c in soup.find_all(name="a", attrs={"href": re.compile(self.imgReg)}):
        for c in soup.find_all(name="a"):
            if c.img != None:
                return c.img.get("src")
        return ""

    def downImg(self, p):
        route = os.path.join(saveroute, self.title, "img")
        if not os.path.exists(route):
            os.makedirs(route)
        url = self.findImg(p)
        if len(url) == 0:
            return False
        data = None
        for i in range(3):
            try:
                data = requests.get(url, timeout=2)
                break
            except:
                continue
        if data == None:
            return True
        print(p)
        with open(os.path.join(route, "%s.%s" % (p, url.split(".")[-1])), "wb+") as f:
            f.write(data.content)
        return True

    def downBook(self):
        page = 1
        print("Start")
        while self.downImg(page):
            page += 1
        print("Success")

    def downBookAria(self):
        route = os.path.join(saveroute, self.title, "img")
        if not os.path.exists(route):
            os.makedirs(route)
        page = 1
        while True:
            url = self.findImg(page)
            if len(url) == 0:
                break
            ariaDownloader.download(url,route,"%s.%s" % (page, url.split(".")[-1]))
            page += 1

    def getImageUrls(self,export=False):
        imgs =[]
        page = 1
        while True:
            url = self.findImg(page)
            if len(url) == 0:
                break
            imgs.append(url)
            page +=1
        if export:
            route = os.path.join(saveroute, self.title)
            if not os.path.exists(route):
                os.makedirs(route)
            with open(os.path.join(route,"images.txt"),"w+",encoding="utf8") as f:
                f.write("[Title:%s]\n" % self.title)
                f.write("[Total Page:%s]\n" % len(imgs))
                f.writelines(map(lambda x:"".join([x,"\n"]),imgs))
        return imgs