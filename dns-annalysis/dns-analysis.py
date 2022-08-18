import re
import os
import sys
import time
from qqwry import QQwry

# 归属地数据文件路径
HOME_DAT_PATH = 'qqwry.dat'
# 输入文件路径
SOURCE_PATH = 'D:/Users/Worker/Desktop/yuliao/测试'
# 输出文件路径
RESULT_PATH = SOURCE_PATH + '结果'

RESULT_1_PATH = RESULT_PATH + '/result.txt'
RESULT_2_PATH = RESULT_PATH + '/result2.txt'

def get_result():
    '''功能: 汇总目录下所有result.txt的内容'''
    filenames = os.listdir(SOURCE_PATH)
    res = ''
    for filename in filenames:
        file_path = SOURCE_PATH + '/' + filename
        with open(file_path, 'r') as f:
            text = re.sub(r'^S.*\n?^A.*\n?', '', f.read(), flags=re.MULTILINE)
            res = res + text + '\n'
    return res

def gen_result(res, res_2):
    ''' 传入: result原始内容
        生成: result汇总文件 '''
    if not os.path.exists(RESULT_PATH):
        os.makedirs(RESULT_PATH)
    with open(RESULT_1_PATH, 'w') as f:
        f.write(res)
    with open(RESULT_2_PATH, 'a+') as f:
        f.write(res_2) 
    
def get_ip_list(res):
    ''' 传入: 文件路径
        返回: ip列表 '''
    return re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', res)

def count_ip(li):
    ''' 传入: ip列表
        返回: 包含ip出现次数的字典 '''
    di = {}
    for i in li:
        if i not in di:
            di[i] = 1
        else:
            di[i] += 1
    return di

def find_home(ip):
    ''' 传入: 单个ip地址
        返回: 归属地 '''
    query = QQwry()
    query.load_file(HOME_DAT_PATH)
    res = query.lookup(ip)
    home = res[0] + res[1]
    return home

def add_home(di):
    ''' 传入: ip字典
        返回: 带归属地的格式化文本 '''
    line = '--------------------------------------------------\n'
    text = line + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '\n' + line
    for ip, count in di.items():
        home = find_home(ip)
        text = text + '("' + ip + '", ' + home + ', 访问次数：' + str(count) + ')' + '\n' 
    return(text)

if __name__ == '__main__':

    result = get_result()

    ip_list = get_ip_list(result)

    ip_dict = count_ip(ip_list)

    result_2 = add_home(ip_dict)

    gen_result(result, result_2)
    