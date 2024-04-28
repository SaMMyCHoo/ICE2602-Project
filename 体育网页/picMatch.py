import time
import re
import os
import string
import cv2
from bs4 import BeautifulSoup
import urllib.request
import numpy as np
import torch
import torchvision
import torchvision.models
import torchvision.transforms as transforms
from torchvision.datasets.folder import default_loader

model = torchvision.models.alexnet(pretrained=True)

normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])
trans = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    normalize,
])
def alex_features(x):
    x=model.features(x)
    x=model.avgpool(x)
    return x

def url2feature(url):
    req = urllib.request.Request(url)
    res = urllib.request.urlopen(req)
    with res as response ,open('2.jpg','wb') as f:
        f.write(response.read())
        f.flush()
        f.close()

    taimg=default_loader('2.jpg')
    taimg=torch.unsqueeze(trans(taimg), 0)
    feature=alex_features(taimg)
    feature = feature.detach().numpy()
    return feature

def get_score(feature1,feature2):
    normalized1=feature1/np.linalg.norm(feature1)
    normalized2=feature2/np.linalg.norm(feature2)
    dist = np.linalg.norm(normalized1-normalized2)
    return dist

def img2feature(imgpath):
    ta_img=default_loader(imgpath)
    ta_img=torch.unsqueeze(trans(ta_img), 0)
    return alex_features(ta_img).detach().numpy()

def get_info(x,y):
    fc=open('html/{}_0.txt'.format(x),encoding='utf-8',errors='ignore')
    ss=fc.read().split('\n')
    if(len(ss)<2):
        return ('','','')
    url,title=ss[0],ss[1]
    fc.close()
    fc=open('html/{}_2.txt'.format(x),encoding='utf-8',errors='ignore')
    srcs=fc.read().split('\n')
    src=srcs[len(srcs)//2-1+y]
    fc.close()
    return (src,url,title)

def findmatch(url):
    npy=url2feature(url)
    scores=[]
    dir=os.listdir('pics')
    t=np.random.randint(0,13)
    while(t<len(dir)):
        tmp=dir[t]
        t+=13
        now=os.listdir('pics/{}'.format(tmp))
        if(len(now)==0):
            continue
        nps=[np.load('pics/{}/{}.npy'.format(tmp,_+1))for _ in range(len(now))]
        k=0
        for j in range(1,len(now)):
           if(get_score(npy,nps[j])<get_score(npy,nps[k])):
               k=j
        scores.append((tmp,k,get_score(npy,nps[k])))
    scores.sort(key=lambda x:x[2])
    ans=[]
    now=0
    while(now<len(scores)):
        if(scores[now][2]<1.2):
            ans.append(get_info(scores[now][0],scores[now][1]))
        else:
            break
        now+=1
    return ans