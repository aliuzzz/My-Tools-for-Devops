import requests
import datetime
import time
from selenium import webdriver
import requests
import pandas as pd
import time
import os
from retrying import retry
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

#存放下载的csv文件的文件夹路径
FILE_PATH = 'xxxxxx'
#存放导出的csv文件的文件夹路径
OUTPUT_PATH = 'xxxxxx'


chrome_options = Options()
chrome_options.add_argument('--headless') 
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=chrome_options)
driver.get('http://ip/cacti')
user = 用户名
passwd = 密码

# 读当前文件夹下的xlsx文件，并将数据写入字典
df = pd.read_csv('threeshold.csv')
num_list = {}
for i in range(len(df)):
    num_list[df.iloc[i][0]] = [df.iloc[i][1],df.iloc[i][2],df.iloc[i][3]]

#清空文件夹
def clear_file():
    file_path = FILE_PATH
    for root, dirs, files in os.walk(file_path):
        for file in files:
            os.remove(os.path.join(root, file))

#登录并且下载csv表格和图片,添加重试机制，如果登录失败，则重新登录,直到成功
@retry
def selenium_login():
    #----------selenium登录------------------------------------------------
    zhanghu = driver.find_element(By.CSS_SELECTOR, '[name="login_username"]')
    mima = driver.find_element(By.CSS_SELECTOR, '[name="login_password"]')
    zhanghu.send_keys(user)
    mima.send_keys(passwd)
    driver.find_element(By.CSS_SELECTOR,'[value="Login"]').click()
    driver.find_element(By.CSS_SELECTOR,'[alt="Graphs"]').click()
    cookie = driver.get_cookies()
    print(cookie)
    
    cookie_str =''
    for cook in cookie:
        cookie_str +=cook.get('name')+'='+ cook.get('value')
               # if cook.get('name') == 'Cacti':
     #       cookie_str = cook.get('value')
    print(cookie_str)    
    if len(cookie_str) != 32 :
        print("获取cookie失败，重试...")
        raise Exception("获取cookie失败，重试...")
    else:
        print("获取cookie成功")
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
        'content-type': 'text/html; charset=UTF-8',
        'Referer': 'http://ip/cacti/graph_view.php'
    }
    cookie_data = {
      'Cookie':'cacti_zoom=zoomMode=quick,zoomOutPositioning=center,zoomOutFactor=2,zoomMarkers=true,zoomTimestamps=auto,zoom3rdMouseButton=false; _ga=GA1.1.63182077.1647313573; _gid=GA1.1.1565299994.1647917243; '+cookie_str+'; _gat=1'
    }
    
    #-------------------------处理日期------------------------------------------

    # 当天的日期
    today_date = datetime.datetime.now().date()
    # 当月1号
    one_date = datetime.datetime.now().replace(day=1)
    # 当天的零点
    today_zero_time = get_day_zero_time(today_date)
    # 当月1号零点
    one_zero_time = get_day_zero_time(one_date)

    #------------------------------------------------------------------------

    #--------------------------下载csv文件------------------------------------
    # 用带cookie的方法下载,下载的为当月1号0点到当天0点的csv
    for num,value in num_list.items():
        Downloadcsv_address = 'http://ip/cacti/graph_xport.php?local_graph_id=' + str(num) + '&rra_id=0' \
                              '&view_type=tree&graph_start=' + str(one_zero_time) + '&graph_end=' + str(today_zero_time)
        print(Downloadcsv_address)
        file_address = FILE_PATH + str(value[0]) + ".csv"  # 存放路径
        r = requests.get(Downloadcsv_address, headers=headers, cookies=cookie_data)        
        with open(file_address, "wb") as code:
            code.write(r.content)
        print(num, 'Download success!')

    driver.quit()
    #------------------------------------------------------------------------

#获取0：00的时间戳
def get_day_zero_time(date):
    if not date:
        return 0

    date_zero = datetime.datetime.now().replace(year=date.year, month=date.month,

    day=date.day, hour=0, minute=0, second=0)

    date_zero_time = int(time.mktime(date_zero.timetuple()))

    return(date_zero_time)


#处理表格形成结果
def csv_deal():
    # 新建一个result.txt文件------------------------------------------------
    with open("result.md",'w+',encoding='utf-8') as f:
            #打印当前文件名
        print('当前时间：',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),file=f)
        print('\n',file=f)
    #------------------------------------------------------------------------
    
    #读文件-------------------------------------------------------------------
    Directory_name = FILE_PATH
    #Directory_name = r'D:/0work/0wxdata/cacti/rrd95analysis/RRD/rrd_download'
    filenames = os.listdir(Directory_name)
    print("读取到以下文件：",filenames)
    #------------------------------------------------------------------------ 
    for csvname in filenames:
        filename = (Directory_name+"/"+csvname)
        print(filename)
        #读取num_list中的description，找到与当前文件名相同的description，读取它的threshold_in和threshold_out
        for num,value in num_list.items():
            if csvname.split('.')[0] == value[0]:
                threshold_in = value[1]
                threshold_out = value[2]
                print(threshold_in,threshold_out)
    #------------------------------------------------------------------------

    #-----------处理表格-----------------------------------------------------
        # 找到第一个空行位置
        blank_line = 0
        with open(filename,'r',encoding='utf8') as f:
            for (num,value) in enumerate(f):
                if num == 8:
                    no_95 = value.split(',',2)[1]
                if value.strip() == '""':
                    blank_line = num + 1
                    break

        # 读文件，跳过无效头部
        df = pd.read_csv(filename, skiprows=blank_line)

        #大于433行，继续处理，否则退出当前循环
        if df.shape[0] > 433:
            # 删除第一列
            df.drop(df.columns[0], inplace=True, axis=1)
            # 删除匹配 "col" 的列
            df.drop(list(df.filter(regex='col')), axis=1, inplace=True)
            # 主从降序排输入值列
            p_col = ['inbound', 'outbound']
            df.columns = p_col
            df.sort_values(by=['inbound', 'outbound'], ascending=False, inplace=True)
        else:
            with open("result.md",'a+',encoding='utf-8') as f:
                #打印当前时间
                print('##  当前时间：',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),file=f)
                print(filename,file=f)
                print('##  未满433行，跳过处理',file=f)
            continue
    #------------------------------------------------------------------------
        
    #-----------处理数据-----------------------------------------------------    
        print("正在处理inbound.......")
        #取总行数的0.05做为95值的位置
        no_one = round(len(df)*0.05)
        no_two = round(len(df)*0.05)+1
        no_three = round(len(df)*0.05)+2
        no_one_x = no_one+1
        no_two_y = no_two+1
        no_three_z = no_three+1
        
        #定位95值的具体数字
        no_one_value = float(df.iloc[[no_one],[0]].values)
        no_two_value = float(df.iloc[[no_two],[0]].values)
        no_three_value = float(df.iloc[[no_three],[0]].values)

        show_one = str(no_one_x)+"值为："+str(no_one_value)+"字节"
        show_two = str(no_two_y)+"值为："+str(no_two_value)+"字节"
        show_three = str(no_three_z)+"值为："+str(no_three_value)+"字节"

        no_443 = df.iloc[442]['inbound']/1000/1000/1000
        #保留两位小数
        no_443 = round(no_443,2)
        no_443_in=str(no_443)+"GB"
        
        #判断value[1]和value[2]是否为空
        if pd.isnull(threshold_in):
            with open("result.md",'a+',encoding='utf-8') as f:
                print(str('* **'+csvname+'**'),file=f)
                print('    #### -------Inbound-------\n',file=f)
                print(str('    **443值为：'+no_443_in+'**\n'),file=f)
                print(str('    '+show_one+'\n'),file=f)
                print(str('    '+show_two+'\n'),file=f)
                print(str('    '+show_three+'\n'),file=f)
        else:
            if no_443 <= threshold_in:        
                with open("result.md",'a+',encoding='utf-8') as f:
                    print(str('* **'+csvname+'**'),file=f)
                    print('    #### -------Inbound-------\n',file=f)
                    print(str('    **443值为：'+no_443_in+'**\n'),file=f)
                    print(str('    '+show_one+'\n'),file=f)
                    print(str('    '+show_two+'\n'),file=f)
                    print(str('    '+show_three+'\n'),file=f)
            else:
                with open("result.md",'a+',encoding='utf-8') as f:
                    print(str('* **'+csvname+'**'),file=f)
                    print('    #### -------Inbound-------\n',file=f)
                    print('    **Inbound已满足保底**\n',file=f)
                    print('    **保底值为：'+str(threshold_in)+'GB'+'**\n',file=f)
                    print(str('    **443值为：'+no_443_in+'**\n'),file=f)

        time.sleep(1)

        #更改顺序，主从降序排输出值列
        df.sort_values(by=['outbound', 'inbound'], ascending=False, inplace=True)

        print("正在处理outbound.......")
        no_one_value = float(df.iloc[[no_one],[1]].values)
        no_two_value = float(df.iloc[[no_two],[1]].values)
        no_three_value = float(df.iloc[[no_three],[1]].values)

        show_one = str(no_one_x)+"值为："+str(no_one_value)+"字节"
        show_two = str(no_two_y)+"值为："+str(no_two_value)+"字节"
        show_three = str(no_three_z)+"值为："+str(no_three_value)+"字节"   

        no_443 = df.iloc[442]['outbound']/1000/1000/1000
        no_443 = round(no_443,2)
        no_443_out=str(no_443)+"GB"
        
        if pd.isnull(threshold_out):
            with open("result.md",'a+',encoding='utf-8') as f:
                print('    #### -------Outbound-------',file=f)
                print(str('    表中95值：'+str(no_95)+'\n'),file=f)
                print(str('    **443值为：'+no_443_out+'**\n'),file=f)
                print(str('    '+show_one+'\n'),file=f)
                print(str('    '+show_two+'\n'),file=f)
                print(str('    '+show_three+'\n'),file=f)
                print('\n',file=f)
        else:
            if no_443 <= threshold_in:
                with open("result.md",'a+',encoding='utf-8') as f:
                    print('    #### -------Outbound-------',file=f)
                    print(str('    表中95值：'+str(no_95)+'\n'),file=f)
                    print(str('    **443值为：'+no_443_out+'**\n'),file=f)
                    print(str('    '+show_one+'\n'),file=f)
                    print(str('    '+show_two+'\n'),file=f)
                    print(str('    '+show_three+'\n'),file=f)
                    print('\n',file=f)
            else:
                with open("result.md",'a+',encoding='utf-8') as f:
                    print('    #### -------Outbound-------',file=f)
                    print('    **Outbound已满足保底**\n',file=f)
                    print('    **保底值为：'+str(threshold_out)+'GB'+'**\n',file=f)
                    print(str('    **443值为：'+no_443_out+'**\n'),file=f)
                    print('\n',file=f)

        #----------------------------------------------------------------
        #  Save as
        #df.to_csv('new1.csv', index=False, encoding='utf-8')
        df.to_csv(OUTPUT_PATH+csvname, index=False, encoding='utf-8')




if __name__ == '__main__':
    clear_file()
    selenium_login()
    csv_deal()