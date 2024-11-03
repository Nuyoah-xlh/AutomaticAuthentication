import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import subprocess

# 设置Chrome选项以隐藏浏览器
chrome_options = Options()
chrome_options.add_argument('--headless')  # 使用无头模式

# 设置WebDriver路径
driver_path = './chromedriver-win64/chromedriver.exe'  # 替换为您的WebDriver路径
service = Service(driver_path)

driver = None  # 初始时不启动浏览器
login_url = 'http://m.njust.edu.cn/portal/index.html'  # 替换为您的校园网认证页面的URL
username = 'XXX'  # 替换为您的账号
password = 'XXXX'  # 替换为您的密码

try:
    while True:
        # 检查网络连接
        response = subprocess.call(["ping", "-n", "1", "www.baidu.com"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if response != 0:
            # 如果无法连接外网，启动浏览器并访问登录页面
            if driver is None:
                driver = webdriver.Chrome(service=service, options=chrome_options)

            driver.get(login_url)
            time.sleep(5)  # 等待页面加载

            try:
                # 输入账号
                username_input = driver.find_element(By.ID, 'username')  # 替换为实际的账号输入框ID
                username_input.clear()
                username_input.send_keys(username)

                # 输入密码
                password_input = driver.find_element(By.ID, 'password')  # 替换为实际的密码输入框ID
                password_input.clear()
                password_input.send_keys(password)

                # 找到并点击登录按钮
                login_button = driver.find_element(By.ID, 'loginBtn')  # 替换为实际的按钮ID
                login_button.click()

            except NoSuchElementException as e:
                pass  # 捕获异常，但不打印
            except Exception as e:
                pass  # 捕获其他异常，但不打印

        else:
            # 网络正常时，关闭浏览器
            if driver is not None:
                driver.quit()
                driver = None

        time.sleep(60*20)  # 每5分钟检查一次

except KeyboardInterrupt:
    pass  # 捕获用户中断，但不打印
finally:
    if driver is not None:
        driver.quit()  # 确保退出WebDriver
