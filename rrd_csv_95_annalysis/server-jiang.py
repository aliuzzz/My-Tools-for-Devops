import requests
import urllib3

myurl = 'server酱ip地址.send'

def read_txt(path):
    '''
    读取文件
    '''

    with open(path, 'r', encoding='utf-8') as f:
        txt = f.read()
        print(txt)
    return txt

def pust_txt(text, desp):
    '''
    发送消息
    '''

    url = myurl
    data = {
        'text': text,
        'desp': desp
    }
    urllib3.disable_warnings()
    requests.post(url, data=data,verify=False)
    
pust_txt('发送的名字', read_txt('待发送的文件路径'))