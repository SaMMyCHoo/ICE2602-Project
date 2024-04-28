from flask import Flask,render_template,request,redirect,url_for
import SearchFiles
import tkinter as tk
import picMatch
from tkinter import filedialog
app=Flask(__name__)

keys=[]
@app.route('/search',methods=["POST","GET"])
def search():
    content=request.args.get('keyword')
    return render_template("search.html",content=content)

@app.route('/',methods=["POST","GET"])
def orin():
    return render_template('orin.html')
@app.route('/delete')
def delete():
    global keys
    keys=[]
    return render_template('history.html',keys=keys)
# @app.route('/response')
# def response():
#     content=request.args.get('keyword')
#     keys.append(content)
#     all_elem=SearchFiles.search(content)
#     return render_template("response.html",all_elem=all_elem,content=content)
@app.route('/judge',methods=["POST","GET"])
def judge():
    way=request.args.get('searchway')
    content=request.args.get('keyword')
    keys.append(content)
    if way=='0':
        all_elem=SearchFiles.search(content,0)
        length=len(all_elem)
        return  render_template('response.html',all_elem=all_elem,content=content,length=length)
    elif way=="1":
        all_elem=SearchFiles.search(content,1)
        length=len(all_elem)
        return render_template('time_response.html',all_elem=all_elem,content=content,length=length)
    else:
        all_elem=SearchFiles.search(content,2)
        length=len(all_elem)
        return render_template('classify_response.html',all_elem=all_elem,content=content,length=length)
@app.route('/show',methods=["POST","GET"])
def show():
    return render_template('history.html',keys=keys)

@app.route('/img_response')
def img_response():
    url=request.args['imageurl']
    result=picMatch.findmatch(url)
    length=len(result)
    return render_template('img_response.html',result=result,length=length,url=url)

    
if __name__=="__main__":
    app.run(debug=True,port=8080)