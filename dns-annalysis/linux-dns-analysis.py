from calendar import month
import os
import re
import os.path #文件夹遍历函数  
from time import sleep
import datetime

now_time = datetime.datetime.now()
year =str(now_time.strftime('%Y'))
month1 =str(now_time.strftime('%m'))
day =str(now_time.strftime('%d'))

#拼接
def pinjie():
    #获取目标文件夹的路径
    filedir = '/data/mtr/'+year+'年'+month1+'月/'+year+'年'+month1+'月'+day+'日/域名测试/华为域名测试'
    if not os.path.exists(filedir):
        os.makedirs(filedir)
    filenames=os.listdir(filedir)#获取当前文件夹中的文件名称列表
    #打开当前目录下的result.txt文件，如果没有则创建
    dirs = '/data/mtr/'+year+'年'+month1+'月/'+year+'年'+month1+'月'+day+'日/域名测试/华为域名测试结果'
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    sleep(1)
    f=open('/data/mtr/'+year+'年'+month1+'月/'+year+'年'+month1+'月'+day+'日/域名测试/华为域名测试结果/result.txt','w')
    #先遍历文件名
    for filename in filenames:
        filepath = filedir+'/'+filename
        #遍历单个文件，读取行数
        for line in open(filepath):
            f.writelines(line)
        f.write('\n')
    #关闭文件
    f.close()
    sleep(5)
    print("拼接完成")

#统计数
def tongji(file_path):
    global count
    log = open(file_path, 'r')
    C = r'\.'.join([r'\d{1,3}']*4)
    find = re.compile(C)
    count={}
    for i in log:
        for ip in find.findall(i):
            count[ip] = count.get(ip,1) + 1
            
if __name__ == '__main__':
    pinjie()
    num = 0
    #tongji(r'/data/mtr/'+year+'年'+month1+'月/'+year+'年'+month1+'月'+day+'日/测试/result.txt')
    tongji(r'/data/mtr/'+year+'年'+month1+'月/'+year+'年'+month1+'月'+day+'日/域名测试/华为域名测试结果/result.txt')
    R=count.items()
    #with open('/data/mtr/'+year+'年'+month1+'月/'+year+'年'+month1+'月'+day+'日/测试/result2.txt','a') as file0:
    with open('/data/mtr/'+year+'年'+month1+'月/'+year+'年'+month1+'月'+day+'日/域名测试/华为域名测试结果/result2.txt','a') as file0:
        for i in R:
            if i[1] > 0:
                print(i,file=file0)
                num+=1
    print('符合数量: %s'%(num))