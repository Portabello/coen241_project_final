# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import time

class Huffpost_spiderSpider(scrapy.Spider):
    name = "huffpost"
    allowed_domains = ['www.huffpost.com']
    start_urls = ['https://www.huffpost.com']
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"

    # initiating selenium
    def __init__(self):

        # set up the driver
        chrome_options = Options()
        path_to_extension = r'C:\Users\Jasmit\Desktop\SCU MASTERS MAIN\Spring 2021\COEN 242 Big Data\final_project\final\final\1.35.2_30'

        chrome_options.add_argument('load-extension=' + path_to_extension)
        driver = webdriver.Chrome(executable_path=str('./chromedriver'), options=chrome_options)
        driver.get("https://www.huffpost.com")

        # begin search
        search_input = driver.find_element_by_id("hamburger") # find the search bar
        search_input.click()
        search_btn = driver.find_element_by_xpath("/html/body/div/div[1]/div/div/div[2]/div[2]/a[1]")
        search_btn.click()


        # record the first page
        self.html = [driver.page_source]

        # start turning pages
        i = 0
        while i < 50: # 100 is just right to get us back to July
            i += 1
            time.sleep(5) # just in case the next button hasn't finished loading
            next_btn = driver.find_element_by_xpath("//a[@class='pagination__next-link']")
            next_btn.click()

            self.html.append(driver.page_source) # not the best way but will do

    # using scrapy's native parse to first scrape links on result pages
    def parse(self, response):
        for page in self.html:
            resp = Selector(text=page)
            results = resp.xpath("//div[@class='card__headlines']/a")

            for result in results:
                title = result.xpath(".//text()").get()

                link = result.xpath(".//@href").get() # cut off the domain; had better just use request in fact
                yield response.follow(url=link, callback=self.parse_article, meta={"title": title})

    def parse_time(self, unparsed_time):
        if unparsed_time == None or len(unparsed_time) == 0:
            return "05/2021"
        year = unparsed_time[6:10]
        month = unparsed_time[0:2]
        return month+"/"+year

    # pass on the links to open and process actual news articles
    def parse_article(self, response):
        title = response.request.meta['title']
        time = response.xpath("//div[@class='timestamp']/span/span//text()").get()
        parsed_time = self.parse_time(time)
        yield {
            "title": title,
            "time": parsed_time
    }
