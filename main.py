import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import subprocess
import pywifi
from pywifi import const

print("正在初始化程序...")

# 设置Chrome选项以隐藏浏览器
chrome_options = Options()
chrome_options.add_argument('--headless')  # 使用无头模式
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--remote-debugging-port=9222')

# 设置WebDriver路径
driver_path = './chromedriver-win64/chromedriver.exe'  # 替换为您的WebDriver路径
service = Service(driver_path)

driver = None  # 初始时不启动浏览器
login_url = 'http://m.njust.edu.cn/portal/index.html'  # 替换为您的校园网认证页面的URL
username = 'XXX'  # 替换为您的账号
password = 'XXX'  # 替换为您的密码

print("配置信息已加载完成")


def connect_njust_wifi():
    print("正在尝试连接NJUST WiFi...")
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]  # 获取第一个无线网卡

    while True:
        try:
            print("正在扫描可用WiFi网络...")
            iface.scan()
            time.sleep(2)
            scan_results = iface.scan_results()

            for result in scan_results:
                if result.ssid == "NJUST":
                    print("找到NJUST WiFi网络,正在连接...")
                    profile = pywifi.Profile()
                    profile.ssid = "NJUST"
                    profile.auth = const.AUTH_ALG_OPEN
                    profile.akm.append(const.AKM_TYPE_NONE)

                    iface.remove_all_network_profiles()
                    tmp_profile = iface.add_network_profile(profile)

                    iface.connect(tmp_profile)
                    time.sleep(5)  # 等待连接

                    if iface.status() == const.IFACE_CONNECTED:
                        print("成功连接到NJUST WiFi!")
                        return True

            print("未找到NJUST WiFi,继续尝试...")
            time.sleep(5)  # 等待后重试

        except Exception as e:
            print(f"WiFi连接出错: {str(e)}")
            print("5秒后重试...")
            time.sleep(5)
            continue


try:
    print("开始运行自动认证程序...")
    while True:
        try:
            # 检查是否连接到NJUST WiFi
            print("检查WiFi连接状态...")
            wifi = pywifi.PyWiFi()
            iface = wifi.interfaces()[0]
            if iface.status() != const.IFACE_CONNECTED or \
                    (iface.status() == const.IFACE_CONNECTED and iface.network_profiles()[0].ssid != "NJUST"):
                connect_njust_wifi()
                continue

            # 检查网络连接
            print("检查网络连通性...")
            # response = subprocess.call(["ping", "-n", "1", "www.baidu.com"], stdout=subprocess.PIPE,
            #                            stderr=subprocess.PIPE)
            # 替换原来的 ping 调用
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            response = subprocess.call(
                ["ping", "-n", "1", "www.baidu.com"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                startupinfo=startupinfo  # 关键：隐藏控制台窗口
            )
            if response != 0:
                print("检测到网络未认证,准备进行认证...")
                # 如果无法连接外网，启动浏览器并访问登录页面
                retry_count = 0
                max_retries = 3  # 最多重试3次
                while retry_count < max_retries:
                    try:
                        if driver is None:
                            print("启动浏览器...")
                            driver = webdriver.Chrome(service=service, options=chrome_options)

                        print("访问认证页面...")
                        driver.get(login_url)
                        time.sleep(5)  # 等待页面加载

                        # 检查页面元素是否存在
                        try:
                            username_input = driver.find_element(By.ID, 'username')
                            password_input = driver.find_element(By.ID, 'password')
                            login_button = driver.find_element(By.ID, 'loginBtn')

                            # 检查元素是否可交互
                            if not username_input.is_enabled() or not password_input.is_enabled() or not login_button.is_enabled():
                                print("页面元素不可交互,等待5秒后重试...")
                                time.sleep(5)
                                retry_count += 1
                                continue

                            print("输入认证信息...")
                            # 输入账号
                            username_input.clear()
                            username_input.send_keys(username)

                            # 输入密码
                            password_input.clear()
                            password_input.send_keys(password)

                            # 找到并点击登录按钮
                            print("点击登录按钮...")
                            login_button.click()
                            print("认证完成!")
                            break

                        except NoSuchElementException:
                            print("页面元素未加载完成,等待5秒后重试...")
                            time.sleep(5)
                            retry_count += 1
                            continue

                    except Exception as e:
                        if "element not interactable" in str(e):
                            print("页面元素不可交互,等待5秒后重试...")
                            time.sleep(5)
                            retry_count += 1
                            continue
                        else:
                            print(f"认证过程出错: {str(e)}")
                            print("5秒后重试...")
                            time.sleep(5)
                            retry_count += 1
                            continue

                if retry_count >= max_retries:
                    print("认证重试次数过多,可能是WiFi连接问题,返回检查WiFi状态...")
                    if driver is not None:
                        driver.quit()
                        driver = None
                    continue

            else:
                print("网络连接正常")
                # 网络正常时，关闭浏览器
                if driver is not None:
                    print("关闭浏览器...")
                    driver.quit()
                    driver = None

            timeout = 10*60  # 超时时间为x秒钟
            print("等待"+str(timeout)+"秒钟后进行下一次检查...")
            time.sleep(10)  # 每x秒钟检查一次

        except Exception as e:
            print(f"发生异常: {str(e)}")
            print("5秒后重试...")
            time.sleep(5)
            continue

except KeyboardInterrupt:
    print("程序被用户中断")
finally:
    if driver is not None:
        print("正在清理资源...")
        driver.quit()  # 确保退出WebDriver
