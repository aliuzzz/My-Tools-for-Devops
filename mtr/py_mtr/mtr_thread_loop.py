import os
import time
import threading
import pandas as pd
from datetime import date

df = pd.read_csv('mtr.csv')

today = date.today()
year = str(today.year)
year1 = str(today.year)
month = str(today.month)
month1 = str(today.month)
day = str(today.day)
hours = str(time.strftime('%H',time.localtime(time.time())))

#创建线程执行函数
#将mtr的结果生成/data/mtr/xxxx年xx月/xxxx年xx月xx日/region/时间-discriptions.txt
def run(ip,year,month,year1,month1,day,region,hours,discriptions):
    result=os.popen('mtr -r -c 56 -n %s >> /data/mtr/%s年%s月/%s年%s月%s日/%s/%s-%s.txt' %(ip,year,month,year1,month1,day,region,hours,discriptions)).read()

#创建循环，根据csv创建线程
for i in range(len(df)):
    id = df.values[i, 0]
    ip = df.values[i, 1]
    region = df.values[i, 2]
    discriptions = df.values[i, 3]
    path = "/data/mtr/"+str(year)+"年"+month+"月/"+year1+"年"+month1+"月"+day+"日/"+region+"/"
   #file_path = path+str(hours)+"-"+str(discriptions)
    if os.path.exists(path) == False:
        os.makedirs(path)
    threading.Thread(target=run,args=[ip,year,month,year1,month1,day,region,hours,discriptions,]).start()
