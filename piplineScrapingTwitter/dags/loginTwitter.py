from dotenv import load_dotenv
import os
from selenium.webdriver.support import expected_conditions as EC

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType


class LoginTwitter :
    def __init__(self):
        load_dotenv()
        self.username = "yannioucha3706"
        self.password = "Wm16062017@"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager("124.0.6367", chrome_type=ChromeType.GOOGLE).install()),options=chrome_options)
        print("Driver is ready")
    def login(self):
        self.driver.get("https://twitter.com/i/flow/login")
        username = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='text' and @type='text']"))
        )
        print("ecris username")
        username.send_keys(self.username)
        username.send_keys(Keys.RETURN)

        password = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='password' and @type='password']"))
        )
        password.send_keys(self.password)
        password.send_keys(Keys.RETURN)
        print('Login successful.')

    def open_web_site(self, url='https://www.iledefrance-mobilites.fr/'):
        self.driver.switch_to.new_window('tab')
        self.driver.get(url)
        print("Web site opened")




