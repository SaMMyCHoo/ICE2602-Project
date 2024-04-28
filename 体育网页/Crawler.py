import math
import threading
import time
import queue
import os
import re
import sys
import string
from tokenize import Ignore
import urllib.parse
import urllib.request
import jieba
from bs4 import BeautifulSoup

keys=['sport','nba','cba','fifa','football','basketball']

def trans(url):
    url=url.split('/')
    url=''.join(url)
    return url

urlset=set()

def check(url):
    tmp=trans(url)
    if(tmp in urlset):
        return False
    urlset.add(tmp)
    p=[re.compile('^https://www.msn.cn/zh-cn//sports^'),re.compile('^https://sports.sina.com.cn^')]
    for p0 in p:
        if(p0.match(url)==True):
            return True
    for key in keys:
        if(re.findall(key,url,re.I)):
            return True
    return False

def get_page(page):
    content=''
    try:
        content = urllib.request.urlopen(page,timeout=1).read()
    except:
        pass
    return content

def get_all_links(content, page):
    links = []
    try:
        soup = BeautifulSoup(content,features="html.parser")
        encode=soup.original_encoding
        for item in soup.findAll('a',{'href':re.compile('^http|^/')}):
            p = item.get('href','')
            try:
                now = urllib.parse.urljoin(page,p)
            except:
                pass
            if(check(now)):
                urlset.add(now)
                links.append(now)
        return links,encode
    except:
        return links,encode

def add_page_to_folder(page, content,nth,encode):
    index_filename = 'index.txt'  
    folder = 'html' 
    filename = "{}".format(nth)
    try:
        index = open(index_filename, 'a')
        index.write(page + '\t' + filename + '\n')
        index.close()
    except:
        pass
    if not os.path.exists(folder):
        os.mkdir(folder)
    f = open(os.path.join(folder, filename+'_0.txt'), 'w',encoding=encode)
    f1 = open(os.path.join(folder, filename+"_1.txt"), 'w',encoding=encode)
    f2 = open(os.path.join(folder, filename+"_2.txt"), 'w',encoding=encode)
    try:
        soup = BeautifulSoup(content,features="html.parser")
        title=soup.head.title.string
        txt='\n'.join(soup.findAll(text=True))
        imgset=[]
        for i in soup.findAll('img'):# 通过findAll函数找到所有img类型的标签
            if(i.get('src')!=None):# 如果存在src属性说明找到图片地址
                imgset.append(urllib.parse.urljoin(page,i.get('src')))
        pic='\n'.join(imgset)
        f.write(page+'\n')
        f.write(title+'\n')
        f1.write(txt+'\n')
        f2.write(pic+'\n')
        f.close()
    except:
        pass


def working():
    global Count
    global cnt,nth
    while (cnt<Count):
        page = q.get()
        if page not in crawled:
            content = get_page(page)
            if varLock.acquire():
                nth+=1
                varLock.release()
            outlinks,encode = get_all_links(content, page)
            add_page_to_folder(page, content,nth,encode)
            for link in outlinks:
                q.put(link)
            if varLock.acquire():
                cnt+=1
                crawled.append(page)
                varLock.release()
            q.task_done()
            

seed=['https://www.msn.cn/zh-cn//sports','https://sports.sina.com.cn/','https://new.qq.com/ch/sports/','https://new.qq.com/ch/nba/','https://sports.163.com/']
Count=20000
cnt=0
nth=1
start = time.time()
NUM = 20
crawled = []
varLock = threading.Lock()
q = queue.Queue()
for urls in seed:
    q.put(urls)
for i in range(NUM):
    t = threading.Thread(target=working)
    t.setDaemon(True)
    t.start()
for i in range(NUM):
    t.join()
end = time.time()
print(end - start)