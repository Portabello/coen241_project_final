import scrapy
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


class Fox_spiderSpider(scrapy.Spider):
    name = 'fox'
    allowed_domains = ['www.foxnews.com']
    start_urls = ['https://www.foxnews.com']
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"



    def __init__(self):
        chrome_options = Options()
        path_to_extension = r'C:\Users\Jasmit\Desktop\SCU MASTERS MAIN\Spring 2021\COEN 242 Big Data\final_project\final\final\1.35.2_30'
        chrome_options.add_argument('load-extension=' + path_to_extension)
        driver = webdriver.Chrome(executable_path=str('./chromedriver'), options=chrome_options)
        driver.get("https://www.foxnews.com/category/world")

        wait = WebDriverWait(driver, 10)

        i = 0
        while i < 50:
            try:
                time.sleep(1)
                element = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, "(//div[@class='button load-more js-load-more'])[1]/a")))
                element.click()
                i += 1
            except TimeoutException:
                break

        self.html = driver.page_source


    def parse(self, response):
        resp = Selector(text=self.html)
        results = resp.xpath("//article[@class='article']//h4[@class='title']/a")
        for result in results:
            title = result.xpath(".//text()").get()
            eyebrow = result.xpath(".//span[@class='eyebrow']/a/text()").get() # scraped only for filtering
            link = result.xpath(".//@href").get()
            if eyebrow == 'VIDEO':
                continue # filter out videos
            else:
                yield response.follow(url=link, callback=self.parse_article, meta={"title": title})

    def parse_time(self, unparsed_time):
        if unparsed_time == None or len(unparsed_time) == 0:
            return "05/2021"
        year = unparsed_time[0:4]
        month = unparsed_time[5:7]
        return month+"/"+year


    def parse_article(self, response):
        title = response.request.meta['title']
        time = response.xpath("//meta[@name='dcterms.modified']/@content").get()
        parsed_time = self.parse_time(time)
        yield {
            "title": title,
            "time": parsed_time
        }
