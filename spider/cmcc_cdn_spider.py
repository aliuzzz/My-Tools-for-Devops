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


chrome_driver_path = 'D://python//chromedriver.exe'
chrome_options = Options()
chrome_options.add_argument('--headless') 
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=chrome_options)
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)
driver.get('https://p11.cdn.10086.cn/login/redirect?service_code=QKUB8S9Y&redirect_uri=https://p.cdn.10086.cn/unionauth/callback')

user = 'xxxxx'
passwd = 'xxxx'
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
    
    #屏幕截图并保存本地
    driver.save_screenshot('screenshot.png')
    driver.quit()

if __name__ == '__main__':
    selenium_login()
    print('截图完毕')