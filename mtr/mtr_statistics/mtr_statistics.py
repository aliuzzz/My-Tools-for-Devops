#用于检查mtr中含有的丢包率，%号前不为0的，就打印出它的时间和文档名，方便巡检
import os
import re
import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

CSV_PATH = "/mtr/mtr_company.csv"
#读取ip列表
df = pd.read_csv(CSV_PATH)

#设置日期
now = datetime.datetime.now()
month_str = now.strftime("%Y年%m月")
date_str = now.strftime("%Y年%m月%d日")

def process_file(file_path, root):
    with open(file_path, "r") as f:
        lines = f.readlines()
        for i in range(1, len(lines)):
            if "Start" in lines[i]:
                #找到上一行的 %
                percentage_match = re.search(r"(\d+\.\d+)%", lines[i-2])
                #print(percentage_match.group(0)[:-1])
                if percentage_match:
                    percentage = percentage_match.group(0)[:-1]  #去掉 %
                    print(percentage)
                    if float(percentage) > 0:
                        #输出到 xunjian.txt
                        with open(os.path.join(root, "xunjian.txt"), "w+") as xunjian_file:
                            xunjian_file.write(lines[i-1])
                            xunjian_file.write(lines[i])
                            xunjian_file.write(lines[i-2])
                            xunjian_file.write(f"{file_path}\n")
                else:
                    continue

def process_company(region, company):
    for root, dirs, files in os.walk(f"/tttt/mtr/{month_str}/{date_str}/{region}/{company}/"):
        for file in files:
            file_path = os.path.join(root, file)  #所有txt文件的路径
            process_file(file_path, root)

def main():
    with ThreadPoolExecutor(max_workers=200) as executor:
        futures = []
        for i in range(len(df)):
            region = df.values[i, 2]  #东北-吉林 。。。。
            company = df.values[i, 3]  #齐齐哈尔联通。。。。
            futures.append(executor.submit(process_company, region, company))
        for future in futures:
            future.result()

if __name__ == '__main__':
    main()
