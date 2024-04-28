# SJTU EE208
INDEX_DIR = "IndexFiles.index"
import numpy as np
import re,sys, os, lucene, threading, time
import jieba
from datetime import datetime
from jieba.analyse import *
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, StringField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.pylucene.search.similarities import PythonSimilarity, PythonClassicSimilarity

Keys='''
热火 活塞 马拉多纳 贝尔纳多 席尔瓦 凯尔特人 骑士 奇才 魔术 公牛	步行者 雄鹿	尼克斯 猛龙 山猫 老鹰 火箭 湖人	灰熊 森林狼	掘金 太阳 马刺 超音速 小牛 快船	开拓者	
爵士 勇士 黄蜂 库里 沃尔 欧文 乐福 米切尔 奥拉迪波 麦科勒姆 塔图姆 戴维斯 阿德托昆博 卡尔 安东尼 唐斯 恩比德 戈贝尔 韦德 奥尼尔 姚明 诺维茨基 约基奇 东契奇
字母哥 武切维奇 那不勒斯 托特纳姆热刺 摩纳哥 切尔西	巴黎圣日耳曼 马德里竞技 前锋 中锋 后卫 前腰 斯卡洛尼 德尚 大罗 小罗 卡塔尔 	
巴塞罗那 拜仁慕尼黑 尤文图斯 皇家马德里 马竞 大巴黎 国米 巴萨 小罗 大罗 尤文 皇马 梅西 内马尔 姆巴佩 贝克汉姆 苏亚雷斯 阿尔瓦雷兹 恩佐 费尔南德斯 哈兰德 莱万 德布劳内 马内 贝利 小罗 大罗 魔笛 莫德里奇 马丁内斯 劳塔罗 卢卡库 世界杯 欧冠
'''
Keys=Keys.split()
for Key in Keys:
    jieba.add_word(Key)

class Ticker(object):

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)

class IndexFiles(object):
    """Usage: python IndexFiles <doc_directory>"""

    def __init__(self, root, storeDir):

        if not os.path.exists(storeDir):
            os.mkdir(storeDir)

        # store = SimpleFSDirectory(File(storeDir).toPath())
        store = SimpleFSDirectory(Paths.get(storeDir))
        analyzer = WhitespaceAnalyzer()
        analyzer = LimitTokenCountAnalyzer(analyzer, 1048576)
        config = IndexWriterConfig(analyzer)
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)

        # set a new similarity computing method
        config.setSimilarity(PythonClassicSimilarity())

        writer = IndexWriter(store, config)

        self.indexDocs(root, writer)
        ticker = Ticker()
        print('commit index')
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print('done')

    def indexDocs(self, root, writer):

        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.NONE)  # Not Indexed
        
        t2 = FieldType()
        t2.setStored(False)
        t2.setTokenized(True)
        t2.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)  # Indexes documents, frequencies and positions.

        def date(url):
            content = urllib.request.urlopen(url,timeout=1).read()
            soup = BeautifulSoup(content,features="html.parser")
            content=''.join(soup.findAll(text=True))
            result = re.findall(r"[0-9]{4}-[0-9]{1,2}-[0-9]{1,2}",content)
            if(result):
                return ' '.join(result[0].split('-'))
            result = re.findall(r"[0-9]{4}/[0-9]{1,2}/[0-9]{1,2}",content)
            if(result):
                return ' '.join(result[0].split('/'))
            return '0 0 0'
                      
        for root,dirnames,filenames in os.walk(root):
            k=0
            while(k*3<len(filenames)):
                i=k*3
                k+=1
                filename=filenames[i]
                now=filename.split('_')[0]
                print("adding Web Page No.{}...".format(now))
                try:
                    path =[os.path.join(root, filenames[j]) for j in range(i,i+3)]
                    file =[open(p,encoding='utf-8',errors='ignore') for p in path]
                    contents=[f.read() for f in file]
                    if(len(contents[0])==0):
                        continue
                    doc=Document()
                    info=contents[0].split('\n')
                    url=info[0]
                    day=date(url)
                    title=info[1] 
                    info=re.sub('[^\u4e00-\u9fa5]+','',contents[1])
                    words=jieba.lcut(info)
                    bug=['按钮','定向','跟帖','的','新浪','腾讯','图集','正文','标题','表单','跟贴','画中画']
                    s=''
                    for word in words:
                        if(word in bug):
                            continue
                        s+=word+' '
                    words=s 
                    '/'.join(s.split(' '))
                    keywords=jieba.analyse.extract_tags(s,topK = 1, withWeight = True)
                    if(len(url)>0):
                        doc.add(Field('url',url,t1))
                        if(len(title)>0):
                            doc.add(Field('title',title,t1))
                            if(len(words)>0):
                                doc.add(Field('keyword',keywords[0][0],t1))
                                doc.add(Field('date',day,t1))
                                doc.add(Field('content',words,t1))
                                doc.add(Field('contents',words,t2))
                    else:
                        print("warning: no content in %s" % "web {}".format(now))
                    writer.addDocument(doc)
                except Exception as e:
                    print("Failed in indexDocs:", e)
                    
                            
                
if __name__ == '__main__':
    lucene.initVM()#vmargs=['-Djava.awt.headless=true'])
    print('lucene', lucene.VERSION)
    # import ipdb; ipdb.set_trace()
    start = datetime.now()
    try:
        IndexFiles('html', "index")
        end = datetime.now()
        print(end - start)
    except Exception as e:
        print("Failed: ", e)
        raise e
