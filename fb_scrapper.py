
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common import proxy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType

from random_user_agent.user_agent import UserAgent 
from random_user_agent.params import SoftwareName, OperatingSystem, HardwareType

import time
import os 

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
hardware_values = [HardwareType.COMPUTER.value]

cities = ["nyc", "orlando", "atlanta"]

class Request:
    selenium_retries=0
    def __init__(self, search_item, city):
        base_url = "https://www.facebook.com/marketplace/"
        search_url = "/search/?query="

        self.url = base_url+city+search_url+"%20".join(search_item.split(" "))
        print(self.url)
        self.user_agent_rotator = UserAgent(software_names = software_names, operating_systems=operating_systems, hardware_values=hardware_values, limit=100)
        self.chrome_options=None
        self.browser=None
        
        self.refresh_user_agent()
        
    
    #Gets a new user-agent if we see that the url is a mobile url. 
    def refresh_user_agent(self):
        user_agent = self.user_agent_rotator.get_random_user_agent()
        self.chrome_options = Options()
        #self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--window_size=1920,1080")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument(f'user-agent={user_agent}')
    
    #Creates browser and runs the given url.
    def run_browser(self):
        self.browser = webdriver.Chrome(options=self.chrome_options)
        self.browser.get(self.url)
        self.browser.implicitly_wait(1)
        return self.browser.current_url

    def fill_user_pass_fields(self):
        try:
            em = browser.find_element_by_id("m_login_email")        
            pas = browser.find_element_by_id("m_login_password")
        except NoSuchElementException as e:
            em = browser.find_element_by_id("email")
            pas = browser.find_element_by_id("pass")            
        login_button = browser.find_element_by_xpath('//button[@name="login"]')

        em.send_keys(os.environ.get("FB_USERNAME"))
        pas.send_keys(os.environ.get("FB_PASS"))
        #browser.find_element_by_css_selector("#pass").send_keys("insert password here")
        #browser.find_element_by_css_selector("#u_0_q").click()
        login_button.click()

    def get_selenium_res(self):
        try:
            scrap_url = self.run_browser()
            while(scrap_url.startswith("https://m.")):
                self.refresh_user_agent()
                self.browser.close()
                scrap_url = self.run_browser()
            print(scrap_url)
            time.sleep(1000000)
                
            return True
        except Exception as e:
            print("An exception happened!")
            self.browser.close()
            raise e

#req = Request("https://www.facebook.com/marketplace/nyc/search/?query=ford%20transit%20high&exact=false")
req = Request("Ford transit 2015", "nyc")
#req = Request('http://lumtest.com/myip.json')
req.get_selenium_res()

#Wait for an element to appear:
# time_to_wait = 90
# try:
#     WebDriverWait(browser, time_to_wait).until(
#         EC.presence_of_all_elements_located((By.CLASS_NAME, "class_name"))
#     )
# finally:


#Proxy Usage:
#PROXY = "http://gate.smartproxy.com:7000"
#prox = Proxy()
#prox.proxy_type = ProxyType.MANUAL
#prox.auto_detect=False
#capabilities = webdriver.DesiredCapabilities.CHROME
#prox.http_proxy = PROXY
#prox.ssl_proxy = PROXY
#prox.add_to_capabilities(capabilities)
#browser = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities)