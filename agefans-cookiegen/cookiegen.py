import math
import re
import time

import requests


def getcookie(t1:int):
    time_now = int(time.time()*1000)
    print("t1 is %d, now is %s, t1-time_now = %d"%(t1,time_now,t1-time_now))
    t1_tmp = math.floor(t1 / 1000 + 0.5) >> 0x5
    k2 = (t1_tmp * (t1_tmp % 0x1000) * 0x3 + 0x1450f) * (t1_tmp % 0x1000) + t1_tmp
    t2 = time_now
    k2_s = str(k2)
    t2_s = str(t2)
    t2_s = t2_s[:-1:]+k2_s[-1]
    print("k2=%s" % k2_s)
    print("t2=%s" % t2_s)
    return {"t2":t2_s,"k2":k2_s}

url = "https://www.agefans.vip/_getplay?aid=20210249&playindex=2&epindex=1"
data = requests.head(url,headers={"referer":"https://www.agefans.vip/",})
print(data)
setcookies = data.headers.get("set-cookie")
print(setcookies)
t1 = int(re.compile(r"t1=[^;]*;").search(setcookies).group()[3:-1:])
print(t1)
cookies = getcookie(t1)
cookies["t1"] = str(t1)
data = requests.get(url,headers={"referer":"https://www.agefans.vip/",},cookies=cookies)
print(data.text)