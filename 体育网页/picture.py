import time
import re
import os
import string
import requests
from bs4 import BeautifulSoup
import numpy as np
import torch
import torchvision
import torchvision.transforms as transforms
from torchvision.datasets.folder import default_loader
if not os.path.exists('pics'):
    os.mkdir('pics')
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
def img2feature(imgpath):
    ta_img=default_loader(imgpath)
    ta_img=torch.unsqueeze(trans(ta_img), 0)
    return alex_features(ta_img).detach().numpy()

def url2feature():
    ids=os.listdir('html')
    for id in ids:
        p='_2'
        if(p in id):
            urlid=int(id.split('_')[0])
            folder="pics/{}".format(urlid)
            with open("html/"+id,"r") as f0:
                srcs = f0.read().split("\n")
                cnt=0
                for now in range(len(srcs)//2-1,len(srcs)):
                    if(cnt>1):
                        break
                    try:
                        src=srcs[now]
                        img=requests.get(src)
                        with open('1.jpg','wb') as f:
                            f.write(img.content)
                        feature=img2feature('1.jpg')
                        cnt+=1
                        if not os.path.exists(folder):
                            os.mkdir(folder)
                        np.save(folder+'/{}.npy'.format(cnt), feature)
                    except:
                        pass
url2feature()