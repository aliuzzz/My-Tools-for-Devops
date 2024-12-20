import pymysql
from dbutils.pooled_db import PooledDB
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import subprocess

TIME_INTERVAL = 60
MAX_WORKERS = 10  # 控制最大线程数

POOL = PooledDB(
    creator=pymysql, 
    maxconnections=100, 
    mincached=2,
    maxcached=5,
    maxshared=3,
    blocking=True,
    maxusage=None, 
    setsession=[], 
    ping=0,
    host='27.221.49.44',
    port=3306,
    user='root',
    password='QingDaoWx789',
    database='mtr',
    charset='utf8'
)
now = datetime.now()
year = now.year
month = now.month 
day = now.day
hour = now.hour
def run(ip, date, region, company, descriptions):
    try:
        file_path = f"/data/mtr/{date.year}年{date.month}月/{year}年{date.month}月{date.day}日/{region}/{company}/{date.hour}-{descriptions}.txt"
        cmd = f'echo "------------------------------------------------------------------------------" >> {file_path}' \
              f' && /usr/sbin/mtr -r -6 -i 0.3 -c 120 -n {ip} >> {file_path}'
        result = subprocess.call(cmd, shell=True)
    except Exception as e:
        print(f"Error running subprocess: {e}")

def my_job():
    date = datetime.now()
    
    conn = None
    cursor = None
    
    try:
        conn = POOL.connection()        
        cursor = conn.cursor()

        sql_count = "SELECT COUNT(*) FROM mtr_company"
        sql_mtr_info = "SELECT ip, region, room, description FROM mtr_company_zhisuantest"
        cursor.execute(sql_count)
        count = cursor.fetchone()[0]
        mtr_interval = TIME_INTERVAL / count
        cursor.execute(sql_mtr_info)
        mtr_info = cursor.fetchall()

        # 使用线程池
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            for row in mtr_info:
                ip = row[0]
                region = row[1]
                room = row[2]
                description = row[3]
                path = f"/data/mtr/{date.year}年{date.month}月/{date.year}年{date.month}月{date.day}日/{region}/{room}/"
                if not os.path.exists(path):
                    os.makedirs(path)
                
                executor.submit(run, ip, date, region, room, description)
                time.sleep(mtr_interval)

    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    while True:
        try:
            my_job()
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(1)

if __name__ == '__main__':
    main()
