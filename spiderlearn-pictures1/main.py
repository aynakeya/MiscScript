import requests
from bookModel import book

maxbid = 1425
minbid = 1376
for bookid in range(minbid,maxbid):
    #input("Book No.%s press enter to continue...." % bookid)
    print("Book No.%s" % bookid)
    b = book(bookid)
    if b.status == 404:
        print("404",bookid)
        continue
    b.getImageUrls(export=True)
    #b.downBookAria()