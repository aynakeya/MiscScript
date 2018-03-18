from functools import reduce

b = ["ABC","ACBSD","ASFASDG","SDAAJTHRD","FGDSAS","LGGSDF"]

"""
one way to align the word.
e.g.
hello ==> 5 letter
change into 7 letter
newstr("hello",7) ==> "hel  lo"
"""
def newstr(oldstr,length):
    if len(oldstr) >= length:
        return oldstr
    else:
        binstr = str(oldstr.encode("utf-8"))
        blank = length-len(oldstr)
        spacenum = len(oldstr)-1
        return ("  "*(blank//spacenum)).join(list(oldstr))+(" "*(blank%spacenum))

"""
one way to align the word.
e.g.
hello ==> 5 letter
change into 7 letter
newstr1("hello",7) ==> "he l lo"

the result of list b 

A   B   C
A C B S D
ASF A SDG
SDAAJTHRD
FG D S AS
LG G S DF

"""
def newstr1(oldstr,length):
    if len(oldstr) >= length:
        return oldstr
    else:
        blank = length - len(oldstr)
        spacenum = len(oldstr) - 1
        blanks = [(blank // spacenum) for i in range(spacenum)]
        for i in range(blank % spacenum):
            blanks[i] += 1
        upstr = blanks[1::2]
        upstr.reverse()
        return reduce(lambda x,y:x+y,map(lambda x,y:x+y*" ",list(oldstr),upstr+blanks[0::2]+[0]))


