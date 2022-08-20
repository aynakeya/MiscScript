import sys,os,re

Exclude_Ext = [".py"]


Episode_Finder = re.compile(r"\[[0-9]{1,2}(\.[0-9]+)?(v[0-9]+)?\]")
Episode_Replacer = re.compile(r"[0-9]{1,2}(\.[0-9]+)?")

filenames = []

class Filename():
    def __init__(self,name):
        self.name = name
        self.replacer = {}

    def add_replacer(self,x,y):
        self.replacer[x] = y

    def get_filename(self):
        filename = self.name
        for key,value in self.replacer.items():
            filename = re.sub(key,value,filename)
        ep = Episode_Finder.search(filename)
        if ep != None:
            ep_str = ep.group()
            ep_num = Episode_Replacer.search(ep_str).group()
            v_str = ep_str.replace(ep_num,"",1)
            if v_str == "[]":
                final_str= "- %s " % (ep_num)
            else:
                final_str= "- %s %s" % (ep_num,v_str)
            filename = Episode_Finder.sub(final_str,filename)
        return filename


def print_change():
    max_len_1 = max(map(lambda x:len(x.name),filenames))
    max_len_2 = max(map(lambda x:len(x.get_filename()),filenames))
    for x in filenames:
        print(x.name.ljust(max_len_1),"==>",x.get_filename().ljust(max_len_2))

def add_replacer(f,t):
    for x in filenames:
        x.add_replacer(f,t)



cwd = os.getcwd()

if len(sys.argv) > 1:
    if os.path.isdir(sys.argv[1]):
        cwd = sys.argv[1]

print("Using Path:", cwd)

def rename():
    for x in filenames:
        try:
            os.rename(os.path.join(cwd,x.name),os.path.join(cwd,x.get_filename()))
        except Exception as e:
            pass


for x in os.scandir(cwd):
    if x.is_file():
        n,e = os.path.splitext(x.name)
        if e in Exclude_Ext:
            continue
        fn = Filename(x.name)
        filenames.append(fn)



print_change()

while True:
    f = input("from: ").strip("\n")
    if len(f) == 0:
        break
    t = input("to: ").strip("\n")
    add_replacer(f,t)
    print_change()

print("="*20,"final","="*20)

print_change()

input("Press Enter to Rename")

rename()


input("Ok!")
