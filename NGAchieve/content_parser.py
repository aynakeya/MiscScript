import re


def md_escape(text:str):
    return text.replace("[","\[").replace("]","\]")

def html_character(content:str):
    return content.replace("<br/>","\n")

def ftag(content:str):
    content = content.replace("[del]","~~").replace("[/del]", "~~")
    content = content.replace("[b]", "**").replace("[/b]", "**")
    content = content.replace("<u>", "*").replace("</u>", "*")
    return content

def url_replace(content:str):
    reg_exp = re.compile(r"\[url(=(.*))?\]((?!\[url).)*\[/url\]")
    inner_reg = re.compile(r"\[url=((?!\[).)*\]")
    for match in reg_exp.finditer(content):
        url = match.group()
        inner_url = inner_reg.search(url)
        if inner_url is None:
            new_url = url[5:-6]
            text = new_url
        else:
            text = url[len(inner_url.group()):-6]
            new_url = inner_url.group()[5:-1]
        text = md_escape(text)
        if "read.php?tid=" in new_url and not new_url.startswith("http"):
            new_url = "https://bbs.nga.cn"+new_url
        content = content.replace(url,"[{}]({})".format(text,new_url))
    return content
def image_replace(content:str):
    reg_exp =re.compile(r"\[img\]((?!\[img\]).)*\[/img\]")
    for match in reg_exp.finditer(content):
        img = match.group()
        new_img = img[5:-6]
        if not new_img.startswith("http"):
            new_img = "http://img.nga.178.com/attachments"+ new_img[1:]
        img_format = "![{}]({})".format(new_img,new_img)
        content = content.replace(img,img_format)
    return content

def parse(content):
    if content is None:
        return ""
    if content == "":
        return ""
    content = html_character(content)
    content = image_replace(content)
    content = ftag(content)
    content = url_replace(content)
    return content