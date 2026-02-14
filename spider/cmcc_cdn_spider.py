#####小爬，把数爬下来记录到本地
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
from io import StringIO
import requests,time,sys,ddddocr
from requests.adapters import HTTPAdapter
from datetime import datetime


chrome_options = Options()
chrome_options.add_argument('--headless') 
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=chrome_options)
#service = Service(chrome_driver_path)
#driver = webdriver.Chrome(service=service)
driver.get('https://p11.cdn.10086.cn/login/redirect?service_code=QKUB8S9Y&redirect_uri=https://p.cdn.10086.cn/unionauth/callback')

user = 'xxxxxxx'
passwd = 'xxxxxxx'
def selenium_login():
    # ----------selenium登录------------------------------------------------
    driver.maximize_window() 
    login_user = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[name="username"]')))
    login_password = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[name="password"]')))
    login_user.send_keys(user)
    login_password.send_keys(passwd)
    # ===== 处理自定义下拉菜单 =====
    
    # 点击下拉按钮展开选项
    dropdown_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "span.cm-select-cert"))
    )
    dropdown_button.click()
    option_to_select = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//li[@class='cm-select-option']/a/span[text()='企业']"))
    )
    option_to_select.click()
    time.sleep(1)
    # 保存 session
    session = requests.Session()
    adapter = HTTPAdapter(pool_maxsize=100)
    
    # ===== 处理验证码 =====
    max_attempts = 10  # 最大尝试次数
    for attempt in range(max_attempts):
        print(f"尝试登录，第 {attempt+1}/{max_attempts} 次尝试")
        
        # 刷新验证码
        if attempt > 0:  # 第一次不需要刷新
            refresh_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'verify-img'))
            )
            refresh_button.click()
            time.sleep(1)  # 等待验证码刷新
            
        # 定位验证码输入框和图片
        login_vcode = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[name="verifyCode"]')))
        img_element = driver.find_element(By.CLASS_NAME, 'verify-img')
        
        # 截图并识别验证码
        img_element.screenshot('v_code.png')
        original_stdout = sys.stdout
        new_stdout = StringIO()
        sys.stdout = new_stdout
        ocr = ddddocr.DdddOcr()
        image = open("v_code.png", "rb").read()
        result = ocr.classification(image)
        sys.stdout = original_stdout
        
        # 输入验证码并登录
        login_vcode.clear()  # 清除之前的输入
        login_vcode.send_keys(result)
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, 'span.cm-touch-ripple').click()
        time.sleep(3)  # 等待登录结果
        
        # 检查是否有验证码错误提示
        try:
            error_message = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="text-left mb-5"]'))
            )
            print(f"验证码不正确: {error_message.text}")
            continue  # 继续下一次尝试
        except:
            print("未检测到验证码错误，继续后续操作")
            break  # 没有错误，跳出循环
    
    else:  # 如果达到最大尝试次数
        print("达到最大尝试次数，登录失败")
        driver.quit()
        return
    #跳转到统计分析
    statistics_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "统计分析"))
    )
    # 点击按钮
    statistics_button.click()
    time.sleep(2)
    # 切换到iframe
    iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//iframe[contains(@src, "index.html")]'))
    )
    driver.switch_to.frame(iframe)

    # 点击昨日按钮
    yesterday_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/div/a[2]/span/div/span'))
    )
    yesterday_button.click()
    time.sleep(5)
    
    # 点击"确定"按钮
    confirm_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/a[1]/span/div/span'))
    )
    confirm_button.click()
    time.sleep(2)

    # 获取峰值
    peak_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="peak"]'))
    )
    peak_value = peak_element.text  # 获取元素的文本内容

    # 将内容写入本地文件
    with open('peak_value_anhui_zhibo.txt', 'w', encoding='utf-8') as f:
        f.write(peak_value)

    #进制切换1000->1024
    demical_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/span[6]/span/span[2]'))
    )
    demical_button.click()
    
    #点击日期选择器
    date_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div/div[2]/div[2]/div/div[1]/i'))
    )
    date_button.click()
    
    time.sleep(2)
    
    # 获取当前日期
    today = datetime.now()
    current_day = today.day
    current_month = today.month
    current_year = today.year
    
    print(f"当前日期: {current_year}年{current_month}月{current_day}日")
    
    # 检查当前显示的月份，并导航到正确的月份
    while True:
        # 获取两个日期选择器的年份和月份
        try:
            # 查看第一个日期选择器
            first_year_elem = driver.find_element(By.CSS_SELECTOR, ".cm-date-picker:first-child .date-picker-header .year")
            first_month_elem = driver.find_element(By.CSS_SELECTOR, ".cm-date-picker:first-child .date-picker-header .month")
            first_year = int(first_year_elem.text)
            first_month = int(first_month_elem.text)
            
            print(f"第一个面板显示: {first_year}年{first_month}月")
            
            # 检查第一个面板是否是我们需要的月份
            if first_year == current_year and first_month == current_month:
                # 找到当前月份，选择1号
                first_day_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'cm-date-picker')][1]//button[@class='day' and .//span[text()='1']]"))
                )
                first_day_button.click()
                
                time.sleep(1)
                
                # 选择当前日期
                current_day_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'cm-date-picker')][1]//button[@class='day' and .//span[text()='{current_day}']]"))
                )
                current_day_button.click()
                
                print(f"已选择{current_year}年{current_month}月1日到{current_day}日")
                break
            else:
                # 检查第二个日期选择器
                try:
                    second_year_elem = driver.find_element(By.CSS_SELECTOR, ".cm-date-picker:nth-child(2) .date-picker-header .year")
                    second_month_elem = driver.find_element(By.CSS_SELECTOR, ".cm-date-picker:nth-child(2) .date-picker-header .month")
                    second_year = int(second_year_elem.text)
                    second_month = int(second_month_elem.text)
                    
                    print(f"第二个面板显示: {second_year}年{second_month}月")
                    
                    if second_year == current_year and second_month == current_month:
                        # 在第二个面板中找到当前月份
                        # 选择1号
                        first_day_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'cm-date-picker')][2]//button[@class='day' and .//span[text()='1']]"))
                        )
                        first_day_button.click()
                        
                        time.sleep(1)
                        
                        # 选择当前日期
                        current_day_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'cm-date-picker')][2]//button[@class='day' and .//span[text()='{current_day}']]"))
                        )
                        current_day_button.click()
                        
                        print(f"已选择{current_year}年{current_month}月1日到{current_day}日")
                        break
                except:
                    pass  # 如果没有第二个面板，则继续导航
            
            # 如果当前显示的月份不是我们要的，需要导航
            if (first_year * 12 + first_month) < (current_year * 12 + current_month):
                # 目标月份在未来的月份，点击next按钮
                next_button = driver.find_element(By.CSS_SELECTOR, ".date-picker-header .next")
                next_button.click()
                print("点击下个月按钮")
                time.sleep(1)
            elif (first_year * 12 + first_month) > (current_year * 12 + current_month):
                # 目标月份在过去的月份，点击prev按钮
                prev_button = driver.find_element(By.CSS_SELECTOR, ".date-picker-header .prev")
                prev_button.click()
                print("点击上个月按钮")
                time.sleep(1)
            else:
                # 如果月份相等但还在循环中，说明有其他问题
                print("月份相等，退出循环")
                break
                
        except Exception as e:
            print(f"检查月份时出错: {e}")
            break
    
    # 修改时间粒度：点击时间粒度选择器，从"一天"改为"1小时"
    try:
        # 使用您提供的XPath定位时间粒度选择器
        time_granularity_selector = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[2]/div[2]/div/div[2]/span[1]/div'))
        )
        time_granularity_selector.click()
        print("已点击时间粒度选择器")
        time.sleep(2)
        
        # 使用您提供的精确XPath定位"1小时"选项
        hour_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[2]/div[2]/div/div[2]/div/div/ul/li[2]/a/span'))
        )
        hour_option.click()
        print("已选择'1小时'时间粒度")
        time.sleep(2)
        
        # 再次点击原始的确定按钮
        confirm_button.click()
        print("已再次点击确定按钮")
        
    except Exception as e:
        print(f"修改时间粒度时出错: {e}")
        # 如果上述方法失败，尝试另一种方式
        try:
            # 尝试点击时间粒度选择器后，等待选项出现，然后点击"1小时"
            time_granularity_selector = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div[2]/div[2]/div/div[2]/span[1]/div')
            time_granularity_selector.click()
            time.sleep(2)
            
            # 尝试用更灵活的方式查找"1小时"选项
            hour_options = driver.find_elements(By.XPATH, "//span[contains(text(), '1小时') or text()='1小时']")
            for option in hour_options:
                if option.is_displayed():
                    option.click()
                    print("已通过备选方式选择'1小时'时间粒度")
                    break
            
            # 再次点击确定按钮
            confirm_button.click()
            print("已再次点击确定按钮")
        except Exception as e2:
            print(f"备选方案也失败: {e2}")
            # 即使时间粒度修改失败，也要继续截图
            try:
                confirm_button.click()
                print("已点击确定按钮")
            except:
                print("点击确定按钮也失败")
    
    # 等待页面加载完成
    time.sleep(10)    
    # 屏幕截图并保存本地
    driver.save_screenshot('screenshot_anhuizhibo.png')
    driver.quit()

if __name__ == '__main__':
    selenium_login()
    print('截图完毕')
