import base64
import binascii
import json
import os.path
from urllib.parse import urlparse

import aria2p
import tqdm
import time
import random
from dataclasses import dataclass
from typing import List

import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad


def decrypt_win_url(encrypted_url):
    key = binascii.unhexlify('aaad3e4fd540b0f79dca95606e72bf93')
    encrypted_url = encrypted_url.replace('_', '/').replace('-', '+')
    padding = '=' * (-len(encrypted_url) % 4)
    encrypted_message = base64.b64decode(encrypted_url + padding)
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_message = cipher.decrypt(encrypted_message)
    return unpad(decrypted_message, AES.block_size).decode('utf-8')


@dataclass
class TrackInfo:
    track_id: int
    title: str
    album_title: str
    author: str
    quality_level: int
    download_url: str
    cover_url: str

    @property
    def file_extension(self):
        # parse url and get last path, and get extension
        uri = urlparse(self.download_url)
        return "."+uri.path.split(".")[-1]

    @property
    def filename(self):
        return f"{self.title}{self.file_extension}"



class XimalayaDownloader:
    DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ????/4.0.4 Chrome/102.0.5005.167 Electron/19.1.1 Safari/537.36 4.0.4"

    def __init__(self, proxy_list=None, ua=DEFAULT_UA):
        self.ua = ua
        self.proxy_list: List[str] = [] if proxy_list is None else proxy_list

    def get_download_api(self, track_id, quality_level=2):
        return f"https://mobile.ximalaya.com/mobile/download/v2/track/{track_id}/ts-{int(time.time() * 1000)}?trackId={track_id}&device=win32&trackQualityLevel={quality_level}"

    def get_album_track_ids(self, album_id, page=1, page_size=30):
        result = httpx.get(f"https://pc.ximalaya.com/simple-revision-for-pc/play/v1/show?id={album_id}&num={page}&sort=0&size={page_size}&ptype=0").json()
        return [track['trackId'] for track in result['data']['tracksAudioPlay']]

    def get_album_tracks(self, album_id):
        ids = []
        for i in range(1,200):
            result = self.get_album_track_ids(album_id, i, 30)
            if len(result) == 0:
                break
            ids.extend(result)
        return ids

    def get_download_info(self, track_id, quality_level=2) -> TrackInfo:
        proxy = None
        if len(self.proxy_list) > 0:
            # random select a proxy
            proxy = self.proxy_list[random.randint(0, len(self.proxy_list) - 1)]
        result = httpx.get(self.get_download_api(track_id, quality_level),
                           headers={
                               "User-Agent": self.ua,
                               "Origin": "https://mobile.ximalaya.com",
                               "Referer": "https://mobile.ximalaya.com",
                           },
                           cookies={
                               "install_id": "126c0443-3613-48d0-b89c-909cff1cb3a3",
                               "channel": "99&100002",
                               "1&_device": "win32&126c0443-3613-48d0-b89c-909cff1cb3a3&4.0.4",
                               "1&remember_me": "y",
                               "1&_token": "YOUR_FUCKING_TOKEN",
                               "v1": "8ffgX.NpKV>%$EX4#*j7"
                           },
                           proxy=proxy
                           ).json()
        print(result)
        return TrackInfo(track_id=track_id,
                         title=result['data']['title'],
                         album_title=result['data']['albumTitle'],
                         author=result['data']['nickname'],
                         quality_level=result['data']['downloadQualityLevel'],
                         download_url=decrypt_win_url(result['data']['downloadAacUrl']),
                         cover_url=result['data']['coverLarge'])


downlaoder = XimalayaDownloader(proxy_list=None)

aria2 = aria2p.API(
    aria2p.Client(
        host="http://localhost",
        port=16800,
        secret=""
    )
)

# if track_ids.txt exists, load it
if os.path.isfile("track_ids.txt"):
    result = json.loads(open("track_ids.txt").read())
else:
    result = downlaoder.get_album_tracks(38987600)
    with open("track_ids.txt", "w") as f:
        f.write(json.dumps(result))
# result = downlaoder.get_album_track_ids(38987600, 1, 30)
start_index = 1607
pbar = tqdm.tqdm(result)
for idx,track_id in enumerate(pbar):
    if idx < start_index:
        continue
    pbar.set_description("Push to aria2")
    try:
        track = downlaoder.get_download_info(track_id, 2)
    except Exception as e:
        print(f"Failed, at index={idx}, track_id={track_id}, error={e}")
        break
    aria2.add_uris([track.download_url], options={
        "dir": "/home/aynakeya/Downloads/ximalaya/",
        "out": track.filename,
    })
    not_complete = sum([1 for d in aria2.get_downloads() if not d.is_complete])
    while not_complete > 30:
        time.sleep(1)
        not_complete = sum([1 for d in aria2.get_downloads() if not d.is_complete])
        pbar.set_description(f"Waiting")

# print(downlaoder.get_download_info(317293547, 2))
