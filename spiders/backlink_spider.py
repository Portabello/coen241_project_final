# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import time
import pymongo
import sys
import pika
from time import sleep

class Backlink_spiderSpider(scrapy.Spider):
    name = "cnn"
    allowed_domains = ['www.cnn.com']
    #start_urls = ['https://www.cnn.com']

    def __init__(self, **kwargs):

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path=str('./chromedriver'), options=chrome_options)
    
        rabbitURL = "172.17.0.3"
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitURL))
        channel = connection.channel()
        channel.queue_declare(queue="www.cnn.com")


        method_frame, header_frame, body = channel.basic_get(queue = "www.cnn.com", auto_ack=True)
        # print("##############################")
        print(body)
        # print("################################")
        body_decode = body.decode("utf-8")
        #connection.close()

        driver.get(body_decode)
        self.html = [driver.page_source]



    # using scrapy's native parse to first scrape links on result pages
    def parse(self, response):
        for page in self.html:
            resp = Selector(text=page)
            title = resp.xpath(".//text()").get()
            link = resp.xpath(".//@href").get()[13:]
            full_url = resp.xpath(".//@href").get()
            yield response.follow(url=link, callback=self.parse_article, meta={"url": full_url, "title": title})
            rabbitURL = "172.17.0.3"
            connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitURL))
            channel = connection.channel()
            channel.queue_declare(queue="www.cnn.com")
            method_frame, header_frame, body = channel.basic_get(queue = "www.cnn.com", auto_ack=True)
            body_decode = body.decode("utf-8")
            yield response.follow(url=body_decode, callback=self.parse)

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
        new_entry = {"url": url, "title": title, "time": time}
        x = col_db.insert_one(new_entry)

        backlinks_databse = mongo_client["links"]
        backinks_col = backlinks_database["links"]
        for links in backlinks:
            if "https://www.cnn" in links:
                new_entry = {"link": links}
                x = backlinks_col.insert_one(new_entry)
