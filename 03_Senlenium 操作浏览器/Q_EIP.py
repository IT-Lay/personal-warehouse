import traceback
import time
import schedule
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

def job_eip():
    driver = None
    try:
        reply_list = ['看开了，谁的头顶都有一汪蓝天，看淡了，谁的心中都有一片花海', '好好吃饭，好好睡觉，好好挣钱，好好花钱。既然活着就好好活着，每分钟都为自己活着。', '一场说走就走的旅行，背后势必隐藏着一笔想取就取的钱。', '不要相信童话，或者南瓜。童话甜美而残酷，人生也是',
                      '其实没有什么是忘不掉的，过去再美好再刻骨铭心，原来也只是过去。至于灾难和痛苦，也大抵应该是如此吧。','世上最美的，莫过于那从泪水中挣脱出来的那个微笑。', '有时候，我们感觉累，是由于在人生的道路上，忘了去哪。', '有些记忆随风而逝，有些声音听过无痕，有些永不会消弭在时光的叶脉里。',
                      '时间随着墙上停摆的钟，抛弃我在黑暗之中', '谁的一句来日方长让我目睹了人走茶凉。']
        # 创建一个ChromeOptions对象，用于设置headless模式
        # chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # 保持浏览器打开状态
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("detach", True)
        print('脚本开始~')
        driver = webdriver.Chrome(options=chrome_options)
        # 连接登录URL
        driver.get("https://eip.quectel.com/login")
        # 等待登录成功(判断元素标志）
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.LINK_TEXT, "欢迎来到 Quectel EIP")))
        ok_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'login-button') and @type='button']")
        time.sleep(0.1)
        ok_btn.click()
        # 等待登录成功(判断元素标志）
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h3.auth-title#title")))
        # 找到账号输入框
        usr_name = driver.find_element(By.ID, "username")
        # 找到密码输入框
        psw = driver.find_element(By.ID, "password")
        # 找到登录按钮
        submit_btn = driver.find_element(By.ID, "btnSubmit")
        # 输入账号
        usr_name.send_keys('xx.xxx@quectel.com')
        # 输入密码
        psw.send_keys('xxxxxx')
        # 点击登录按钮
        time.sleep(0.1)
        submit_btn.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "discourse-rewards-total-points")))
        # 打开对应帖子的网址
        driver.get('https://eip.quectel.com/t/topic/16711')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.LINK_TEXT, "荒天帝 赞")))
        times = 0
        for text in reply_list:
            # 找到回复按钮并点击
            times += 1
            time.sleep(1)
            if times == 1:
                reply_button = driver.find_element(By.XPATH,'//button[@class="widget-button btn-flat reply create fade-out btn-icon-text" and @title="开始撰写对此帖子的回复" and @aria-label="回复 @jking.wang 发布的帖子 #1"]')
            else:
                reply_button = driver.find_element(By.XPATH, '//button[@class="btn btn-icon-text btn-primary create"]')
            time.sleep(0.5)
            reply_button.click()
            # 找到回复输入框并输入内容
            time.sleep(0.5)
            reply_textarea = driver.find_element(By.CLASS_NAME, 'd-editor-input')
            time.sleep(0.1)
            reply_textarea.send_keys(text)
            time.sleep(0.5)
            if times == 1:
                hf_button = driver.find_element(By.CSS_SELECTOR, '.btn.btn-icon-text.btn-primary.create')
            else:
                hf_button = driver.find_element(By.XPATH, '//button[@class="btn btn-icon-text btn-primary create "]')
            time.sleep(0.5)
            # 找到确认回复按钮
            driver.execute_script("arguments[0].click();", hf_button)
            time.sleep(10)
    except Exception:
        print(f'-- Error -- {traceback.format_exc()}')
    finally:
        # 关闭浏览器
        driver.quit()
# job_eip()

# 创建任务
for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
    getattr(schedule.every(), day).at("08:30").do(job_eip)

while True:
    # 运行所有可以运行的任务
    schedule.run_pending()
    time.sleep(30)
