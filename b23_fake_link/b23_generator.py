import httpx


resp = httpx.post("https://api.bilibili.com/x/intl/share/click",
    params = {"build": "67900000", 
    "buvid": "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF", 
    "platform": "whateveryouwant", 
    "share_channel": "whateveryouwant", 
    "share_id": "public.webview.0.0.pv", 
    "share_mode": "233", 
    "oid": "https://live.bilibili.com/7777?spm_id_from=333.1007.0.0"})

print(resp.json())