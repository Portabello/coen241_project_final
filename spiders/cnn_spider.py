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
        driver = webdriver.Chrome(executable_path=str('./chromedriver'), options=chrome_options)
        driver.get("https://www.cnn.com")
        search_input = driver.find_element_by_id("footer-search-bar")
        search_input.send_keys("*")
        search_btn = driver.find_element_by_xpath("(//button[contains(@class, 'Flex-sc-1')])[2]")
        search_btn.click()
        self.html = [driver.page_source]

        i = 0
        while i < 10:
            i += 1
            time.sleep(5)
            next_btn = driver.find_element_by_xpath("(//div[contains(@class, 'pagination-arrow')])[2]")
            next_btn.click()
            self.html.append(driver.page_source)

    # using scrapy's native parse to first scrape links on result pages
    def parse(self, response):
        for page in self.html:
            resp = Selector(text=page)
            results = resp.xpath("//div[@class='cnn-search__result cnn-search__result--article']/div/h3/a")
            for result in results:
                title = result.xpath(".//text()").get()
                link = result.xpath(".//@href").get()[13:]
                full_url = result.xpath(".//@href").get()
                yield response.follow(url=link, callback=self.parse_article, meta={"url": full_url, "title": title})


    def parse_time(self, unparsed_time):
        try:
            months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            years = ["2021", "2020", "2019", "2018", "2017"]
            parsed_time = ""
            for count, month in enumerate(months):
                if month in unparsed_time:
                    if (count+1) > 9:
                        parsed_time += str(count+1)+"/"
                        break
                    else:
                        parsed_time += "0"+str(count+1)+"/"
                        break
            for year in years:
                if year in unparsed_time:
                    parsed_time += year
                    break
            if len(parsed_time) == 0:
                parsed_time += "5/2021"
            return parsed_time
        except:
            return "NAN"

    def parse_title(self, unparsed_title):
        punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        for c in unparsed_title:
            if c in punc:
                unparsed_title = unparsed_title.replace(c, "")
        return unparsed_title.lower()
    # pass on the links to open and process actual news articles
    def parse_article(self, response):
        title = response.request.meta['title']
        url = response.request.meta['url']
        backlinks = response.xpath(".//a[@class='specified_string']/@href").get()
        time = response.xpath("//p[@class='update-time']/text()").get()
        parsed_time = self.parse_time(time)

        mongo_client = pymongo.MongoClient(host=['172.17.0.2'], serverSelectionTimeoutMS = 3000)
        database = mongo_client["headlines"]
        col_db = database["info"]
        new_entry = {"url": , "title": , "time": }
        x = col_db.insert_one(new_entry)

        yield {
            "url": url,
            "backlinks": backlinks,
            "title": self.parse_title(title),
            "time": parsed_time
    }
