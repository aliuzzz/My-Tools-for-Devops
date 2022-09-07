
import threading
import os
import pandas as pd

def run(ip):
    result=os.popen('mtr -r -c 10 -n  %s'%ip).read()
    print(result)
num_list = {}
df = pd.read_csv('mtr\py_mtr\mtr.csv')

t1=threading.Thread(target=run,args=("123.234.23.23",))#创建线程1
t2=threading.Thread(target=run,args=("123.234.24.24",))#创建线程2
#并发执行一共只等2秒
t1.start()
t2.start()
