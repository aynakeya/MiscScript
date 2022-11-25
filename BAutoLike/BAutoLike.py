# 2020/10/31 Aynakeya
# auto like for usbdrive

import requests

def isOfficialClan(dynamic):
    uname = dynamic["user_profile"]["info"]["uname"].lower()
    suffix = ["official","offcial","officiai","挂科人风笛"]
    for s in suffix:
        if s in uname:
            return True
    return False

def httpGet(url, maxReconn=5, **kwargs):
    trial = 0
    while trial < maxReconn:
        try:
            return requests.get(url, timeout=5, **kwargs)
        except:
            trial += 1
            continue
    return None

def httpPost(url, maxReconn=5, **kwargs):
    trial = 0
    while trial < maxReconn:
        try:
            return requests.post(url, timeout=5, **kwargs)
        except:
            trial += 1
            continue
    return None

class SimpleDynamicLiker():
    likeApi = "https://api.vc.bilibili.com/dynamic_like/v1/dynamic_like/thumb"
    # newest 20 dynamic
    dynamicApi = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_new?type_list=268435455"

    def __init__(self, sdata):
        self.cookie = {"SESSDATA": sdata}
        self.current = 0
        self.filters = []

    def addFilter(self,fun):
        self.filters.append(fun)

    def getNew(self):
        resp = requests.get(self.dynamicApi,cookies=self.cookie)
        if resp == None:
            return []
        resp = resp.json()
        if resp["code"] == 0 and len(resp["data"]["cards"])>0:
            tmp = self.current
            self.current = resp["data"]["cards"][0]["desc"]["dynamic_id"]
            return [c["desc"] for c in resp["data"]["cards"] if c["desc"]["dynamic_id"] > tmp]
        return []

    def thumbUp(self,did):
        data = httpPost(self.likeApi,data={"up":"1","dynamic_id":did},cookies=self.cookie)
        if data == None:
            return -100,"Fail to get response"
        try:
            return data.json()["code"],data.json()["msg"]
        except:
            return -100,"Unknown Error"

    def checkFilter(self,dynamic):
        b = False
        for f in self.filters:
            b = b or f(dynamic)
        return b

    def likeNew(self):
        print("开始运行自动点赞，当前offset %s" %self.current)
        for dynamic in self.getNew():
            print("获取到新动态 %s, 发布者 %s" %(dynamic["dynamic_id"],dynamic["user_profile"]["info"]["uname"]))
            if self.checkFilter(dynamic):
                print("动态 %s 通过过滤，正在点赞"%dynamic["dynamic_id"])
                code,msg = self.thumbUp(dynamic["dynamic_id"])
                if code == 0:
                    msg = "成功"
                if code == -6:
                    msg = "未登录"
                print("点赞状态: %s - %s" %(code,msg))



