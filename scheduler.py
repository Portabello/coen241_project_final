from pymongo import MongoClient
import pika
from urllib.parse import urlparse

class scheduler:
    def __init__(self, mongoURL, rabbitURL):
        self.client = MongoClient(host=[mongoURL], serverSelectionTimeoutMS = 3000)
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitURL))
        self.channel = connection.channel()
        self.domains = set(["www.cnn.com"])
        for domain in self.domains:
            self.channel.queue_declare(queue=domain)
    def scan(self):
        cursors = self.client.db.link.find()
        for cursor in cursors:
            if self.client.db.visited.find({'key': cursor.link}):
                self.client.db.link.delete(cursor)
                continue
            domain = urlparse(cursor.link).netloc
            if domain not in self.domains:
                continue
            self.channel.basic_publish(exchange='', routing_key=domain, body = cursor.link)
            print(cursor.link, "added to mq")
            self.client.db.link.delete(cursor)

    def __del__(self):
        self.connection.close()


if __name__ == "__main__":
    s = scheduler("172.17.0.2", "172.17.0.3")
    while(True):
        s.scan()
        sleep(20)
