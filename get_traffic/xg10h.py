import os
import requests
import pymysql
import configparser

filename = '/root/xg_download/xg10h.txt'

config = configparser.ConfigParser()
config.read('/root/xg_download/xg_config.conf')

host = config['database']['host']
user = config['database']['user']
password = config['database']['password']  
db = config['database']['db']

api_url = config['api_info']['api_url']
key_name = config['api_info']['key_name']
key = config['api_info']['key']
video_name = config['api_info']['video_name']
status_value = config['video_type']['type']
mission_num = config['mission_num']['num']

# 连接数据库
conn = pymysql.connect(host=host, port=3306, user=user, password=password, database=db, connect_timeout=300)
cursor = conn.cursor()
query = f"SELECT url FROM get_traffic where status IN ({status_value}) ORDER BY RAND() LIMIT 1"
cursor.execute(query)
rows = cursor.fetchall()
conn.close()
url = rows[0][0]
api_url = f"{api_url}&{key_name}={key}&{video_name}={url}"
print(api_url)
res = requests.get(api_url).json()
if not os.path.isfile(filename):
    # 不存在时创建文件
    with open(filename, 'w') as f:
        pass
if res.get('code') == '0001':
    print('标题：' + res.get('data', {}).get('desc'))
    print('url:' + res.get('data', {}).get('playAddr'))
    with open('/root/xg_download/xg10h.txt', 'w') as f:
        f.write(f'{res.get("data", {}).get("desc", "")[:5]}.mp4\n{res.get("data", {}).get("playAddr")}\n')
    with open('/root/xg_download/get_traffic.sh','w') as f:
        f.write(f'#!/bin/sh\n')
        for _ in range(int(mission_num)):
            f.write("/usr/bin/screen -dmS mysession /usr/bin/go run /root/xg_download/xg10h.go\n")
            f.write("sleep 60\n")
    os.chmod('/root/xg_download/get_traffic.sh', 0o755)