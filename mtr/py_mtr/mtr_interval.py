####################################################
###使用阻塞的方式，使线程结束之后进入睡眠等待下一次新开始
####################################################

import os
import time
import threading
import pandas as pd
from datetime import date
from concurrent.futures import ThreadPoolExecutor

df = pd.read_csv('/mnt/mtr.csv')

today = date.today()
year = str(today.year)
year1 = str(today.year)
month = str(today.month)
month1 = str(today.month)
day = str(today.day)
hours = str(time.strftime('%H',time.localtime(time.time())))

#定义线程执行的函数
def run(ip,year,month,year1,month1,day,region,hours,discriptions):
    while True:
        result=os.popen('mtr -r -c 56 -n -i 0.5 %s >> /data/mtr/%s年%s月/%s年%s月%s日/%s/%s-%s.txt' %(ip,year,month,year1,month1,day,region,hours,discriptions)).read()
        #print(result)
        interval = 2  #等待时间为2秒
        time.sleep(interval) 

for i in range(len(df)):
    id = df.values[i, 0]    
    ip = df.values[i, 1]
    region = df.values[i, 2]
    discriptions = df.values[i, 3]
    path = "/data/mtr/"+str(year)+"年"+month+"月/"+year1+"年"+month1+"月"+day+"日/"+region+"/"
    if os.path.exists(path) == False:
        os.makedirs(path)
    threading.Thread(target=run,args=[ip,year,month,year1,month1,day,region,hours,discriptions,]).start()#线程开始

   