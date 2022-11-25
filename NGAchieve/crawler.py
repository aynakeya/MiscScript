import json
import traceback

import requests



class NGAHttpClient():
    def __init__(self):
        self.nga_para = {"lite":"js"}
        self.nga_header = {
            'User-agent': 'Nga_Official/80023'}
        self.nga_cookies = {
            'ngaPassportUid': '62691713',
            'ngaPassportCid': 'X92h5p5bg7epu65vdqfo92osup08mihcsrn5283i',
        }
        self.trial = 3

    def get(self,url):
        t = 0
        while t < self.trial:
            try:
                data = requests.get(url,headers = self.nga_header,
                                    params=self.nga_para,
                                    cookies = self.nga_cookies)
                text = data.text\
                    .replace('	', '')\
                    .replace("window.script_muti_get_var_store=", "")\
                    .replace("\\\"","-a*b-")\
                    .replace("\\","")\
                    .replace("-a*b-","\\\"")
                return json.loads(text,strict=False)
            except:
                traceback.print_exc()
            t +=1
        return None

client = NGAHttpClient()
from db import session, Post


def _get_post_data(tid,page,pre):
    print(tid,page,pre)
    data = client.get("https://bbs.nga.cn/read.php?tid={}&page={}".format(tid,page))
    if data == None:
        session.commit()
        return
    try:
        if pre == data["data"]["__PAGE"]:
            session.commit()
            return
    except:
        session.commit()
        return
    session.add(Post(tid=tid,page=page,data=json.dumps(data)))
    _get_post_data(tid,page+1,data["data"]["__PAGE"])

def get_post_data(tid):
    if str(tid) == "17190139":
        return
    _get_post_data(tid,1,0)


def _get_recom_posts(page):
    print("page now {}".format(page))
    url = "https://bbs.nga.cn/thread.php?&recommend=1&fid=-34587507&admin=1&page={}".format(page)
    data = client.get(url)
    if data is None:
        return
    if data.get("error") is not None:
        return
    for _,val in data["data"]["__T"].items():
        get_post_data(val["tid"])
    _get_recom_posts(page+1)

def get_recom_post():
    _get_recom_posts(273)