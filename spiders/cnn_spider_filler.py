# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import time
import pymongo

class Cnn_spiderSpider(scrapy.Spider):
    name = "cnn"
    allowed_domains = ['www.cnn.com']
    start_urls = ['https://www.cnn.com']

    def __init__(self, **kwargs):

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(executable_path=str('./chromedriver'), options=chrome_options)

        self.mongo_client = pymongo.MongoClient(host=['172.17.0.2'], serverSelectionTimeoutMS = 3000)
        self.database = self.mongo_client["links"]
        self.col_db = self.database["links"]

    # using scrapy's native parse to first scrape links on result pages
    def parse(self, response):
        self.driver.get("https://www.cnn.com")
        time.sleep(1)
        search_input = self.driver.find_element_by_id("footer-search-bar")
        search_input.send_keys("*")
        search_btn = self.driver.find_element_by_xpath("(//button[contains(@class, 'Flex-sc-1')])[2]")
        search_btn.click()

        i = 0
        while i < 1:
            i += 1
            time.sleep(5)
            try:
                next_btn = self.driver.find_element_by_xpath("(//div[contains(@class, 'pagination-arrow')])[2]")
                next_btn.click()
                resp = Selector(text=self.driver.page_source)
                results = resp.xpath("//div[@class='cnn-search__result cnn-search__result--article']/div/h3/a")
                for result in results:
                    title = result.xpath(".//text()").get()
                    link = result.xpath(".//@href").get()[13:]
                    full_url = result.xpath(".//@href").get()
                    new_entry = {"url":full_url}
                    self.col_db.insert_one(new_entry)
            except:
                continue
        time.sleep(15)
        print("sleeping")
        yield response.follow(url=self.start_urls[0], callback=self.parse, dont_filter=True)
