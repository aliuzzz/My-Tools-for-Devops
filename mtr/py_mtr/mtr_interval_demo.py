###阻塞模式 多线程mtr的demo，只读了ip，执行的为mtr -r -c 10 -n ip

import os
import time
import threading
import pandas as pd

def run(ip, interval = 10):
    while True:
        result=os.popen('mtr -r -c 10 -n  %s'%ip).read()
        print(result)
        time.sleep(interval) # 让线程睡眠指定时间

df = pd.read_csv('mtr.csv')

for i in range(len(df)):
    ip = df.values[i, 1]
    threading.Thread(target=run,args=(ip,)).start()