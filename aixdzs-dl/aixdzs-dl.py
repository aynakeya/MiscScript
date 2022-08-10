from queue import Queue
import requests
import time
import sys
import threading


api_base = "https://apicn.aixdzs.com/"
api_chapter = "https://apicn.aixdzs.com/chapter/%d/%d" # book_id, chapater_id
api_content = "https://apicn.aixdzs.com/content-ios/%d" # book_id
api_info = "https://apicn.aixdzs.com/book/%d" # book_id
api_cover = "https://img22.aixdzs.com/"


replacer = {"\u3000":"  "}

class BookChapter():
    def __init__(self,sep="\n"):
        self.name = ""
        self.content = ""
        self.sep=sep
    
    def out(self):
        return self.name + self.sep + self.content

class Book():
    def __init__(self,sep="\n\n"):
        self.id = 0
        self.title = ""
        self.author = ""
        self.cover = ""
        self.intro = ""
        self.chapter_count = 0
        self.chapters = []
        self.sep = sep

    def out(self):
        return "%s\n%s\n\n%s\n%s\n" % (self.title,self.author,self.intro,self.cover)+ self.sep + self.sep.join(c.out() for c in self.chapters)

def get_book(id:int):
    try:
        book = Book()
        book.id = id
        resp = requests.get(api_info % id).json()
        book.title = resp["title"]
        book.author = resp["author"]
        book.chapter_count = int(resp["chaptersCount"])
        book.cover = api_cover + resp["cover"]
        book.intro = resp["longIntro"]
        return book
    except:
        return None


def get_book_content_s(book:Book):
    print("单线程 章节数: %d" % book.chapter_count)
    for i in range(1,book.chapter_count+1,1):
        j = 0
        while j < 3:
            try:
                c = BookChapter()
                print(api_chapter % (book.id,i))
                resp = requests.get(api_chapter % (book.id,i)).json()
                c.name = resp["chapter"]["title"]
                c.content = resp["chapter"]["body"]
                book.chapters.append(c)
                break
            except KeyboardInterrupt:
                sys.exit(0)
                return
            except:
                print("fail to get",api_chapter % (book.id,i))
                time.sleep(1)
                j +=1

def _multi_thread_dl(q,book):
    while not q.empty():
        index = q.get()
        chap_id = index+1
        j = 0
        while j < 3:
            try:
                if chap_id % 100 == 0:                    
                    print(api_chapter % (book.id,chap_id))
                resp = requests.get(api_chapter % (book.id,chap_id)).json()
                book.chapters[index].name = resp["chapter"]["title"]
                book.chapters[index].content = resp["chapter"]["body"]
                q.task_done()
                break
            except KeyboardInterrupt:
                sys.exit(0)
                return
            except Exception as e:
                print("fail to get",api_chapter % (book.id,chap_id))
                print(e)
                time.sleep(1)
                j +=1
        if j == 3:
            print("get failed, exit",api_chapter % (book.id,chap_id))
            sys.exit(0)
    return True

def get_book_content(book:Book):
    print("多线程 章节数: %d" % book.chapter_count)
    q = Queue(maxsize=0)
    num_theads = 50
    for i in range(book.chapter_count):
        c = BookChapter()
        book.chapters.append(c)
        q.put(i)
    for i in range(num_theads):
        worker = threading.Thread(target=_multi_thread_dl, args=(q,book))
        worker.setDaemon(True)
        worker.start()
    q.join()

def download_book(book_id:int,out_name=""):
    b = get_book(book_id)
    if b == None:
        print("book id not valid")
        return
    print("标题: %s 作者: %s" % (b.title,b.author))
    get_book_content(b)
    if out_name == "":
        out_name = "%s-%s.txt" % (b.title,b.author)
    with open(out_name,"w",encoding="utf-8") as f:
        f.write(b.out())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("aixdz-dl.py book_id <outname>")
        sys.exit(0)
    book_id = int(sys.argv[1])
    print("download book id = %d" % book_id)
    outname = ""
    if len(sys.argv) >=3:
        outname = sys.argv[2]
    download_book(book_id,outname)

# download_book(50991)
# b = get_book(50991)
# print(b.title,b.author,b.chapter_count)
# get_book_content(b)
# print(b.chapters[0].out())
