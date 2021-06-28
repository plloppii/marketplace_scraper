
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common import proxy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType

from random_user_agent.user_agent import UserAgent 
from random_user_agent.params import SoftwareName, OperatingSystem, HardwareType

from dataclasses import dataclass
from typing import List

import time
import os 
import logging

from listing import Listing

states= set(["AL","AK","AS","AZ","AR","CA","CO","CT","DE","DC","FL","GA","GU","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","MP","OH","OK","OR","PA","PR","RI","SC","SD","TN","TX","UT","VT","VA","VI","WA","WV","WI","WY"])
cities = ["nyc", "orlando", "atlanta"]

logging.basicConfig(filename="std.log", format='%(asctime)s %(message)s', filemode='a') 
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#https://www.facebook.com/marketplace/nyc/search/?query=ford%20transit%20high&exact=false
#https://www.facebook.com/marketplace/nyc/search/?daysSinceListed=1&query=ford%20transit%20high&exact=false
#https://m.facebook.com/marketplace/nyc/?query=Ford%20transit%202015&radius_in_km=500
@dataclass
class Scraper:
    search_item:str=""
    city:str="nyc"
    date_listed:int=1
    override_url:str=None
    browser_type:str=None

    _get_url:str=None
    _selenium_retries:int = 0 
    _chrome_options:Options=None
    _browser:WebDriver=None

    def __post_init__(self):
        if self.override_url:
            url = self.override_url
        else:
            base_url = "https://facebook.com/marketplace/"
            city_url = self.city+"/search/?"
            days_listed_url = "daysSinceListed={}&".format(self.date_listed) if (self.date_listed != None) else ""
            query_url = "query="+"%20".join(self.search_item.split(" "))
            url = base_url+city_url+days_listed_url+query_url
        self._get_url=url
        logger.info(self._get_url) 
        print(self._get_url)

        self.user_agent_rotator = UserAgent(
            software_names=[SoftwareName.CHROME.value], 
            operating_systems=[OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value], 
            hardware_types=[HardwareType.COMPUTER.value], 
            limit=100)
        #Populates chrome options
        self.refresh_user_agent()
        
    #Refreshes the user-agent and creates new chrome option.  
    def refresh_user_agent(self):
        user_agent = self.user_agent_rotator.get_random_user_agent()
        self._chrome_options = Options()
        #self._chrome_options.add_argument("--headless")
        self._chrome_options.add_argument("--no-sandbox")
        self._chrome_options.add_argument("--window_size=1920,1080")
        self._chrome_options.add_argument("--disable-gpu")
        self._chrome_options.add_argument(f'user-agent={user_agent}')
    
    #Creates browser and runs the given url.
    def _get_return_url(self):
        self._browser = webdriver.Chrome(options=self._chrome_options)
        self._browser.get(self._get_url)
        self._browser.implicitly_wait(1)
        return self._browser.current_url

    def open_browser(self):
        def refresh_browser(url):
            return (url.startswith("https://m") and self.browser_type=="desktop") or \
                                (not url.startswith("https://m") and self.browser_type=="mobile")
        try:
            if self.browser_type and self.browser_type in ["mobile", "desktop"]:
                scrape_url = self._get_return_url()
                while(refresh_browser(scrape_url)):
                    self.refresh_user_agent()
                    self._browser.close()
                    scrape_url = self._get_return_url()
                self._get_url=scrape_url
            else:
                self._get_url=self._get_return_url()
            return True
        except Exception as e:
            self._browser.close()
            raise e
    
    def scrape_listings(self):
        self._scrape_web_contents()
        self._browser.close()
        #if self._get_url.startswith("https://m"):
        #    return self._scrape_mobile_contents()
        #else:
        #    return self._scrape_web_contents()

    def _scrape_mobile_contents(self):
        pass


    def _scrape_web_contents(self)->List[Listing]:
        web_element_list = self._browser.find_elements_by_xpath("//a[contains(@href,'/marketplace/item')]")
        return_listings=[]
        search_str_set=set(self.search_item.split(" "))
        for web_element in web_element_list:
            try:
                print("-------")
                print(web_element)
                print("Web element text:\n"+web_element.text)
                web_element_text = web_element.text
                #extract the url
                url = web_element.get_attribute("href")
                image_url = web_element.find_element(By.XPATH, ".//img").get_attribute("src")
                print("url:"+url)
                print("image_url:"+image_url)

                name, price, location, additional_info = None, None, None, None
                for line in web_element_text.split("\n"):
                    if "$" in line: price=line
                    elif search_str_set&set(line.split(" ")): name=line
                    elif len(line.split(","))>=2 and line.split(",")[1].strip() in states: 
                        location=line
                    else: additional_info=line
                print("name:"+str(name))
                print("price:"+str(price))
                print("location:"+str(location))
                print("additional_info:"+str(additional_info))

                return_listings.append(Listing(price=price, name=name, location=location, url=url, image_url=image_url, additional_info=additional_info))
            except StaleElementReferenceException as e:
                print("Error getting info for element "+web_element.id)

        return return_listings

if __name__ == "__main__":
    req = Scraper(search_item="Ford transit 2015", city="nyc", date_listed=2, browser_type="desktop")
    # req = Scraper(search_item="Ford transit 2015", city="nyc", date_listed=2)
    #req = Request(override_url="https://www.facebook.com/marketplace/nyc/search/?query=ford%20transit%20high&exact=false")
    #req = Request(override_url="https://amazon.com")
    #req = Request('http://lumtest.com/myip.json')

    req.open_browser()
    req.scrape_listings()


#Finding login and password field to enter 
'''
    def fill_user_pass_fields(self):
        try:
            em = _browser.find_element_by_id("m_login_email")        
            pas = _browser.find_element_by_id("m_login_password")
        except NoSuchElementException as e:
            em = _browser.find_element_by_id("email")
            pas = _browser.find_element_by_id("pass")            
        login_button = _browser.find_element_by_xpath('//button[@name="login"]')

        em.send_keys(os.environ.get("FB_USERNAME"))
        pas.send_keys(os.environ.get("FB_PASS"))
        #_browser.find_element_by_css_selector("#pass").send_keys("insert password here")
        #_browser.find_element_by_css_selector("#u_0_q").click()
        login_button.click()
'''
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
#browser = webdriver.Chrome(options=_chrome_options, desired_capabilities=capabilities)