import time

from bs4 import BeautifulSoup
from dotenv import load_dotenv
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

    def open_web_site(self, url='https://me-deplacer.iledefrance-mobilites.fr/infos-trafic/train'):
        self.driver.switch_to.new_window('tab')
        self.driver.get(url)
        self.driver.implicitly_wait(5)
        print("Web site opened")

    def accept_cookies(self):
        try:
            # Wait for the cookies pop-up
            cookies_popup = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[contains(text(), "Je suis d’accord")]'))
            )
            cookies_popup.click()
            print('Cookies accepted.')
        except Exception as e:
            print('Could not find cookies button. Maybe it was not there.')
            print(str(e))

    def get_type_transport_href(self):
        type_transport_href = []
        self.open_web_site()
        self.driver.implicitly_wait(5)
        transport_type = WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//nav[@class="text--caption-regular"]//ul//li//a')
        ))

        for line in transport_type:
            type_transport_href.append(line.get_attribute('href'))
        print("Transport type found")
        return type_transport_href

    def get_line_transport_href(self):
        transport_types = ['TRAIN/RER', 'METRO', 'TRAMWAY']
        self.open_web_site()
        type_transport_href = self.get_type_transport_href()[1:-1]

        line_transport = {transport_type: [] for transport_type in transport_types}

        for i, transport in enumerate(type_transport_href):
            print(f"Opening website for {transport_types[i]}")
            self.open_web_site(transport)
            lines = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH,'//div[@class="my-journey-content"]//a[contains(@class, "my-journey-content-link") or contains(@class, "sub-icon")]'))
            )
            line_transport_href = [line.get_attribute('href') for line in lines]
            if transport_types[i] == 'METRO':
                line_transport[transport_types[i]] = line_transport_href[:3] + line_transport_href[4:8] + line_transport_href[9:-3]
            else:
                line_transport[transport_types[i]] = line_transport_href
        print("Line transport found")
        return line_transport

    def get_twitter_hrefs(self):
        transport_types = ['TRAIN/RER', 'METRO', 'TRAMWAY']
        line_twitter_page = {transport_type: [] for transport_type in transport_types}
        line_transport = self.get_line_transport_href()
        first_time = True

        for transport_type, lines in line_transport.items():
            print(f"Opening Twitter page for {transport_type}")
            for line in lines:
                self.open_web_site(line)
                twitter_button = self.wait_and_find(By.XPATH, '//*[@id="contenu"]/div/div[3]/ul/li[3]/a')
                twitter_button.click()
                print("Twitter button clicked")
                if first_time:
                    self.accept_cookies()
                    first_time = False
                twitter_href =self.wait_and_find(By.XPATH, '//*[@id="contenu"]/div/div[4]/div/a')
                print("Twitter page ")
                line_twitter_page[transport_type].append(twitter_href.get_attribute('href'))

        return line_twitter_page

    def wait_and_find(self, by, value):
        return WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((by, value)))


    def get_twitte(self,line_twitter_page:dict)->dict:
        data = {}
        self.login()
        for transport_type, lines in line_twitter_page.items():
            print(f"Opening Twitter page for {transport_type}")
            for line in lines:
                self.open_web_site(line)
                time.sleep(2)
                body = self.wait_and_find(By.XPATH, '/html/body')
                for _ in range(3):  # Ajustez le nombre de défilements selon vos besoins
                    body.send_keys(Keys.PAGE_DOWN)
                    time.sleep(2)  # Attendre que la page se charge
                articles = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, '//div[@class="css-175oi2r"]//article')
                    )
                )
                data[line] = []
                for article in articles:
                    articleData = {}
                    soup = BeautifulSoup(article.get_attribute('outerHTML'), 'html.parser')
                    lineName = soup.find_all('span')
                    articleData['lineName'] = lineName[1].text.strip() if len(lineName) > 1 else None
                    publicationTime = soup.find('time')
                    articleData['publicationTime'] = publicationTime['datetime'] if publicationTime else None
                    signalType = soup.find('img', draggable="false")
                    articleData['signalType'] = signalType.get('src') if signalType else None
                    imageInTweet = soup.find('img', src=True, draggable="true")
                    articleData['imageInTweet'] = imageInTweet.get('src') if imageInTweet else None
                    twitterText = soup.find(dir='auto')
                    articleData['twitterText'] = twitterText.text.strip() if twitterText else None
                    print(articleData)
                    data[line].append(articleData)


        return data








