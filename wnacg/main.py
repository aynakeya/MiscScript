from model import bookModel,downloaders
from config import Config
import sys

if __name__ == "__main__":
    sid = int(input("enter start id: "))
    eid = int(input("enter start id: "))
    print("Choose your downloader")
    for d in downloaders.keys():
        print("* %s" %d)
    d = input("choose: ")
    if not d in downloaders.keys():
        print("No such downloader")
        sys.exit()
    dl = downloaders[d]()
    print("--------------------------------------")
    print("[Info] Download Start")
    for i in range(sid,eid+1):
        b = bookModel(i)
        print("[Info] book id %s: Getting information" %i)
        if not b.getInfo():
            print("[Fail] book id %s: can't get information, skip..." %i)
            continue
        if len(b.links) == 0:
            print("[Info] book id %s: no download links found, skip..." %i)
            continue
        if Config.export:
            b.export(Config.saveroute,Config.exportFile)
        print("[Info] book id %s: Downloading..." %i)
        dl.download(b.links[0],Config.saveroute,b.getFilename())
    print("[Info] Download End")