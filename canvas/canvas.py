class canvas(object):
    __slots__ = ("__height","__width","__title","__canvas","__dot","__author","__space")

    def __init__(self,height,width):
        self.__height = height
        self.__width = width
        self.__dot = "+"
        self.__title = "Untitled"
        self.__author = "Unkown"
        self.__space = ""
        self.initcanvas(" ")
        return

    def __str__(self):
        return "A Canvas Object-name:%s" % (self.__title)

    __repr__ = __str__

    def initcanvas(self,initstr):
        if initstr != None:
            initstr = str(initstr)
            if len(initstr) > 0 :
                self.__canvas = [[initstr for j in range(0, self.__width, 1)] for i in range(0, self.__height, 1)]
            else:
                print("Can't Be A Blank String!")
        else:
            print("Can't Be None")
        return

    def output(self):
        for i in range(0, self.__height, 1):
            for j in range(0, self.__height, 1):
                print(self.__canvas[i][j], self.__space, sep="", end="")
            print("")
        return

    def present(self):
        print("%s" % self.__title)
        self.output()
        print("Author: %s" % self.__author)
        return

    def drawdot(self,x,y):
        try:
            self.__canvas[x - 1][y - 1] = self.__dot
        except :
            print("Error")
        return

    def cleardot(self,x,y):
        try:
            self.__canvas[x-1][y-1] = " "
        except:
            print("Error")
        return

    @property
    def space(self):
        return self.__space

    @space.setter
    def space(self, space):
        self.__space = str(space)
        return

    @property
    def dot(self):
        return self.__dot

    @dot.setter
    def dot(self, dot):
        self.__dot = str(dot)
        return

    @property
    def author(self):
        return self.__author

    @author.setter
    def author(self, author):
        self.__author = str(author)
        return

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, name):
        self.__title = name
        return
