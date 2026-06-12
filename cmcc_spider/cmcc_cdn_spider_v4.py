"""
中国移动CDN - 带宽统计XLS导出脚本 (v4)
功能：登录CDN平台，自动导出昨日带宽统计XLS文件（最小单位，1000进制）

改动说明（适配Linux环境）：
1. 配置外置到YAML文件，支持多客户（一个文件配置多个客户）
2. 保留Linux容器参数（--no-sandbox、--disable-dev-shm-usage）
3. 默认下载目录为脚本所在目录
4. 支持通过配置文件指定chromedriver路径

用法：
    python cmcc_cdn_spider_v4.py                    # 默认跑第一个客户
    python cmcc_cdn_spider_v4.py --list             # 列出所有客户
    python cmcc_cdn_spider_v4.py --customer "淮北移动"  # 指定客户
    python cmcc_cdn_spider_v4.py --all              # 批量执行所有客户

依赖：
    pip install selenium requests ddddocr pyyaml
"""
import argparse
import os
import sys
import time
from datetime import datetime, timedelta
from io import StringIO

import ddddocr
import requests
import yaml
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _get_default_download_dir():
    """获取默认下载目录"""
    if sys.platform == 'win32':
        return os.path.join(os.path.expanduser('~'), 'Downloads')
    return os.path.dirname(os.path.abspath(__file__))


# ========== 默认配置 ==========
DEFAULT_CONFIG = {
    'download_dir': _get_default_download_dir(),
    'unit_scale': 1000,
}
# =============================


def load_config(config_path, customer_name=None):
    """加载YAML配置文件，支持多客户配置

    配置格式：
        customers:
          - name: "安徽移动"
            user: 'xxx'
            ...
          - name: "淮北移动"
            user: 'yyy'
            ...
        defaults:
          unit_scale: 1000
          download_dir: "."
          chromedriver_path: null
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        raw = yaml.safe_load(f)

    # 兼容旧格式（单客户直接写在根级）
    if 'customers' not in raw:
        for key, val in DEFAULT_CONFIG.items():
            if key not in raw:
                raw[key] = val
        required = ['user', 'passwd', 'cp_id', 'target_domains']
        for key in required:
            if key not in raw or not raw[key]:
                raise ValueError(f"配置文件缺少必填项: {key}")
        return [raw]

    # 新格式：多客户
    defaults = raw.get('defaults', {})
    customers = raw.get('customers', [])
    if not customers:
        raise ValueError("配置文件中 customers 列表为空")

    result = []
    for cust in customers:
        # 合并 defaults -> 客户配置
        merged = dict(defaults)
        merged.update(cust)
        # 再合并系统默认值
        for key, val in DEFAULT_CONFIG.items():
            if key not in merged:
                merged[key] = val
        # 校验
        required = ['user', 'passwd', 'cp_id', 'target_domains']
        for key in required:
            if key not in merged or not merged[key]:
                raise ValueError(f"客户 '{merged.get('name', 'unknown')}' 缺少必填项: {key}")
        result.append(merged)

    # 如果指定了客户名称，过滤返回
    if customer_name:
        matched = [c for c in result if c.get('name') == customer_name]
        if not matched:
            available = [c.get('name', 'unnamed') for c in result]
            raise ValueError(f"未找到客户 '{customer_name}'，可用客户: {available}")
        return matched

    return result


def get_yesterday():
    """获取昨天日期，格式 YYYY-MM-DD"""
    return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')


def build_download_url(yesterday_str, cfg):
    """构造XLS下载URL"""
    url = (
        f'https://p.cdn.10086.cn/statistics/getBwFile'
        f'?cpId={cfg["cp_id"]}'
    )
    if cfg.get('target_domains'):
        domain_names = ','.join(cfg['target_domains'])
        url += f'&domainNames={domain_names}'
    url += (
        f'&startTime={yesterday_str}%2000:00'
        f'&endTime={yesterday_str}%2023:59'
        f'&granular=0'
        f'&unitScale={cfg["unit_scale"]}'
        f'&minUnit=true'
    )
    return url


def download_with_cookies(driver, url, save_path):
    """方案A：用Selenium的cookies直接GET下载文件"""
    selenium_cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in selenium_cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    session.headers.update({
        'User-Agent': driver.execute_script('return navigator.userAgent'),
        'Referer': driver.current_url,
    })

    print(f"[方案A] 尝试直接下载: {url}")
    try:
        resp = session.get(url, timeout=30)
    except Exception as e:
        print(f"[方案A] 请求异常: {e}")
        return False

    if len(resp.content) < 100:
        print(f"[方案A] 返回内容过小 ({len(resp.content)} bytes)")
        return False

    content_type = resp.headers.get('Content-Type', '')
    is_xls_magic = resp.content[:4] == b'\xd0\xcf\x11\xe0'
    is_html_response = 'text/html' in content_type.lower()

    if is_html_response and not is_xls_magic:
        print(f"[方案A] 返回内容为HTML非XLS (Content-Type: {content_type})")
        return False

    if resp.status_code not in (200, 201):
        print(f"[方案A] HTTP {resp.status_code}，下载失败")
        return False

    with open(save_path, 'wb') as f:
        f.write(resp.content)
    print(f"[方案A] 下载成功: {save_path} ({len(resp.content)} bytes)")
    return True


def select_domains(driver, target_domains):
    """在域名下拉框中勾选指定的域名"""
    print(f"[域名筛选] 准备勾选 {len(target_domains)} 个域名: {target_domains}")

    try:
        domain_trigger = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.cm-select-text.cm-select-placeholder"))
        )
        domain_trigger.click()
        print("[域名筛选] 已点击域名下拉触发按钮")
        time.sleep(5)
    except Exception as e:
        print(f"[域名筛选] 点击下拉触发按钮失败: {e}")
        return False

    success_count = 0
    for domain in target_domains:
        try:
            domain_li = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.XPATH, f"//li[@title='{domain}']"))
            )
            _click_checkbox_in_li(driver, domain_li)

            if _is_li_checked(driver, domain_li):
                print(f"[域名筛选] 已勾选: {domain}")
                success_count += 1
            else:
                _force_check_li(driver, domain_li)
                if _is_li_checked(driver, domain_li):
                    print(f"[域名筛选] 强制勾选成功: {domain}")
                    success_count += 1
                else:
                    print(f"[域名筛选] 强制勾选也失败: {domain}")
        except Exception as e:
            print(f"[域名筛选] 未找到域名: {domain} ({type(e).__name__})")

    try:
        driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(1)
    except Exception:
        pass

    print(f"[域名筛选] 完成: {success_count}/{len(target_domains)} 个域名已勾选")
    return success_count > 0


def _click_checkbox_in_li(driver, li_element):
    """多策略点击 li 内的 checkbox"""
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", li_element)
    time.sleep(0.5)
    actions = ActionChains(driver)

    try:
        checkbox = li_element.find_element(By.CSS_SELECTOR, "span.cm-checkbox")
        actions.move_to_element(checkbox).click().perform()
        time.sleep(2)
        if _is_li_checked(driver, li_element):
            return
    except Exception:
        pass

    try:
        inp = li_element.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        driver.execute_script("arguments[0].click();", inp)
        time.sleep(2)
        if _is_li_checked(driver, li_element):
            return
    except Exception:
        pass

    try:
        label = li_element.find_element(By.CSS_SELECTOR, "label")
        actions.move_to_element(label).click().perform()
        time.sleep(2)
        if _is_li_checked(driver, li_element):
            return
    except Exception:
        pass

    try:
        actions.move_to_element(li_element).click().perform()
        time.sleep(2)
    except Exception:
        pass


def _is_li_checked(driver, li_element):
    """判断 li 是否已被勾选"""
    return driver.execute_script("""
        var li = arguments[0];
        if (!li) return false;
        var checkboxSpan = li.querySelector('span.cm-checkbox');
        if (checkboxSpan && checkboxSpan.classList.contains('cm-checkbox-checked')) return true;
        if (li.classList.contains('cm-select-option-active')) return true;
        return false;
    """, li_element)


def _force_check_li(driver, li_element):
    """最后手段：直接用 JS 修改 class 并触发事件"""
    driver.execute_script("""
        var li = arguments[0];
        if (!li) return;
        li.classList.add('cm-select-option-active');
        var cbSpan = li.querySelector('span.cm-checkbox');
        if (cbSpan) cbSpan.classList.add('cm-checkbox-checked');
        var inp = li.querySelector('input[type="checkbox"]');
        if (inp) {
            inp.checked = true;
            inp.dispatchEvent(new Event('change', { bubbles: true }));
        }
        li.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    """, li_element)
    time.sleep(1)


def click_export(driver):
    """方案B：模拟点击UI按钮下载文件"""
    print("[方案B] 尝试模拟点击导出...")

    min_unit_xpath = '/html/body/div[1]/div/div/div[3]/div/div/div/div[1]/div/div/div[2]/div/div/div[2]/div/span/span'
    try:
        min_unit_toggle = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, min_unit_xpath))
        )
        min_unit_toggle.click()
        time.sleep(1)
        print("已点击「导出为最小单位」")
    except Exception as e:
        print(f"点击「导出为最小单位」失败: {e}")
        try:
            min_unit_toggle = driver.find_element(By.XPATH, "//span[contains(text(), '导出为最小单位')]")
            min_unit_toggle.click()
            time.sleep(1)
            print("通过文本定位点击「导出为最小单位」成功")
        except Exception as e2:
            print(f"备用定位也失败: {e2}")

    try:
        export_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.cm-button.pull-right.primary.export-btn"))
        )
        export_button.click()
        time.sleep(5)
        print("已点击「导出」按钮，文件将保存到浏览器下载目录")
    except Exception as e:
        print(f"点击「导出」按钮失败: {e}")
        try:
            export_button = driver.find_element(By.XPATH, "//a[contains(text(), '导出')]")
            export_button.click()
            time.sleep(5)
            print("通过文本定位点击「导出」成功")
        except Exception as e2:
            print(f"备用定位也失败: {e2}")


def _create_driver(cfg):
    """创建Chrome WebDriver（Linux适配）"""
    download_dir = cfg['download_dir']

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')

    prefs = {
        'download.default_directory': os.path.abspath(download_dir),
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True,
    }
    chrome_options.add_experimental_option('prefs', prefs)

    # 支持通过配置指定chromedriver路径
    driver_path = cfg.get('chromedriver_path')
    if driver_path:
        if not os.path.exists(driver_path):
            print(f"[警告] 配置的chromedriver路径不存在: {driver_path}，尝试自动查找")
            driver_path = None

    if driver_path:
        driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)

    return driver


def run_spider(cfg):
    """主流程：登录 → 选择昨日 → 导出XLS"""
    download_dir = cfg['download_dir']

    driver = _create_driver(cfg)
    xls_path = None

    try:
        driver.get('https://p11.cdn.10086.cn/login/redirect?service_code=QKUB8S9Y&redirect_uri=https://p.cdn.10086.cn/unionauth/callback')
        driver.maximize_window()

        # 填写账号密码
        login_user = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[name="username"]'))
        )
        login_password = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[name="password"]'))
        )
        login_user.send_keys(cfg['user'])
        login_password.send_keys(cfg['passwd'])

        # 选择"企业"证书类型
        dropdown_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.cm-select-cert"))
        )
        dropdown_button.click()
        option_to_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[@class='cm-select-option']/a/span[text()='企业']"))
        )
        option_to_select.click()
        time.sleep(1)

        # 验证码识别与登录
        max_attempts = 10
        for attempt in range(max_attempts):
            print(f"尝试登录，第 {attempt+1}/{max_attempts} 次尝试")

            if attempt > 0:
                refresh_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, 'verify-img'))
                )
                refresh_button.click()
                time.sleep(1)

            login_vcode = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[name="verifyCode"]'))
            )
            img_element = driver.find_element(By.CLASS_NAME, 'verify-img')
            v_code_path = os.path.join(download_dir, 'v_code.png')
            img_element.screenshot(v_code_path)

            original_stdout = sys.stdout
            new_stdout = StringIO()
            sys.stdout = new_stdout
            ocr = ddddocr.DdddOcr()
            image = open(v_code_path, "rb").read()
            result = ocr.classification(image)
            sys.stdout = original_stdout

            login_vcode.clear()
            login_vcode.send_keys(result)
            time.sleep(1)
            driver.find_element(By.CSS_SELECTOR, 'span.cm-touch-ripple').click()
            time.sleep(3)

            try:
                error_message = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="text-left mb-5"]'))
                )
                print(f"验证码不正确: {error_message.text}")
                continue
            except:
                print("登录成功")
                break
        else:
            print("达到最大尝试次数，登录失败")
            return None

        # 导航到统计分析
        statistics_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "统计分析"))
        )
        statistics_button.click()
        time.sleep(2)

        # 切换到iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//iframe[contains(@src, "index.html")]'))
        )
        driver.switch_to.frame(iframe)

        # 域名筛选
        if cfg.get('target_domains'):
            select_domains(driver, cfg['target_domains'])
        else:
            print("[域名筛选] target_domains 为空，跳过域名筛选")

        # 点击"昨日"
        yesterday_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                '//*[@id="root"]/div/div/div[2]/div[2]/div/a[2]/span/div/span'))
        )
        yesterday_button.click()
        time.sleep(3)

        # 点击"确定"
        confirm_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                '//*[@id="root"]/div/div/div[2]/div[2]/a[1]/span/div/span'))
        )
        confirm_button.click()
        time.sleep(2)

        # 点击"导出为最小单位"
        min_unit_label = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                "//label[contains(text(), '导出为最小单位')]"))
        )
        min_unit_label.click()
        time.sleep(1)

        # 导出XLS
        yesterday_str = get_yesterday()
        download_url = build_download_url(yesterday_str, cfg)
        filename = f"cdn_bandwidth_{cfg['name']}_{yesterday_str}.xls"
        # 按客户名分目录: xls/客户名/
        xls_dir = os.path.join(download_dir, "xls", cfg['name'])
        os.makedirs(xls_dir, exist_ok=True)
        xls_path = os.path.join(xls_dir, filename)

        if download_with_cookies(driver, download_url, xls_path):
            print(f"XLS导出完成: {xls_path}")
        else:
            click_export(driver)

    finally:
        driver.quit()

    return xls_path


def main():
    parser = argparse.ArgumentParser(description='CDN带宽统计XLS导出脚本 v4')
    parser.add_argument('-c', '--config', default='config.yaml', help='YAML配置文件路径 (默认: config.yaml)')
    parser.add_argument('--customer', help='指定客户名称（如"淮北移动"）')
    parser.add_argument('--list', action='store_true', help='列出配置文件中所有客户')
    parser.add_argument('--all', action='store_true', help='批量执行所有客户')
    args = parser.parse_args()

    customers = load_config(args.config, args.customer)

    if args.list:
        print(f"配置文件: {args.config}")
        print(f"共 {len(customers)} 个客户:\n")
        for i, cust in enumerate(customers, 1):
            print(f"  {i}. {cust.get('name', '未命名')}")
            print(f"     账号: {cust['user']}, CP_ID: {cust['cp_id']}")
            print(f"     域名: {cust['target_domains']}")
            print()
        return

    # 决定要执行的客户列表
    to_run = customers if args.all else [customers[0]]
    failed = []

    for cust in to_run:
        name = cust.get('name', cust['user'])
        print(f"\n{'='*50}")
        print(f"[客户] {name}")
        print(f"[配置] 账号: {cust['user']}, CP_ID: {cust['cp_id']}")
        print(f"[配置] 域名: {cust['target_domains']}")
        print('='*50)

        xls_path = run_spider(cust)
        if xls_path and os.path.exists(xls_path):
            print(f"\n[{name}] 下载成功: {xls_path}")
        else:
            print(f"\n[{name}] 下载失败")
            failed.append(name)

    print(f"\n{'='*50}")
    print(f"执行完成: {len(to_run) - len(failed)}/{len(to_run)} 个客户成功")
    if failed:
        print(f"失败客户: {', '.join(failed)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
