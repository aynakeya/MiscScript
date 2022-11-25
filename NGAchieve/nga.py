import json
import traceback

import requests

import content_parser
import jsonclass


class NgaPostInfo():
    def __init__(self):
        self.tid = None
        self.fid = None
        self.quote_from = None
        self.quote_to = None
        self.titlefont = None
        self.topic_misc = None
        self.author = None
        self.authorid = None
        self.subject = None
        self.type = None
        self.postdate = None
        self.lastpost = None
        self.lastposter = None
        self.replies = None
        self.lastmodify = None
        self.recommend = None
        self.tpcurl = None
        self.topic_misc_var = None
        self.parent = None


class NgaUser():
    def __init__(self):
        self.uid = None
        self.username = None
        self.credit = None
        self.medal = None
        self.reputation = None
        self.groupid = None
        self.memberid = None
        self.avatar = None
        self.yz = None
        self.site = None
        self.honor = None
        self.regdate = None
        self.mute_time = None
        self.postnum = None
        self.rvrc = None
        self.money = None
        self.thisvisit = None
        self.signature = None
        self.nickname = None
        self.bit_data = None


class NgaReply():
    ReplyMDFormat = "### \#{index} {subject} {username}({uid})\n\n\n" \
                    "Like: {like}\n\n" \
                    "{content}\n\n" \
                    "---"
    ReplyWithCommentMDFormat = "### \#{index} {subject} {username}({uid})\n\n\n" \
                               "Like: {like}\n\n" \
                               "{content}\n\n" \
                               "#### comments:\n\n" \
                               "{comments}\n\n" \
                               "---"
    ReplyCommentMDFormat = "{subject}-{username}(uid): {content}\n\n"

    def __init__(self):
        self.content = None
        self.alterinfo = None
        self.tid = None
        self.score = None
        self.score_2 = None
        self.postdate = None
        self.authorid = None
        self.subject = None
        self.type = None
        self.fid = None
        self.pid = None
        self.recommend = None
        self.follow = None
        self.lou = None
        self.content_length = None
        self.attachs = None
        self.comment_id = None
        self.from_client = None
        self.postdatetimestamp = None
        self.comment = None

    def make_md(self, index, users):
        self.content = str(self.content)
        user = users.get(str(self.authorid))
        if user is None:
            username = "unknown"
            userid = "unknown"
        else:
            username = user.username
            userid = user.uid
        if self.comment is not None:
            comment = [jsonclass.json_unmarshall(NgaReply, c) for c in self.comment.values()]
        else:
            comment = []
        comments = ""
        for c in comment:
            user = users.get(c.authorid)
            if user is None:
                u1 = "unknown"
                u2 = "unknown"
            else:
                u1 = user.username
                u2 = user.uid
            comments += self.ReplyCommentMDFormat.format(subject=c.subject,
                                                         username=u1,
                                                         uid=u2,
                                                         content=content_parser.parse(c.content))

        if comments == "":
            return self.ReplyMDFormat.format(index=index,
                                             subject=self.subject,
                                             username=username,
                                             uid=userid,
                                             like=self.recommend,
                                             content=content_parser.parse(self.content))
        else:
            return self.ReplyWithCommentMDFormat.format(index=index,
                                                        subject=self.subject,
                                                        username=user,
                                                        uid=userid,
                                                        like=self.recommend,
                                                        content=content_parser.parse(self.content),
                                                        comments=comments)


class NgaPost():
    def __init__(self):
        self.users = {}
        self.replys = []

    @classmethod
    def load(cls, datas: list):
        postself = cls()
        for data in datas:
            for uid, ud in data["data"]["__U"].items():
                postself.users[uid] = jsonclass.json_unmarshall(NgaUser, ud)
            for rdata in data["data"]["__R"].values():
                postself.replys.append(jsonclass.json_unmarshall(NgaReply, rdata))
        return postself

    def make_md(self):
        mds = ["## {subject}({tid})".format(subject=self.replys[0].subject,
                                            tid=self.replys[0].tid)]
        for index, reply in enumerate(self.replys):
            mds.append(reply.make_md(index, self.users))
        return "\n\n".join(mds)

    def get_title(self):
        return "{tid}.md".format(
            tid=self.replys[0].tid,
        )

    def get_title_full(self):
        user = self.users.get(str(self.replys[0].authorid))
        if user is None:
            username = "unknown"
            userid = "unknown"
        else:
            username = user.username
            userid = user.uid
        return "{subject}({tid}) - {user}(uid).md".format(subject=self.replys[0].subject,
                                                          tid=self.replys[0].tid,
                                                          user=username,
                                                          uid=userid)
