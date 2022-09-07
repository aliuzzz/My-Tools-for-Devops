#### mtr多线程，以线程池的形式去进行执行。对cpu消耗和内存消耗较小，和普通的可以优先考虑。但interval方式目前的写法比较吃内存

import os
import time
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


def run(ip,year,month,year1,month1,day,region,hours,discriptions):
    result=os.popen('mtr -r -c 56 -n %s >> /data/mtr/%s年%s月/%s年%s月%s日/%s/%s-%s.txt' %(ip,year,month,year1,month1,day,region,hours,discriptions)).read()
    #print(result)
    
with ThreadPoolExecutor(max_workers=len(df)) as t:
    for i in range(len(df)):
        id = df.values[i, 0]    
        ip = df.values[i, 1]
        region = df.values[i, 2]
        discriptions = df.values[i, 3]
        path = "/data/mtr/"+str(year)+"年"+month+"月/"+year1+"年"+month1+"月"+day+"日/"+region+"/"
        if os.path.exists(path) == False:
            os.makedirs(path)
        args = [ip,year,month,year1,month1,day,region,hours,discriptions]
        t.submit(lambda p: run(*p),args)
