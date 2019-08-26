from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait,A4,landscape
from PIL import Image
import os,time
route = r"downloads"
def getCommon(ws,hs):
    wd = {0:0}
    maxw = 0
    hd = {0:0}
    maxh = 0
    for w in ws:
        if w in wd:
            wd[w]+=1
            if wd[w] > wd[maxw]:
                maxw = w
        else:
            wd[w] = 1
    for h in hs:
        if h in hd:
            hd[h] +=1
            if hd[h] > hd[maxh]:
                maxh = h
        else:
            hd[h] = 1
    return maxw,maxh
def autoResize(maxw,maxh,img):
    w,h = img.size
    if w > maxw:
        h = round(h * (maxw/w))
        w = maxw
    if h > maxh:
        w = round(w+ (maxh/h))
        h = maxh

def img2pdf(route,fn,imgs):
    ws,hs = [],[]
    for img in imgs:
        try:
            im = Image.open(img)
            ws.append(im.size[0])
            hs.append(im.size[1])
        except:
            imgs.remove(img)
    maxw, maxh = getCommon(ws,hs)
    if not os.path.exists(route):
        os.makedirs(route)
    pdf = canvas.Canvas(os.path.join(route,fn),pagesize=portrait((maxw, maxh)))
    #pdf = canvas.Canvas(os.path.join(route, fn), pagesize=landscape(A4))
    for img in imgs:
        # preserveAspectRatio prevent picture from resizing anchor c put the image in the center if not fit to the pagesize
        pdf.drawImage(img,0,0,maxw,maxh,preserveAspectRatio=True,anchor='c')
        pdf.showPage()
    pdf.save()

if __name__ == "__main__":
    books = []
    for root, dirs, files in os.walk(route):
        books = dirs
        break
    for book in books:
        rt = os.path.join(route, book, "img")
        if not os.path.exists(rt):
            print(book)
            continue
        imgs = []
        for root, dirs, files in os.walk(rt):
            files.sort(key=lambda x: int(x.split(".")[0]))
            imgs = [os.path.join(rt, x) for x in files]
        if len(imgs) == 0:
            continue
        print("start",book)
        t1 = time.time()
        try:
            if os.path.exists(os.path.join(route,book,book+".pdf")):
                continue
            img2pdf(os.path.join(route,book),book+".pdf",imgs)
        except:
            print("Error",book)
        print("finish",time.time()-t1)


