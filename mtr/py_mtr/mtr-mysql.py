#连接mysql数据库，将信息放到库中，这样n台设备读数据库即可，省掉了多台同步信息的问题
import pymysql
import os
import time
import _thread
import logging
import subprocess
# 执行一次任务间隔时间
TIME_INTERVAL = 60

def run(ip,year,month,year1,month1,day,region,company,hours,discriptions):
   result = subprocess.call('echo "------------------------------------------------------------------------------" \
   >>/data/mtr/%s年%s月/%s年%s月%s日/%s/%s/%s-%s.txt && /usr/sbin/mtr -r -i 0.5 -c 60 -n %s >> /data/mtr/%s年%s月/%s年%s月%s日/%s/%s/%s-%s.txt' \
   %(year,month,year1,month1,day,region,company,hours,discriptions,ip,year,month,year1,month1,day,region,company,hours,discriptions), shell=True)

#启动线程
def my_job():
    year = str(time.strftime('%Y',time.localtime(time.time())))
    year1 = str(time.strftime('%Y',time.localtime(time.time())))
    month = str(time.strftime('%m',time.localtime(time.time())))
    month1 = str(time.strftime('%m',time.localtime(time.time())))
    day = str(time.strftime("%d",time.localtime(time.time())))
    hours = str(time.strftime('%H',time.localtime(time.time())))
    # 建立数据库连接
    conn = pymysql.connect(host='ip',port='端口号",user='用户名',password='密码',db='数据库名')
    #获取游标
    cursor = conn.cursor()
    sql_count = "SELECT COUNT(*) FROM mtrtest" # 取表格总行数
    sql_mtr_info = "SELECT ip, region, room, description FROM mtrtest" #取表格信息
    cursor.execute(sql_count)
    count = cursor.fetchone()[0] #总行数
    mtr_interval = TIME_INTERVAL / count  #间隔
    cursor.execute(sql_mtr_info)
    #获取查询结果
    mtr_info = cursor.fetchall()
    cursor.close()
    conn.close()
    for row in mtr_info:
        ip = row[0]
        region = row[1]
        room = row[2]
        description = row[3]
        path = "/data/mtr/"+str(year)+"年"+month+"月/"+year1+"年"+month1+"月"+day+"日/"+region+"/"+room+"/"
        if os.path.exists(path) == False:
            os.makedirs(path)
        _thread.start_new_thread(run, (ip,year,month,year1,month1,day,region,room,hours,description,))
        #设定每次mtr后休息时间
        time.sleep(mtr_interval)
        logging.basicConfig(
        filename='/var/log/mtr-ip.log',
        level=logging.DEBUG,
        format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]'
        )
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),'一次任务完成')
    logging.basicConfig(
        filename='/var/log/mtr-ip.log',
        level=logging.DEBUG,
        format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]'
        )
    logging.debug('一次任务完成！')

if __name__ == '__main__':
    while True:
        my_job()