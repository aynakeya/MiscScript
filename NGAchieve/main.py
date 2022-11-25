import json
import multiprocessing
import threading
import traceback

import sqlalchemy

import content_parser
from db import session, Post
from nga import NgaPost

tids = []

for post in session.query(Post.tid).group_by(Post.tid).all():
    tids.append(post.tid)

# tids = tids[:10]
tids.reverse()
tids = tids


def get_datas(tid):
    datas = []
    for post in session.query(Post).where(Post.tid == tid):
        datas.append(json.loads(post.data))
    return datas


def get_nga_post(tid):
    post = NgaPost.load(get_datas(tid))
    return post


def generate_md(tid_parts):
    for index, tid in enumerate(tid_parts):
        try:
            p = get_nga_post(tid)
            p.get_title()
            p.make_md()
            with open("mds/{}".format(p.get_title()), "w", encoding="utf-8") as f:
                f.write(p.make_md())
        except:
            traceback.print_exc()
            print(tid)


def make_mds():
    t1 = multiprocessing.Process(target=generate_md, args=(tids[0:1000],))
    t2 = multiprocessing.Process(target=generate_md, args=(tids[1000:2000],))
    t3 = multiprocessing.Process(target=generate_md, args=(tids[2000:3000],))
    t4 = multiprocessing.Process(target=generate_md, args=(tids[3000:4000],))
    t5 = multiprocessing.Process(target=generate_md, args=(tids[4000:5000],))
    t6 = multiprocessing.Process(target=generate_md, args=(tids[5000:6000],))
    t7 = multiprocessing.Process(target=generate_md, args=(tids[6000:7000],))
    t8 = multiprocessing.Process(target=generate_md, args=(tids[7000:8000],))
    t9 = multiprocessing.Process(target=generate_md, args=(tids[8000:9000],))
    t10 = multiprocessing.Process(target=generate_md, args=(tids[9000:],))
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    t7.start()
    t8.start()
    t9.start()
    t10.start()
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()
    t7.join()
    t8.join()
    t9.join()
    t10.join()

from urllib.parse import urljoin

if __name__ == "__main__":
    mdindex = []
    for index, tid in enumerate(tids):
        if index % 100 == 0:
            print(index)
        try:
            p = get_nga_post(tid)
            real_title = content_parser.md_escape(p.get_title_full())
            title = p.get_title()
            mdindex.append("[{}](mds/{})".format(real_title, title))
        except:
            traceback.print_exc()
    with open("index.md", "w", encoding="utf-8") as f:
        f.write("\n\n".join(mdindex))
