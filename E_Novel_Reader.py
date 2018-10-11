import requests
import ast, os, sys, threading, re


# 笔趣阁api
class E_Novel_Getter_Biquege():

    # 初始化api接口
    def __init__(self):
        self.searchapi = "https://sou.jiaston.com/search.aspx?key=%s&page=1&siteid=app"
        self.chaptersapi = "https://shuapi.jiaston.com/book/%s/"
        self.contentapi = "https://shuapi.jiaston.com/book/%s/%s.html"

    # 通过搜索接口返回搜索结果第一本书的id 与作者
    def getBookInfo(self, bookname, index=1):
        raw = requests.get(self.searchapi % bookname)
        raw.encoding = "utf-8"
        data = ast.literal_eval(raw.text.replace("\\/", "/"))
        if len(data["data"]) == 0 or len(data["data"]) < index or index <= 0:
            return None
        return (str(data["data"][index - 1]["Id"]), str(data["data"][index - 1]["Author"]))

    # 通过章节api接口获取书的所有章节
    def getBookChapters(self, bookid):
        raw = requests.get(self.chaptersapi % bookid)
        data = ast.literal_eval(raw.content[3:].decode())
        return data["data"]["list"]

    # 获取某一章的内容
    def getArticleContent(self, bookid, articleid):
        raw = requests.get(self.contentapi % (bookid, articleid))
        data = ast.literal_eval(raw.content[3:].decode())
        return data["data"]["content"]


# 阅读
class E_Novel_Reader():

    #初始化
    def __init__(self, getter, bookname):
        #使用的接口
        self.__getter = getter
        self.bookname = bookname
        self.bookid = None
        self.bookauthor = None
        self.bookchapters = []

        # 获取书本id
        self.__getBookInfo()
        self.__getChapaters()

    # 使用笔趣阁获取
    @classmethod
    def initBiquege(cls, bookname):
        return cls(E_Novel_Getter_Biquege(), bookname)

    # 调用笔趣阁api
    def __getBookInfo(self):
        info = self.__getter.getBookInfo(self.bookname)
        if info is None:
            return
        self.bookid = info[0]
        self.bookauthor = info[1]

    # 调用笔趣阁api
    def __getChapaters(self):
        if self.bookid is None:
            return
        self.bookchapters = self.__getter.getBookChapters(self.bookid)

    # 获取已有的卷名
    def getChapterName(self, juan=-1):
        try:
            return self.bookchapters[juan]["name"]
        except:
            return None

    # 获取已有章节信息
    def getArticleInfo(self, juan=-1, zhang=-1):
        try:
            return (self.bookchapters[juan]["list"][zhang]["id"], self.bookchapters[juan]["list"][zhang]["name"])
        except:
            return None

    # 通过章节信息（id）来获取内容
    # export代表是否输出文件
    def getArticleContent(self, juan=-1, zhang=-1, export=False):
        info = self.getArticleInfo(juan, zhang)
        if info is None:
            return None
        content = self.__getter.getArticleContent(self.bookid, info[0])
        if export:
            with open("%s_%s_%s_%s.txt" % (self.bookname, self.bookauthor, self.getChapterName(juan), info[1]), "w",
                      encoding="utf-8") as f:
                f.write("%s %s %s\n" % (self.bookname, self.getChapterName(juan), info[1]))
                f.write(content)
        return (info[1], content)

    def __createDirs(self):
        bookname = "_".join([self.bookname, self.bookauthor])
        try:
            os.mkdir(os.path.join(sys.path[0],bookname))
        except:
            pass
        for juan in self.bookchapters:
            chaptername = juan["name"]
            path = os.path.join(sys.path[0], bookname, chaptername)
            try:
                os.mkdir(path)
            except:
                pass

    def __Download(self, path, chaptername,index, zhang):
        print("开始下载:",zhang["name"])
        content = self.__getter.getArticleContent(self.bookid, zhang["id"])
        with open(os.path.join(path, "%s_%s.txt" % (index,self.setFileTitle(zhang["name"]))), "w", encoding="utf-8") as f:
            f.write("%s %s %s\n" % (self.bookname, chaptername, zhang["name"]))
            f.write(content)
            f.close()

    # 单进程下载
    def DownloadAll(self):
        n = 1
        self.__createDirs()
        bookname = "_".join([self.bookname, self.bookauthor])
        for juan in self.bookchapters:
            path = os.path.join(sys.path[0], bookname, juan["name"])
            for zhang in juan["list"]:
                if not os.path.exists(os.path.join(path, "%s.txt" % (self.setFileTitle(zhang["name"])))):
                    self.__Download(path,juan["name"],n,zhang)
                n += 1

    # 多线程下载
    def DownloadAll_Multi(self):
        n=1
        threads = []
        bookname = "_".join([self.bookname, self.bookauthor])
        self.__createDirs()
        for juan in self.bookchapters:
            path = os.path.join(sys.path[0], bookname, juan["name"])
            for zhang in juan["list"]:
                if not os.path.exists(os.path.join(path, "%s.txt" % (self.setFileTitle(zhang["name"])))):
                    # 将线程放入list中便于后续操作
                    t = threading.Thread(target=self.__Download, args=(path,juan["name"],n,zhang))
                    threads.append(t)
                n +=1

        #启动所有线程
        for t in threads:
            t.start()

        # 等待所有结束线程
        for t in threads:
            t.join()

    def setFileTitle(self, title):
        fileName = re.sub('[\/:*?"<>|]', '-', title)
        return fileName

if __name__ == "__main__":
    a = E_Novel_Reader.initBiquege("诡秘之主")
    try:
        a.DownloadAll_Multi()
    except:
        print("遇到了问题，请尝试重新运行程序")
