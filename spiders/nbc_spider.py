# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import time

class Nbc_spiderSpider(scrapy.Spider):
    name = "nbc"
    allowed_domains = ['www.nbcnews.com']
    start_urls = ['https://www.nbcnews.com']
    user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"

    # initiating selenium
    def __init__(self):

        chrome_options = Options()
        path_to_extension = r'C:\Users\Jasmit\Desktop\SCU MASTERS MAIN\Spring 2021\COEN 242 Big Data\final_project\final\final\1.35.2_30'
        chrome_options.add_argument('load-extension=' + path_to_extension)
        driver = webdriver.Chrome(executable_path=str('./chromedriver'), options=chrome_options)
        driver.get("https://www.nbcnews.com")
        search_input = driver.find_element_by_xpath("//button[@class='hamburger js-menu-toggle']") # find the search bar
        search_input.click()
        search_btn = driver.find_element_by_xpath("//input[@class='search-input js-search-input']")
        search_btn.send_keys("news")
        search_btn.submit()

        self.html = [driver.page_source]

        i = 0
        while i < 9:
            i += 1
            time.sleep(5)
            next_btn = driver.find_element_by_xpath("//div[@class='gsc-cursor']/div[@aria-label='Page "+str(i+1)+"']")
            next_btn.click()
            time.sleep(5)
            self.html.append(driver.page_source)

    # using scrapy's native parse to first scrape links on result pages
    def parse(self, response):

        for page in self.html:
            resp = Selector(text=page)
            results = resp.xpath("//a[@class='gs-title']")


            for result in results:
                title = result.xpath(".//text()").get()
                if (title == None):
                    break

                link = result.xpath(".//@href").get() # cut off the domain; had better just use request in fact
                if (link == None):
                    break
                yield response.follow(url=link, callback=self.parse_article, meta={"title": title})

    def parse_time(self, unparsed_time):
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

    # pass on the links to open and process actual news articles
    def parse_article(self, response):
        title = response.xpath("//h1//text()").get()
        time = response.xpath("//time[@class='relative z-1']//text()").get()
        parsed_time = self.parse_time(time)

        yield {
            "title": title,
            "time": parsed_time

    }
