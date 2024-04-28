
INDEX_DIR = "IndexFiles.index"

import sys, os, lucene,jieba

import math
from java.io import File
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.util import Version
from org.apache.pylucene.search.similarities import PythonSimilarity, PythonClassicSimilarity

"""
This script is loosely based on the Lucene (java implementation) demo class 
org.apache.lucene.demo.SearchFiles.  It will prompt for a search query, then it
will search the Lucene index in the current directory called 'index' for the
search query entered against the 'contents' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""

def get_date(s):
    s=s.split(' ')
    def isillegal(x):
        y=x[0]*10000+x[1]*100+x[2]
        return y<19000101 or y>20491231
    out=[int(x) for x in s]
    if(isillegal(out)):
        return [0,0,0]  
    return out
      

def run(searcher, analyzer,keyword,mode):
    result=[]
    keyword = jieba.lcut(keyword)
    for i in range(len(keyword)):
        if('不' in keyword[i])or(keyword[i]=='无')or(keyword[i]=='否'):
            keyword[i]='NOT'
        if('和'==keyword[i])or('与'==keyword[i])or(keyword[i]=='并')or(keyword[i]=='且'):
            keyword[i]='AND'
    command = ' '.join(keyword)
    print(command)
    if command == '':
        return result
    else:
        titles=[]
        print()
        print ("Searching for:", command)
        query = QueryParser("contents", analyzer).parse(command)
        scoreDocs = searcher.search(query, 50).scoreDocs
        print ("%s total matching documents." % len(scoreDocs))
        for i, scoreDoc in enumerate(scoreDocs):
            doc = searcher.doc(scoreDoc.doc)
            tmp = doc.get('content').split()
            keys=keyword
            words=[]
            for key in keys:
                fst=0
                found = False
                for i in range(len(tmp)):
                    if(tmp[i]==key):
                        fst=i
                        found=True
                        break
                if(found==True):
                    words += tmp[max(0,fst-3):min(fst+4,len(tmp))]+['……']
            if(doc.get('title') not in titles):
                titles.append(doc.get('title'))
                result.append((doc.get('url'),doc.get('title'),words,doc.get('keyword'),get_date(doc.get('date'))))

    if(mode==1):
        result.sort(key=lambda x:x[4][0]*10000+x[4][1]*100+x[4][2],reverse=True)
        return result
    if(mode==2):
        L=[]
        cnt=0
        keys=dict()
        for u in result:
            if(u[3] in keys.keys()):
                L[keys[u[3]]].append(u)
            if(u[3] not in keys.keys()):
                keys[u[3]]=cnt
                cnt+=1
                L.append([u])
        L.sort(key=lambda x:len(x),reverse=True)
        return L
    return result

def search(keyword,mode):
    Keys='''
    热火 活塞 马拉多纳 贝尔纳多 席尔瓦 凯尔特人 骑士 奇才 魔术 公牛	步行者 雄鹿	尼克斯 猛龙 山猫 老鹰 火箭 湖人	灰熊 森林狼	掘金 太阳 马刺 超音速 小牛 快船	开拓者	
    爵士 勇士 黄蜂 库里 沃尔 欧文 乐福 米切尔 奥拉迪波 麦科勒姆 塔图姆 戴维斯 阿德托昆博 卡尔 安东尼 唐斯 恩比德 戈贝尔 韦德 奥尼尔 姚明 诺维茨基 约基奇 东契奇
    字母哥 武切维奇 那不勒斯 托特纳姆热刺 摩纳哥 切尔西	巴黎圣日耳曼 马德里竞技 前锋 中锋 后卫 前腰 斯卡洛尼 德尚 大罗 小罗 卡塔尔 	
    巴塞罗那 拜仁慕尼黑 尤文图斯 皇家马德里 马竞 大巴黎 国米 巴萨 小罗 大罗 尤文 皇马 梅西 内马尔 姆巴佩 贝克汉姆 苏亚雷斯 阿尔瓦雷兹 恩佐 费尔南德斯 哈兰德 莱万 德布劳内 马内 贝利 小罗 大罗 魔笛 莫德里奇 马丁内斯 劳塔罗 卢卡库 世界杯 欧冠
    '''
    Keys=Keys.split()
    for Key in Keys:
        jieba.add_word(Key)
    STORE_DIR = "index"
    try:
        vm_env=lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    except:
        vm_env=lucene.getVMEnv()
    vm_env.attachCurrentThread()
    print ('lucene', lucene.VERSION)
    #base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    directory = SimpleFSDirectory(File(STORE_DIR).toPath())
    searcher = IndexSearcher(DirectoryReader.open(directory))
    # set a new similarity computing method
    analyzer = WhitespaceAnalyzer()#Version.LUCENE_CURRENT)
    result=run(searcher, analyzer,keyword,mode)
    del searcher
    return result