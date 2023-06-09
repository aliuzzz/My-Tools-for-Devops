#mtr实时监控终版，一分钟一条，读取mtr_company.csv,产生日志
import os
import time
import _thread
import hashlib
import logging
import subprocess
import pandas as pd

# 执行一次任务间隔时间
TIME_INTERVAL = 60
CSV_PATH = "/mtr/mtr_company.csv"

# 读取ip列表
df = pd.read_csv(CSV_PATH)
# 每条mtr命令时间间隔
mtr_interval = TIME_INTERVAL / len(df)
# 变量初始化
file_md5_last = 0

# 执行mtr命令
def run(ip,year,month,year1,month1,day,region,company,hours,discriptions):
    result = subprocess.call('echo "------------------------------------------------------------------------------" \
    >>/data/mtr/%s年%s月/%s年%s月%s日/%s/%s/%s-%s.txt && /usr/local/sbin/mtr -r -i 0.5 -c 60 -n %s >> /data/mtr/%s年%s月/%s年%s月%s日/%s/%s/%s-%s.txt' \
    %(year,month,year1,month1,day,region,company,hours,discriptions,ip,year,month,year1,month1,day,region,company,hours,discriptions), shell=True)

# 启动线程
def my_job():
    year = str(time.strftime('%Y',time.localtime(time.time())))
    year1 = str(time.strftime('%Y',time.localtime(time.time())))
    month = str(time.strftime('%m',time.localtime(time.time())))
    month1 = str(time.strftime('%m',time.localtime(time.time())))
    day = str(time.strftime("%d",time.localtime(time.time())))
    hours = str(time.strftime('%H',time.localtime(time.time())))
    for i in range(len(df)):
        ip = df.values[i, 1]
        region = df.values[i, 2]
        company = df.values[i, 3]
        discriptions = df.values[i, 4]
        path = "/data/mtr/"+str(year)+"年"+month+"月/"+year1+"年"+month1+"月"+day+"日/"+region+"/"+company+"/"
        if os.path.exists(path) == False:
            os.makedirs(path)
        _thread.start_new_thread(run, (ip,year,month,year1,month1,day,region,company,hours,discriptions,))
        
        # 设定每次mtr后休息时间
        time.sleep(mtr_interval)
        logging.basicConfig(
        filename='/var/log/mtr-ip.log',
        level=logging.DEBUG,
        format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]'
        )
        logging.debug('子线程'+str(i)+'开始执行！')
        #print(time.strftime('%H:%M:%S', time.localtime(time.time())),'子线程' + str(i) + '已启动')
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),'一次任务完成')
    logging.basicConfig(
        filename='/var/log/mtr-ip.log',
        level=logging.DEBUG,
        format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]'
        )
    logging.debug('一次任务完成！')

# 判断MD5值是否改变
def md5_changed():
    with open(CSV_PATH, 'rb') as fp:
        data = fp.read()
    file_md5_now = hashlib.md5(data).hexdigest()
    if file_md5_last != file_md5_now:
        file_md5_last = file_md5_now
        #print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),'修改csv')
        return True
    else:
        return False

if __name__ == '__main__':
    while True:
        my_job()   
        if md5_changed:
            df = pd.read_csv(CSV_PATH)


