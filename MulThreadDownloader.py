import threading, sys
import requests
import time
import os
import random

semlock = threading.BoundedSemaphore

# https://blog.csdn.net/drdairen/article/details/60962439

class MulThreadDownload(threading.Thread):
    def __init__(self, url, headers, startpos, endpos, f):
        super(MulThreadDownload, self).__init__()
        self.url = url
        self.headers = headers
        self.startpos = startpos
        self.endpos = endpos
        self.fo = f

        self.headers["Range"] = "bytes=%s-%s" % (self.startpos, self.endpos)

    def download(self):
        print("start thread:%s at %s" % (self.getName(), time.time()))
        res = requests.get(self.url, headers=self.headers)
        self.fo.seek(self.startpos)
        #print(len(res.content))
        #if self.startpos > 70641087:
        #    return
        self.fo.write(res.content)
        print("stop thread:%s at %s" % (self.getName(), time.time()))

    def run(self):
        while True:
            try:
                self.download()
                break
            except:
                pass


class MulThreadDownloader(object):
    def __init__(self,headers, cookie, threadnum=1):
        self.headers = headers
        self.cookie = cookie
        self.threadnum = threadnum


    def download(self, url):
        # 获取文件的大小和文件名
        filename = url.split("?")[0].split('/')[-1]
        filesize = int(requests.head(url,headers=self.headers).headers['Content-Length'])
        # 默认3线程现在，也可以通过传参的方式设置线程数
        step = filesize // self.threadnum
        mtd_list = []
        start = 0
        end = -1
        tempf = open(filename, 'w')
        tempf.close()
        with open(filename, 'rb+') as f:
            # 获取文件描述符
            fd = f.fileno()
            # 如果文件大小为11字节，那就是获取文件0-10的位置的数据。如果end = 10，说明数据已经获取完了。
            while end < filesize - 1:
                start = end + 1
                end = start + step - 1
                if end > filesize:
                    end = filesize
                # 复制文件句柄
                dup = os.dup(fd)
                # 创建文件对象
                fo = os.fdopen(dup, 'rb+', -1)
                t = MulThreadDownload(url, self.headers.copy(), start, end, fo)
                time.sleep(random.random()*0.5)
                t.start()
                mtd_list.append(t)
            print("----------------------------")
            for i in mtd_list:
                i.join()
