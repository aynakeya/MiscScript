import random
import requests
import json
import string
import re

api = 'http://api.bilibili.com/x/share/click'

def random_buvid():
    return ''.join(random.choices(string.digits+string.ascii_letters, k=32))+'infoc'

# https://github.com/Cesium01/b23tvGenerator
def get_b23of(long_url):
    data = {
        'build': '6500300',
        'buvid': random_buvid(),
        'oid': long_url,
        'platform': 'android',
        'share_channel': 'COPY',
        'share_id': 'public.webview.0.0.pv',
        'share_mode': '3'
    }
    res = requests.post(api, data=data, timeout=9)
    data = json.loads(res.content)
    if data['data'].__contains__('content'):
        return data['data']['content']
    else:
        print("get b23.tv short link failed",json.dumps(data))
        return ""

def fake_link(mask_bv,target):
    if re.match("BV[0-9A-Za-z]+",mask_bv) == None:
        print("please enter proper mask bv")
        return ""
    if re.match("BV[0-9A-Za-z]+",target):
        return "https://b23.tv/%s/../%s" % (mask_bv,target)
    uri = get_b23of(target)
    if uri == "":
        print("please enter valid bilibili url")
        return
    return "https://b23.tv/%s/../%s" %(mask_bv,uri.split("/")[-1])
