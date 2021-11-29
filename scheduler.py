from pymongo import MongoClient
import pika
import time
from urllib.parse import urlparse

class scheduler:
    def __init__(self, mongoURL, rabbitURL):
        self.client = MongoClient(host=[mongoURL], serverSelectionTimeoutMS = 3000)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitURL))
        self.channel = self.connection.channel()
        self.domains = set(["www.cnn.com"])
        for domain in self.domains:
            self.channel.queue_declare(queue=domain)
    def scan(self):
        cursors = self.client.links.links.find()
        for cursor in cursors:
            link = cursor["link"]
            print(link)
            if self.client.links.visited.find_one({'_id': link}):
                print("already visited")
                self.client.links.links.delete_one(cursor)
                continue
            self.client.links.visited.insert_one({'_id': link})
            domain = urlparse(link).netloc
            if domain not in self.domains:
                print("not in domain")
                self.client.links.links.delete_one(cursor)
                continue
            self.channel.basic_publish(exchange='', routing_key=domain, body = link)
            print("added to mq")
            self.client.links.links.delete_one(cursor)

    def __del__(self):
        self.connection.close()


if __name__ == "__main__":
    s = scheduler("172.17.0.2", "172.17.0.3")
    while(True):
        s.scan()
        sleep(20)
