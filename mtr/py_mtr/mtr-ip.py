import pymysql,os,time,threading,subprocess
from dbutils.pooled_db import PooledDB
from datetime import datetime
TIME_INTERVAL = 60

# 创建连接池
POOL = PooledDB(
    creator=pymysql,  # 使用要连接的数据库模块
    maxconnections=100,  # 允许的最大连接数
    mincached=2,
    maxcached=5,
    maxshared=3,
    blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True等待。
    maxusage=None,  # 一个连接最多被重复使用的次数，None表示无限制
    setsession=[],  # 开始会话前执行的命令列表
    ping=0,
    host='ip',
    port=3306,
    user='xxxx',
    password='xxxxxx',
    database='mtr',
    charset='utf8'
)

now = datetime.now()
year = now.year
month = now.month 
day = now.day
hour = now.hour

def run(ip,date,region,company,discriptions):
    try:
        file_path = f"/data/mtr/{date.year}年{date.month}月/{year}年{date.month}月{date.day}日/{region}/{company}/{date.hour}-{discriptions}.txt"
        cmd = f'echo "------------------------------------------------------------------------------" >> {file_path}' \
            f' && /usr/sbin/mtr -r -i 0.5 -c 60 -n {ip} >> {file_path}'
        result = subprocess.call(cmd, shell=True)
    except Exception as e:
        print(f"Error running subprocess: {e}")

def my_job():
    date = datetime.now()
    # 从连接池获取连接 
    conn = POOL.connection()        
    cursor = conn.cursor()

    try:
        sql_count = "SELECT COUNT(*) FROM mtr_company"
        sql_mtr_info = "SELECT ip, region, room, description FROM mtr_company"
        cursor.execute(sql_count)
        count = cursor.fetchone()[0]
        mtr_interval = TIME_INTERVAL / count
        cursor.execute(sql_mtr_info)
        mtr_info = cursor.fetchall()

        for row in mtr_info:
            ip = row[0]
            region = row[1]
            room = row[2]
            description = row[3]
            path = f"/data/mtr/{date.year}年{date.month}月/{date.year}年{date.month}月{date.day}日/{region}/{room}/"
            if not os.path.exists(path):
                os.makedirs(path)
            threading.Thread(target=run, args=(ip,date,region,room,description)).start()
            time.sleep(mtr_interval)
    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    while True:
        my_job()
